from __future__ import division
import math
from decimal import getcontext
from timesheet import TimesheetArchive, Timesheet, Entry
import click
from click import echo
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



@click.group()
def cli():
    pass


@cli.command()
@click.argument('id', type=int, required=False)
def show(id):
    """Display a timesheet.Take timesheet id as parameter.If no parameter
    is provided,latest timesheet will be shown by default"""

    if id:
        sheet = session.query(Timesheet).get(id)
    else:
        #lastest sheet
        sheet = session.query(Timesheet).order_by(Timesheet.id.desc()).first()

    if sheet:
        echo(click.style('This is the timesheet you requested.\n', fg='red'))
        echo(click.style('---------------------------------------------------------------------------------------', fg='green'))
        print
        echo(click.style('Name : {:<20} Created Date: {:<20} Total Hours: {:<20}'.format(
                sheet.name, sheet.created_date.strftime('%m/%d/%y'),
                str(sheet.total_hours)), fg='blue'))
        print
        echo(click.style('---------------------------------------------------------------------------------------', fg='green'))
        entries = session.query(Entry).filter(Entry.timesheet_id==sheet.id)
        print '{:<20} {:<20} {:<20} {:<20}'.format('Date', 'Check In Time', 'Check Out Time', 'Hours')
        print

        for entry in entries:
            if entry.checkout_time is None:
                print '{:<20} {:<20} {:<20} {:<20}'.format(entry.date.strftime('%m/%d/%y'),
                                                entry.checkin_time.strftime('%H:%M:%S'),
                                                '--:--:--',
                                                entry.hours)
            else:
                print '{:<20} {:<20} {:<20} {:<20}\n'.format(entry.date.strftime('%m/%d/%y'),
                                                entry.checkin_time.strftime('%H:%M:%S'),
                                                entry.checkout_time.strftime('%H:%M:%S'),
                                                entry.hours)
    else:
        print 'The sheet you are looking for doesnt exist'


@event.listens_for(Timesheet, 'init')
def update_name(target, args, kwargs):
    session.add(target)
    session.commit()
    target.name = 'sheet#' + str(target.id)


@cli.command()
def new():
    """Add a new timesheet."""

    #filter: sheet created less than a day to current time.
    if session.query(Timesheet).filter(Timesheet.created_date==date.today()).count():
        print 'You just created a timesheet today...'
    else:
        new = Timesheet()
        archive.timesheets.append(new)
        session.commit()


@cli.command()
def ls():
    """List all the timesheets."""
    res = session.query(Timesheet).all()
    if res:
        print '+---------------------------------------------------------------------------------------+'
        print '|\tID\t|\tSheet Name\t|\tCreated Date\t|\tTotal Hours\t|'
        for sheet in res:
            print '+---------------------------------------------------------------------------------------+'
            print '|\t' + str(sheet.id) + '\t|\t' +  sheet.name + \
            '\t\t|\t' + sheet.created_date.strftime('%m/%d/%y') + '\t|\t' +\
            str(sheet.total_hours) + '\t\t|'

        print '+---------------------------------------------------------------------------------------+'
    else:
        print 'You havent created any timesheet.'


@cli.command()
def checkin(current_time=datetime.now()):
    """Checking in"""

    res = session.query(Timesheet).filter(
            Timesheet.created_date==date.today())\
                    .order_by(Timesheet.id.desc()).first()
    if res:
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


@cli.command()
def checkout(current_time=datetime.now()):
    """Checking out"""

    res = session.query(Timesheet).filter(
            Timesheet.created_date==date.today())\
                    .order_by(Timesheet.id.desc()).first()

    if res:
        entry = session.query(Entry).filter(Entry.date == date.today())\
                .order_by(Entry.id.desc()).first()

        if entry:
            entry.checkout_time = current_time
            duration = (entry.checkout_time - entry.checkin_time).seconds/(60*60)
            entry.hours = round(duration, 1)
            update_total_hours(res)

        else:
            print 'You havent checked in yet son!'

    else:
        print 'You havent created any timesheet.'
    session.commit()


def update_total_hours(sheet):
    entries = session.query(Entry).filter(Entry.timesheet_id==sheet.id)
    for entry in entries:
        sheet.total_hours += entry.hours




    # date = datetime.now().strftime("%m/%d/%y")
    #
    # checkin_time = datetime.now().strftime("%H:%M:%S")
    # time.sleep(3)
    # checkout_time = datetime.now().strftime("%H:%M:%S")
    #
    # time_in = datetime.strptime(checkin_time, "%H:%M:%S")
    # time_out = datetime.strptime(checkout_time, "%H:%M:%S")
    # working_time = time_out - time_in

