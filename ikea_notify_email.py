#!/usr/bin/env python3

import argparse
import json
import logging
import requests
import smtplib

# Who the email will come from (yourself, most likely)
SENDER = 'your_email@domain.com'

# Who you want the email to go to (again, yourself most likely)
RECIPIENT = 'your_email@domain.com'

# The email server you want to use (Gmail is listed below)
SMTP_SERVER = 'smtp.gmail.com:587'

# If using Gmail, it's your full email address (you@gmail.com)
SMTP_USER = 'your_username'

# If using Gmail, you need to create an app password at https://myaccount.google.com/apppasswords
SMTP_PASSWORD = 'your_password'

IKEA_URL = 'https://ikea-status.dong.st/latest.json'


def send_notification(store):
    fromaddr = SENDER
    toaddrs = RECIPIENT
    server = smtplib.SMTP(SMTP_SERVER)
    server.ehlo()
    server.starttls()
    msg = "\r\n".join([
        "From: {}".format(SENDER),
        "To: {}".format(RECIPIENT),
        "Subject: IKEA Ordering Is Open!!",
        "",
        "It looks like the {} store is open for ordering".format(store)
    ])
    server.login(SMTP_USER, SMTP_PASSWORD)
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


logging.basicConfig(filename='/tmp/ikea.log',
                    format='%(asctime)s %(message)s',
                    level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument('-t','--test', action='store_true')
args = parser.parse_args()

if args.test:
    send_notification('Dummy Store')
    exit(0)
logging.info('Checking IKEA data')
r = requests.get(IKEA_URL)
if r.ok:
    data = json.loads(r.content)
    for i in data:
        store_name = i['name']
        if ('East Palo Alto' in store_name) or ('Emeryville' in store_name):
            store_name = i['name']
            current_status = i['lastStatus']
            if current_status == 'open':
                logging.info('{} seems to be open. Sending notification.'.format(store_name))
                send_notification(store_name)
            else:
                logging.info('{} is not open.'.format(store_name))
else:
    logging.error('There was a problem connecting to IKEA')
    exit(1)

