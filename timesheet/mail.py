import smtplib
from smtplib import SMTPException, SMTPAuthenticationError,\
    SMTPSenderRefused, SMTPRecipientsRefused
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
from .models import User
from timesheet import session
import os
import getpass
import click


def sendmail(to, subject, text, attach):

    user = session.query(User).first()
    if user is None:
        email = click.prompt('Please enter your email address', type=str)
        pwd = getpass.getpass('Password:')
        user = User(email=email, password=pwd)
        session.add(user)
        session.commit()


    msg = MIMEMultipart()
    msg['From'] = user.email
    msg['To'] = to
    msg['Subject'] = subject

    msg.attach(MIMEText(text))

    part = MIMEBase('application', 'octet-stream')
    if attach is not None:
        try:
            with open(attach, 'rb') as fh:
                data = fh.read()
            part.set_payload(data)
            Encoders.encode_base64(part)
            part.add_header('Content-Disposition',
                    'attachment; filename="%s"' % os.path.basename(attach))
            msg.attach(part)
        except IOError:
            click.echo(click.style('Error opening attachment file %s' % attach,
                fg='red'))
    try:
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(user.email, user.password)
        mailServer.sendmail(user.email, to, msg.as_string())
        click.echo(click.style('email sent!', fg='yellow'))
    except SMTPException:
        click.echo(click.style('Failed sending the email.', fg='red'))

    mailServer.close()

