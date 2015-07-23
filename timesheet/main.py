import click
from .mail import sendmail
from .utils import create_new_sheet, show_sheet,\
        list_sheets, delete, check_in, check_out,\
        generate_attachment_txt, generate_attachment_excel



@click.group()
def cli():
    pass


@cli.command()
@click.argument('id', type=int, required=False)
def show(id):
    """Display a timesheet.Take timesheet id as parameter.If no parameter
    is provided,latest timesheet will be shown by default"""
    show_sheet(id)


@cli.command()
def new():
    """Add a new timesheet."""
    create_new_sheet()


@cli.command()
def ls():
    """List all the timesheets."""
    list_sheets()


@cli.command()
def checkin():
    """Checking in"""
    check_in()


@cli.command()
@click.option('--message', '-m', type=str)
def checkout(message):
    """Checking out"""

    check_out(message)


@cli.command()
@click.option('--sheet_id', '-s', type=int,
        help='removes a sheet. take sheet id as parameter')
@click.option('--entry_id', '-e', type=int,
        help='removes entry. take entry id as parameter')
def rm(sheet_id, entry_id):
    """remove sheet or entry of your choice"""
    delete(sheet_id, entry_id)


@cli.command()
@click.option('--to', prompt='To')
@click.option('--subject', prompt='Subect')
@click.option('--message', prompt='Message')
@click.option('--id', prompt='Attachment ID')
def email(to, subject, message, id):
    attachment = generate_attachment_excel(int(id))
    sendmail(to, subject, message, attachment)

