#!/usr/bin/python3
import smtplib
import ssl
import traceback
import subprocess
from datetime import datetime
from email.message import EmailMessage

SERVER_TYPE = "Production"

services = ["nginx", "redis"]

send_email = False

body = "Service information for [b1tst0rm] " + \
    SERVER_TYPE + " app server\r\n\r\n"
body += "Services checked at " + str(datetime.now()) + "\r\n\r\n\r\n"

for service in services:
    body += "\r\nSERVICE: " + service + "\r\n"
    subproc = subprocess.Popen(
        "systemctl status " + service, shell=True, stdout=subprocess.PIPE)

    command_out = subproc.stdout.read().decode('utf-8')

    if "active (running)" not in command_out:
        send_email = True
        body += "    STATUS: Warning, not active or running. See output: \r\n"
        body += command_out + "\r\n\r\n"
    else:
        body += "    STATUS: OK\r\n\r\n"

subproc = subprocess.Popen(
    "df -h /dev/root | awk '{print $5}' | tail -1 | tr -d '%'",
    shell=True,
    stdout=subprocess.PIPE
)

disk_space_percent_full = int(subproc.stdout.read().decode('utf-8'))

if disk_space_percent_full > 75:
    send_email = True
    body += "\r\nWARNING DISK SPACE NEARING CAPACITY:"

body += "\r\n\r\nDISK SPACE: " + str(disk_space_percent_full) + "% full"


if send_email:
    msg = EmailMessage()
    msg['Subject'] = (
        "ALERT: [b1tst0rm] %s app server hourly service check" % (SERVER_TYPE))
    msg['From'] = "example@b1tst0rm.com"
    msg['To'] = "fake@b1tst0rm.com"
    msg.set_content(body)

    context = ssl.create_default_context()

    try:
        # Do NOT use STMP_SSL, it fails negotiating SSL versions.
        # Instead use the starttls command to force encryption.
        server = smtplib.SMTP('smtp-relay.gmail.com', 587)
        server.set_debuglevel(1)
        server.starttls(context=context)
        server.send_message(msg)
        server.quit()
        print('Email sent!')
    except Exception:
        traceback.print_exc()
else:
    print("[" + str(datetime.now()) + "] No issues found. DISK SPACE: " + str(disk_space_percent_full) + "% full")
