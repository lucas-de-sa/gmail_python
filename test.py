import email
import email.header
import imaplib
import os
import sys

host = "imap.gmail.com"
port = 993

username = "redes.ep.teste@gmail.com"
password = "redesach2026"
recipient_folder = 'INBOX'
sender = 'lucasdesapereira@gmail.com'

mail = imaplib.IMAP4_SSL(host, port)
mail.login(username, password)

# select the folder, by default INBOX
resp, _ = mail.select(recipient_folder)
if resp != 'OK':
    print("ERROR: Unable to open the {} folder".format(recipient_folder))
    sys.exit(1)

messages = []
mbox_response, msgnums = mail.search(None, 'FROM', sender)

print(msgnums)
