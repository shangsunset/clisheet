from timesheet import TimesheetArchive, Timesheet, Entry
import click
from click import echo
from datetime import datetime, timedelta, date
from sqlalchemy import create_engine
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



#TODO
@cli.command()
@click.argument('id', type=int, required=False)
def sheet(id):
    """Display a timesheet.Take timesheet id as parameter.'"""
    # sheets_count = session.query(Timesheet).count()
    if id:
        sheet = session.query(Timesheet).get(id)
        print '+---------------------------------------------------------------------------------------+'
        print
        print '|\tName : ' + sheet.name + '\t|\tCreated Date : ' +\
                sheet.created_date.strftime('%m/%d/%y') + ' \t|\tTotal Hour: ' +\
                str(sheet.total_hours) + '\t|'
        print
        print '+---------------------------------------------------------------------------------------+'
        entries = session.query(Entry).filter(Entry.timesheet_id==sheet.id)
        print '|\tDate\t|\tCheck In Time\t|\tCheck Out Time\t|\tHours|'
        for entry in entries:
            print '|\t' + entry.date.strftime('%m/%d/%y') + '\t|\t' +\
                    entry.checkin_time.strftime('%H:%M:%S') + \
            '\t|\t' + entry.checkout_time.strftime('%H:%M:%S') + '\t|\t' +\
            str(entry.hours) + '\t|'
    else:
        latest = session.query(Timesheet).order_by(Timesheet.id.desc()).first()

        print '+---------------------------------------------------------------------------------------+'
        print
        print '|\tName : ' + latest.name + '\t|\tCreated Date : ' +\
                latest.created_date.strftime('%m/%d/%y') + ' \t|\tTotal Hour: ' +\
                str(latest.total_hours) + '\t|'
        print
        print '+---------------------------------------------------------------------------------------+'
        entries = session.query(Entry).filter(Entry.timesheet_id==latest.id)
        print '|\tDate\t|\tCheck In Time\t|\tCheck Out Time\t|\tHours|'
        for entry in entries:
            print '|\t' + entry.date.strftime('%m/%d/%y') + '\t|\t' +\
                    entry.checkin_time.strftime('%H:%M:%S') + \
            '\t|\t' + entry.checkout_time.strftime('%H:%M:%S') + '\t|\t' +\
            str(entry.hours) + '\t|'




    # print 'The sheet you are looking for doesnt exist'




@cli.command()
def new():
    """Add a new timesheet."""

    #filter: sheet created less than a day to current time.
    res = session.query(Timesheet).filter(Timesheet.created_date==date.today())

    if res:
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
        print '+---------------------------------------------------------------+'
        print '|\tID\t|\tSheet Name\t|\tCreated Date\t|'
        for sheet in res:
            print '+---------------------------------------------------------------+'
            print '|\t' + str(sheet.id) + '\t|\t' +  sheet.name + \
            '\t|\t' + sheet.created_date.strftime('%m/%d/%y') + '\t|'
        print '+---------------------------------------------------------------+'
    else:
        print 'You havent created any timesheet.'


@cli.command()
def cin(current_time=datetime.now()):
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

        #update when there is check in and check out
        elif entry and entry.checkout_time:
            entry.checkin_time = current_time

        #create an entry if havned checked in
        else:
            res.entries.append(Entry(checkin_time=current_time))
    else:
        sheet = Timesheet()
        archive.timesheets.append(sheet)
        sheet.entries.append(Entry(checkin_time=current_time))

    session.commit()


@cli.command()
def cout(current_time=datetime.now()):
    """Checking out"""
    entry = session.query(Entry).filter(Entry.date == date.today())\
            .order_by(Entry.id.desc()).first()

    if entry:
        entry.checkout_time = current_time
        entry.hours = ((entry.checkout_time - entry.checkin_time).seconds)/(60*60)

    else:
        print 'You havent checked in yet son!'

    session.commit()



    # date = datetime.now().strftime("%m/%d/%y")
    #
    # checkin_time = datetime.now().strftime("%H:%M:%S")
    # time.sleep(3)
    # checkout_time = datetime.now().strftime("%H:%M:%S")
    #
    # time_in = datetime.strptime(checkin_time, "%H:%M:%S")
    # time_out = datetime.strptime(checkout_time, "%H:%M:%S")
    # working_time = time_out - time_in

