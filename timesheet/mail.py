import smtplib
from smtplib import SMTPException, SMTPAuthenticationError,\
    SMTPSenderRefused, SMTPRecipientsRefused
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders
import os
from config import gmail_user, gmail_pwd


def sendmail(to, subject, text, attach=None):
    msg = MIMEMultipart()

    msg['From'] = gmail_user
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
            print 'Error opening attachment file %s' % attach

    try:
        mailServer = smtplib.SMTP("smtp.gmail.com", 587)
        mailServer.ehlo()
        mailServer.starttls()
        mailServer.ehlo()
        mailServer.login(gmail_user, gmail_pwd)
        mailServer.sendmail(gmail_user, to, msg.as_string())
    except SMTPAuthenticationError:
        print 'Login authentication failed.'
    except SMTPException:
        print 'Failed sending the email.'

    mailServer.close()

# sendmail("shangsunset@gmail.com",
#         "hello",
#         "its working")
