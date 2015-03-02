from timesheet import TimesheetArchive, Timesheet, Entry
import click
from click import echo
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///timesheet.db', echo=True)
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


def add_new_sheet():
    archive = session.query(TimesheetArchive).filter(TimesheetArchive.name=='archive').first()
    if not archive:
        archive = TimesheetArchive()
        session.add(archive)
    archive.timesheets.append(Timesheet())
    session.commit()


def list_all_sheets():
    res = session.query(Timesheet).all()
    if res:
        for sheet in res:
            print '+---------------------------------------------------------------+'
            print '|\t' + str(sheet.id) + '\t|\t' +  sheet.name + \
            '\t|\t' + sheet.created_date.strftime('%m/%d/%y') + '\t|'
            print '+---------------------------------------------------------------+'
    else:
        print 'You havent created any timesheet.'


def check_in(sheet_id, checkin_time):
    sheet = session.query(Timesheet).get(sheet_id)
    if sheet:
        entry = Entry(checkin_time=checkin_time)






    # date = datetime.now().strftime("%m/%d/%y")
    #
    # checkin_time = datetime.now().strftime("%H:%M:%S")
    # time.sleep(3)
    # checkout_time = datetime.now().strftime("%H:%M:%S")
    #
    # time_in = datetime.strptime(checkin_time, "%H:%M:%S")
    # time_out = datetime.strptime(checkout_time, "%H:%M:%S")
    # working_time = time_out - time_in
