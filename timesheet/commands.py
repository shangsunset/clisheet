from __future__ import division
import sys
from .models import TimesheetArchive, Timesheet, Entry
import click
from datetime import datetime, timedelta, date, time
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///timesheet.db')
# create a Session
Session = sessionmaker(bind=engine)
session = Session()

archive = session.query(TimesheetArchive).filter(TimesheetArchive.name=='archive').first()
if not archive:
    archive = TimesheetArchive()
    session.add(archive)


def create_new_sheet():

    #filter: sheet created less than a day to current time.
    if session.query(Timesheet).filter(Timesheet.created_date==date.today()).count():
        print 'You just created a timesheet today...'
    else:
        new = Timesheet()
        archive.timesheets.append(new)
        session.commit()


def show_sheet(id):

    if id:
        sheet = session.query(Timesheet).get(id)
    else:
        #lastest sheet
        sheet = session.query(Timesheet).order_by(Timesheet.id.desc()).first()

    if sheet is not None:
        click.echo(click.style('-'*120, fg='green'))
        print
        click.echo(click.style('Name: {:<20} Created Date: {:<20} Total Hours: {:<20}'.format(
                sheet.name, sheet.created_date.strftime('%m/%d/%y'),
                str(sheet.total_hours)), fg='blue'))
        print
        click.echo(click.style('-'*120, fg='green'))
        entries = session.query(Entry).filter(Entry.timesheet_id==sheet.id)
        print '{:<10} {:<15} {:<20} {:<20} {:<15} {:<20}'.format(
                'ID', 'Date', 'Check In Time', 'Check Out Time', 'Hours', 'Task')
        print

        for entry in entries:
            if entry.checkout_time is None:
                print '{:<10} {:<15} {:<20} {:<20} {:<15} {:<10}\n'.format(
                                str(entry.id), entry.date.strftime('%m/%d/%y'),
                                entry.checkin_time.strftime('%H:%M:%S'),
                                '--:--:--', entry.hours, '')
            else:
                print '{:<10} {:<15} {:<20} {:<20} {:<15} {:<10}\n'.format(
                                str(entry.id), entry.date.strftime('%m/%d/%y'),
                                entry.checkin_time.strftime('%H:%M:%S'),
                                entry.checkout_time.strftime('%H:%M:%S'),
                                entry.hours, entry.task)

    else:
        print 'The sheet you are looking for doesnt exist'


def list_sheets():
    res = session.query(Timesheet).all()
    if res:
        print '+' + '-'*87 + '+'
        print '|\tID\t|\tSheet Name\t|\tCreated Date\t|\tTotal Hours\t|'
        for sheet in res:
            print '+' + '-'*87 + '+'
            print '|\t' + str(sheet.id) + '\t|\t' +  sheet.name + \
            '\t\t|\t' + sheet.created_date.strftime('%m/%d/%y') + '\t|\t' +\
            str(sheet.total_hours) + '\t\t|'

        print '+' + '-'*87 + '+'
    else:
        print 'You havent created any timesheet.'


def check_in(current_time=datetime.now()):

    res = session.query(Timesheet).order_by(Timesheet.id.desc()).first()
    if res is not None:
        entry = session.query(Entry).filter(
                Entry.date == date.today())\
                .order_by(Entry.id.desc()).first()

        #if checked in but havent checked out
        if entry and not entry.checkout_time:
            print 'You havent checked out from the last session. ' \
                    'I think this is a repeated action'

        #create a new entry when there is already check in and check out made
        elif entry and entry.checkout_time:
            res.entries.append(Entry(checkin_time=current_time))

        #create an entry if havned checked in
        else:
            res.entries.append(Entry(checkin_time=current_time))
    else:
        sheet = Timesheet()
        archive.timesheets.append(sheet)
        sheet.entries.append(Entry(checkin_time=current_time))

    session.commit()


def check_out(task, current_time=datetime.now()):

    res = session.query(Timesheet).order_by(Timesheet.id.desc()).first()

    if res is not None:
        entry = session.query(Entry).filter(Entry.date == date.today())\
                .order_by(Entry.id.desc()).first()

        if entry:
            entry.checkout_time = current_time
            duration = (entry.checkout_time - entry.checkin_time).seconds/(60*60)
            entry.hours = round(duration, 1)
            update_total_hours(res)
            if task:
                entry.task = task

        else:
            print 'You havent checked in yet son!'

    else:
        print 'You havent created any timesheet.'
    session.commit()


def delete(sheet_id, entry_id):
    if sheet_id is not None:
        res = session.query(Timesheet).get(sheet_id)

    elif entry_id is not None:
        res = session.query(Entry).get(entry_id)

    else:
        print 'You didnt provide any option. usage: ts rm {-s} {-e} {id}'
        sys.exit(0)

    if not res:
        click.echo('The ' + ('entry' if entry_id else 'timesheet') +\
            ' you want to delete does not exist. Maybe you entered a wrong id number.')
    else:
        session.delete(res)
    session.commit()


def update_total_hours(sheet):
    entries = session.query(Entry).filter(Entry.timesheet_id==sheet.id)
    for entry in entries:
        sheet.total_hours += entry.hours


@event.listens_for(Timesheet, 'init')
def update_name(target, args, kwargs):
    session.add(target)
    session.commit()
    target.name = 'sheet#' + str(target.id)