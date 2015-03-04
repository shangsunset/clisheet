from timesheet import TimesheetArchive, Timesheet, Entry
import click
from click import echo
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///timesheet.db')
# create a Session
Session = sessionmaker(bind=engine)
session = Session()


@click.command()
@click.argument('arg', required=False)
def main(arg):

    if arg == 'new':
        add_new_sheet()
    if arg == 'ls':
        list_all_sheets()
    if arg == 'in':
        check_in()


def add_new_sheet():
    archive = session.query(TimesheetArchive).filter(TimesheetArchive.name=='archive').first()
    sheets = session.query(Timesheet).all()
    if not archive:
        archive = TimesheetArchive()
        session.add(archive)

    res = session.query(Timesheet).filter(Timesheet.created_date==datetime.now().strftime('%m/%d/%y')).count()
    if res > 0:
        print 'yes'
    # count = 0
    # for sheet in sheets:
    #     if sheet.created_date.now().strftime('%m/%d/%y') == datetime.now().strftime('%m/%d/%y'):
    #         count += 1
    #
    # if count > 0:
    #     print 'Sigh...You already created a timesheet today...'
    # else:
    #     archive.timesheets.append(Timesheet())
    #     session.commit()


def list_all_sheets():
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



def check_in(current_time=datetime.now()):
    sheets = session.query(Timesheet).all()
    count = 0
    for sheet in sheets:
        if sheet.created_date.now().strftime('%m/%d/%y') == datetime.now().strftime('%m/%d/%y'):
            sheet.entries.append(Entry(checkin_time=current_time))
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
