from timesheet import TimesheetArchive
import click
from click import echo
from datetime import datetime

@click.command()
@click.argument('arg', required=False)
def main(arg):

    if arg == 'new':
        archive = TimesheetArchive()
        click.echo(archive.created_date)

    # if arg == 'ls':
        # for ts in ts_list:
        #     click.echo(ts.created_date)

    # date = datetime.now().strftime("%m/%d/%y")
    #
    # checkin_time = datetime.now().strftime("%H:%M:%S")
    # time.sleep(3)
    # checkout_time = datetime.now().strftime("%H:%M:%S")
    #
    # time_in = datetime.strptime(checkin_time, "%H:%M:%S")
    # time_out = datetime.strptime(checkout_time, "%H:%M:%S")
    # working_time = time_out - time_in
