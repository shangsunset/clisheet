from __future__ import division
import sys
import click
from .models import TimesheetArchive, Timesheet, Entry
from datetime import datetime, timedelta, date, time
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from timesheet import session


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


def generate_attachment(id):
    if id is not None:
        sheet = session.query(Timesheet).get(id)

        if sheet is not None:
            entries = session.query(Entry).filter(Entry.timesheet_id==sheet.id)

            attachment = 'timesheet.txt'
            with open(attachment, 'w') as f:
                f.write('Name: {:<20} Created Date: {:<20} Total Hours: {:<20}'.format(
                        sheet.name, sheet.created_date.strftime('%m/%d/%y'),
                        str(sheet.total_hours)))
                f.write('\n')
                f.write('\n')

                f.write('{:<15} {:<20} {:<20} {:<15} {:<20}'.format(
                    'Date', 'Check In Time', 'Check Out Time', 'Hours', 'Message'))
                f.write('\n')
                f.write('\n')

                for entry in entries:
                    f.write('{:<15} {:<20} {:<20} {:<15} {:<10}\n'.format(
                                    entry.date.strftime('%m/%d/%y'),
                                    entry.checkin_time.strftime('%H:%M:%S'),
                                    entry.checkout_time.strftime('%H:%M:%S'),
                                    entry.hours,
                                    (entry.task if entry.task is not None else '')))

            return attachment

        else:
            click.echo(click.style('The timesheet doesnt exist', fg='red'))

    else:
        click.echo(click.style('Timesheet ID is not specified.', fg='red'))
        #lastest sheet
        # sheet = session.query(Timesheet).order_by(Timesheet.id.desc()).first()




def show_sheet(id):

    if id is not None:
        sheet = session.query(Timesheet).get(id)
    else:
        #lastest sheet
        sheet = session.query(Timesheet).order_by(Timesheet.id.desc()).first()

    if sheet is not None:
        print
        click.echo(click.style('Name: {:<20} Created Date: {:<20} Total Hours: {:<20}'.format(
                sheet.name, sheet.created_date.strftime('%m/%d/%y'),
                str(sheet.total_hours)), fg='blue'))
        print
        entries = session.query(Entry).filter(Entry.timesheet_id==sheet.id)
        click.echo(click.style('{:<10} {:<15} {:<20} {:<20} {:<15} {:<20}'.format(
                'ID', 'Date', 'Check In Time', 'Check Out Time', 'Hours', 'Message'),
                fg='green'))
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
                                entry.hours,
                                (entry.task if entry.task is not None else ''))

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
            res.entries.append(Entry(current_time))

        #create an entry if havned checked in
        else:
            res.entries.append(Entry(current_time))
    else:
        sheet = Timesheet()
        archive.timesheets.append(sheet)
        sheet.entries.append(Entry(current_time))

    session.commit()


def check_out(task, current_time=datetime.now()):

    sheet = session.query(Timesheet).order_by(Timesheet.id.desc()).first()

    if sheet is not None:
        entry = session.query(Entry).filter(Entry.date == date.today())\
                .order_by(Entry.id.desc()).first()

        if entry is not None:
            entry.checkout_time = current_time
            entry.hours = entry.get_hour()
            sheet.total_hours += entry.hours

            if task is not None:
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
        print 'You didnt provide any option. usage: ts rm {-s} or {-e} {id}'
        sys.exit(0)

    if not res:
        click.echo('The ' + ('entry' if entry_id else 'timesheet') +\
            ' you want to delete does not exist. Maybe you entered a wrong id number.')
    else:
        session.delete(res)
    session.commit()


@event.listens_for(Timesheet, 'init')
def update_name(target, args, kwargs):
    session.add(target)
    session.commit()
    target.name = 'sheet#' + str(target.id)


