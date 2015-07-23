from __future__ import division
import os
import sys
import click
import xlsxwriter
from .models import TimesheetArchive, Timesheet, Entry
from datetime import datetime, timedelta, date, time
from sqlalchemy import event
from timesheet import session, archive


def create_new_sheet():

    #filter: sheet created less than a day to current time.
    if session.query(Timesheet).filter(Timesheet.created_date==date.today()).count():
        print 'You just created a timesheet today...'
    else:
        new = Timesheet()
        archive.timesheets.append(new)
        session.commit()


def generate_attachment_txt(id):
    if id is not None:
        sheet = session.query(Timesheet).get(id)

        if sheet is not None:
            entries = session.query(Entry).filter(Entry.timesheet_id==sheet.id)

            attachment = 'timesheet-' + str(id) + '.txt'
            with open(attachment, 'w') as f:
                f.write('Name: {:<20} Created Date: {:<20} Total Hours: {:<20}'.format(
                        sheet.name, sheet.created_date.strftime('%m/%d/%y'),
                        str(sheet.total_hours)))
                f.write('\n')
                f.write('\n')

                f.write('{:<15} {:<20} {:<20} {:<15} {:<20}'.format(
                    'Date', 'Check In Time', 'Check Out Time', 'Hour', 'Message'))
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


def generate_attachment_excel(id):
    try:
        os.makedirs('./mytimesheets')
    except OSError:
        if not os.path.isdir('./mytimesheets'):
            raise
    # Create a workbook and add a worksheet.
    attachment = 'mytimesheets/timesheet-' + str(id) + '.xlsx'
    workbook = xlsxwriter.Workbook(attachment)
    worksheet = workbook.add_worksheet()

    # Add a bold format to use to highlight cells.
    bold = workbook.add_format({'bold': 1})

    # Add an Excel date format.
    date_format = workbook.add_format({'num_format': 'mmmm d yyyy'})
    time_formate = workbook.add_format({'num_format': 'hh:mm AM/PM'})

    # Adjust the column width.
    worksheet.set_column('E:E', 30)

    # Write some data headers.
    worksheet.write('A1', 'Date', bold)
    worksheet.write('B1', 'Check In', bold)
    worksheet.write('C1', 'Check Out', bold)
    worksheet.write('D1', 'Hour', bold)
    worksheet.write('E1', 'Message', bold)
    worksheet.write('F1', 'Total Hours', bold)

    # Start from the first cell below the headers.
    row = 1
    col = 0

    if id is not None:
        sheet = session.query(Timesheet).get(id)

        if sheet is not None:
            entries = session.query(Entry).filter(Entry.timesheet_id==sheet.id)
            for entry in entries:
                worksheet.write_string(row, col, entry.date.strftime('%m/%d/%y'))
                worksheet.write_string(row, col + 1, entry.checkin_time.strftime('%H:%M:%S'))
                if entry.checkout_time is not None:
                    worksheet.write_string(row, col + 2, entry.checkout_time.strftime('%H:%M:%S'))
                worksheet.write_number  (row, col + 3, entry.hours)
                worksheet.write_string(row, col + 4, (entry.task if entry.task is not None else ''))
                row+=1

            worksheet.write_number(1, 5, sheet.total_hours)

    workbook.close()

    return attachment

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
            if entry.checkout_time is None:
                entry.checkout_time = current_time
                entry.hours = entry.get_hour()
                sheet.total_hours += entry.hours

            if task is not None:
                entry.task = task

            print sheet.total_hours
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


