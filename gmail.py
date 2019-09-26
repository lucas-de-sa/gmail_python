import smtplib  # Library for the Simple Mail Transfer Protocol
import imaplib  # Library for the Internet Message Access Protocol
import email    # Library for managing email messages
import ssl
import base64
import os
import re


class Gmail:
    ''' Implements the applications of a gmail account with SMT and IMAP. '''

    smtp_server = "smtp.gmail.com"
    imap_server = "imap.gmail.com"
    context = ssl.create_default_context()

    def __init__(self, username, password, smtp_port=465, imap_port=993):
        self.username = username
        self.password = password
        self.smtp_port = smtp_port
        self.imap_port = imap_port
        self.session = None
        self.mail = None
        self.messages = []
        self.folders = []
        self.cur_folder = ''

        self.session_IMAP()
        self.load_folders()
        # self.set_folder()

    def __session_SMTP(self):
        server = smtplib.SMTP_SSL(
            self.smtp_server, self.smtp_port, context=self.context)
        server.login(self.username, self.password)
        self.session = server

    def session_IMAP(self):
        self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port,
                                      ssl_context=self.context)
        self.mail.login(self.username, self.password)

    def __logout_IMAP(self):
        self.mail.close()
        self.mail.logout()

    def send_message(self, recipient, subject, body):
        self.__session_SMTP()
        message = "Subject: {}\n\n".format(subject)
        message += "{}".format(body)
        self.session.sendmail(self.username, recipient, message)
        self.session.close()

    def __parse_mailbox(self, data):
        flags, b, c = data.partition(' ')
        separator, b, name = c.partition(' ')
        return (flags, separator.replace('"', ''), name.replace('"', ''))

    def __get_body_attachment(self, msg_object):
        body = ''
        attachment = None
        for part in msg_object.walk():      # Itera pelas subpartes de um objeto EmailMessage
            content_type = part.get_content_type()
            disp = str(part.get('Content-Disposition'))

            if (content_type == 'text/plain'):
                charset = part.get_content_charset()

                # If charset from body is none (like SMTP sent messages stored in '[Gmail]/Sent Mail' that have no payload for body)
                # then we turn the whole email message into a string and get everything bellow the subject field
                if charset is None:
                    complete_message = str(part)
                    str_from_subject = complete_message.split("Subject:", 1)[1]
                    body = str_from_subject.split("\n", 2)[2]
                    continue

                # If charset is UTF8, then it's a normal body
                body = part.get_payload(decode=True).decode(
                    encoding=charset, errors="ignore")

            if ('attachment' in disp):
                filename = part.get_filename()

                if (os.name == 'nt'):
                    filepath = os.path.join(
                        os.getcwd() + "\\attachments", filename)
                else:
                    filepath = os.path.join(
                        os.getcwd() + "/attachments", filename)

                attachment = {'filepath': filepath, 'part': part}

        return body, attachment

    def load_folders(self):
        mail = self.mail
        resp, data = mail.list('""', '*')

        self.folders = []
        user_folders = ['"INBOX"']
        gmail_folders = []
        for mbox in data:
            flags, separator, name = self.__parse_mailbox(bytes.decode(mbox))

            if "[Gmail]/" in name:
                name = name.split("/ ", 1)[1]
                gmail_folders.append('"{}"'.format(name))
                continue

            if name == 'INBOX':
                continue

            user_folders.append('"{}"'.format(name))

        # Removing useless root Gmail folder ( '/ [Gmail]' )
        user_folders.pop()
        self.folders = user_folders + gmail_folders

    def list_folders(self):
        i = 0
        for folder in self.folders:
            print('{} - {}'.format(i, folder))
            i += 1

    # Private function to check if user's specified folder exists
    def __check_folder(self, folder):
        resp, _ = self.mail.select(folder)
        if resp != 'OK':
            print("ERROR: Unable to open '{}' folder. Please check if the name's correct and try again.".format(
                folder))
            self.__logout_IMAP
            sys.exit(1)

    def set_folder(self, folder='Inbox'):
        """Loads selected folder into class.messages list of dictionaries that follows the following format

            message = [
                        [ {'id': '', 'subject': '', 'attachment': '', 'body': ''} ],
                        ...
                      ]
        """
        mail = self.mail
        self.cur_folder = folder

        self.__check_folder(folder)
        mbox_response, msg_numbers = mail.search(None, 'ALL')

        self.messages = []
        attachment = None

        # Itera por cada mensagem em uma pasta de e-mails
        # uid = unique ID of each e-mail
        for uid in msg_numbers[0].split():
            fetch_resp, raw_msg = mail.fetch(uid, '(RFC822)')
            msg_object = email.message_from_bytes(raw_msg[0][1])
            msg_subject = msg_object['subject']
            msg_from = msg_object['from']

            body, attachment = self.__get_body_attachment(msg_object)
            self.messages.append(
                {'id': uid, 'subject': msg_subject, 'attachment': attachment, 'body': body})
        # self.__logout_IMAP()

    def get_current_folder(self):
        print('You are in {} folder'.format(self.cur_folder))

    def get_messages(self):
        messages = self.messages

        print("You have {} e-mail messages in {} folder:".format(len(messages), self.cur_folder))
        for i in range(len(messages)):
            message = messages[i]
            print("Current ID: {}\tUnique Mail ID: {}\tSubject:{}".format(
                i, message['id'], message['subject']))
        print("")

    def read_message(self, id):
        message = self.messages[id]
        print("Subject:{}\n{}".format(message['subject'], message['body']))

    def create_mailbox(self, name):
        self.mail.create(name)
        self.load_folders()

    def delete_mailbox(self, name):
        self.mail.delete(name)
        self.load_folders()

    def move_message(self, m_id, folder_name):
        # print(self.messages[m_id]['id'])

        if "[Gmail]" in folder_name:
            # Gets 'pure' Gmail folder root name ("[Gmail]/Trash" becomes '/Trash"'')
            folder_name = folder_name.split("]", 1)[1]
            folder_name = folder_name[:-1]             # Removes last '"'
            folder_name = folder_name.replace("/", "\\")
        print(folder_name)

        uid = self.messages[m_id]['id']
        # Moves message to new folder
        self.mail.store(uid, '+X-GM-LABELS', folder_name)
        # Deletes original message
        self.mail.store(uid, '+FLAGS', '(\Deleted)')


user = "redes.ep.teste@gmail.com"       # Remetente
password = "redesach2026"

recipient = "redes.ep.teste@gmail.com"  # Destinatário
subject = "This is a test"
body = "Sending this goddamn e-mail"

folder = '"Folder 01"'
#folder = '"[Gmail]/Sent Mail"'

gm = Gmail(user, password)

# gm.send_message(recipient, subject, body)

# gm.list_messages()
#gm.create_mailbox('"Folder 01"')
#gm.create_mailbox('"Folder 01/Children_Folder_01"')
#gm.delete_mailbox('"Folder 01/Children_Folder_01"')
gm.list_folders()
gm.set_folder(folder)

gm.get_messages()

gm.move_message(0, gm.folders[3])

# gm.list_folders()
# gm.set_folder(folder)
# a = gm.messages[0]['attachment']
# gm.list_messages()
# gm.read_message(0)

# gm.list_messages()
# fp = open(a['filepath'], 'wb')
# fp.write(a['part'].get_payload(decode=True))
# fp.close()

# gm.list_folders()
# test commit
