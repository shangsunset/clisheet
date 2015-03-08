from timesheet import TimesheetArchive, Timesheet, Entry
import click
from click import echo
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///timesheet.db')
# create a Session
Session = sessionmaker(bind=engine)
session = Session()


@click.command()
@click.option('--sheet', '-s', multiple=True, default=1,
                help='display a timesheet. take timesheet id as parameter.')
@click.argument('arg', required=False)
def main(arg, sheet):

    archive = session.query(TimesheetArchive).filter(TimesheetArchive.name=='archive').first()
    if not archive:
        archive = TimesheetArchive()
        session.add(archive)
        session.commit()

    if arg == 'new':
        add_new_sheet(archive)
    if arg == 'ls':
        list_all_sheets(archive)
    if arg == 'in':
        check_in(archive)
    if arg == 'out':
        check_out()

    show_sheet(sheet)


#TODO
def show_sheet(sheet_id):
    # sheets_count = session.query(Timesheet).count()
    sheet = session.query(Timesheet).get(sheet_id)
    if sheet:
        print 'showing %s' % sheet.name

    else:
        print 'The sheet you are looking for doesnt exist'


def add_new_sheet(archive):
    sheets = session.query(Timesheet).all()

    res = session.query(Timesheet).filter(
            datetime.now() - Timesheet.created_date < timedelta(days=1))

    if sheets:
        if res:
            print 'Sigh...You already created a timesheet today...'
        else:
            archive.timesheets.append(Timesheet())
    else:
        archive.timesheets.append(Timesheet())

    session.commit()


def list_all_sheets(archive):
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



def check_in(archive, current_time=datetime.now()):

    res = session.query(Timesheet).filter(
            datetime.now() - Timesheet.created_date < timedelta(days=1)).first()
    if res:
        entry = session.query(Entry).filter(
                datetime.now() - Entry.date < timedelta(days=1)).first()

        if entry and not entry.checkout_time:
            print 'You havent checked out from the last session. ' \
                    'I think this is a repeated action'

        elif entry and entry.checkout_time:
            entry.checkin_time = current_time

        else:
            res.entries.append(Entry(checkin_time=current_time))
    else:
        sheet = Timesheet()
        archive.timesheets.append(sheet)
        sheet.entries.append(Entry(checkin_time=current_time))

    session.commit()



def check_out(current_time=datetime.now()):
    entry = session.query(Entry).filter(
            datetime.now() - Entry.date < timedelta(days=1)).first()
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

