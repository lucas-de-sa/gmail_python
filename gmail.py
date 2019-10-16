import smtplib  # Library for the Simple Mail Transfer Protocol
import imaplib  # Library for the Internet Message Access Protocol
# Library for managing email messages, which consist of headers (RFC 2822 style field names) and payloads
import email
import ssl
import os
import re


class Gmail:
    ''' Implements the applications of a gmail account with SMT and IMAP. '''

    smtp_server = "smtp.gmail.com"
    imap_server = "imap.gmail.com"
    # SSL context object with default settings
    context = ssl.create_default_context()

    def __init__(self, username, password, smtp_port=465, imap_port=993):
        self.username = username
        self.password = password
        self.smtp_port = smtp_port
        self.imap_port = imap_port
        self.session = None
        self.mail = None
        # List of dicts {'id': , 'from': , 'to': , 'subject': , 'attachment': , 'body': }
        self.messages = []
        self.folders = []  # List of folders in account
        self.cur_folder = ''

    def __session_SMTP(self):
        server = smtplib.SMTP_SSL(
            self.smtp_server, self.smtp_port, context=self.context)  # Connects into a encrypted SSL socket
        server.login(self.username, self.password)
        self.session = server

    def session_IMAP(self):
        self.mail = imaplib.IMAP4_SSL(self.imap_server, self.imap_port,
                                      ssl_context=self.context)
        self.mail.login(self.username, self.password)

    def logout_IMAP(self):
        self.mail.close()
        self.mail.logout()

    def send_message(self, recipient, subject, body):
        self.__session_SMTP()
        message = "Subject: {}\n\n".format(subject)
        message += "{}".format(body)
        self.session.sendmail(self.username, recipient, message)
        self.session.close()

    def __parse_mailbox(self, data):
        """
            Extracts folder name from the complete info of a folder.
            ie: (\\HasChildren) "/" "Folder 01"' becomes '"Folder 01"'
        """
        flags, b, c = data.partition(' ')
        separator, b, name = c.partition(' ')
        return (flags, separator.replace('"', ''), name.replace('"', ''))

    def load_mailbox(self):
        mail = self.mail
        resp, data = mail.list('""', '*')  # Lists mailbox names in "data"

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

    def list_mailboxes(self):
        i = 0
        for folder in self.folders:
            print('{} - {}'.format(i, folder))
            i += 1
        print("")

    def __get_body_attachment(self, msg_object):
        body = ''
        attachment = None

        # Iterar por partes de uma mensagem foi adaptado do código do Tim Poulsen neste endereço https://www.timpoulsen.com/2018/reading-email-with-python.html
        for part in msg_object.walk():      # Itera pelas subpartes de um objeto EmailMessage
            content_type = part.get_content_type()
            # Gets disposition of the content in each part of a message object
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

            # If the content disposition is 'attachment', we download it
            if ('attachment' in disp):
                filename = part.get_filename()

                # Apating filepaths between windows (nt) and linux
                if (os.name == 'nt'):
                    filepath = os.path.join(
                        os.getcwd() + "\\attachments", filename)
                else:
                    filepath = os.path.join(
                        os.getcwd() + "/attachments", filename)

                attachment = {'filepath': filepath, 'part': part}

        return body, attachment

    # Private function to check if user's specified folder exists
    def __check_mailbox(self, folder):
        resp, _ = self.mail.select(folder)
        if resp != 'OK':
            print("ERROR: Unable to open '{}' folder. Please check if the name's correct and try again.".format(
                folder))
            self.logout_IMAP
            sys.exit(1)

    def set_mailbox(self, folder='Inbox'):
        """Loads selected folder into class.messages list of dictionaries that follows the following format

            message = [
                        [ {'id': , 'from': , 'to': , 'subject': , 'attachment': , 'body': } ],
                        ...
                      ]
        """
        mail = self.mail
        self.cur_folder = folder

        self.__check_mailbox(folder)
        mbox_response, msg_numbers = mail.search(None, 'ALL')

        self.messages = []
        attachment = None

        # Itera por cada mensagem em uma pasta de e-mails
        # uid = unique ID of each e-mail
        for uid in msg_numbers[0].split():
            # Fetches parts of messages in the RFC822 format
            fetch_resp, raw_msg = mail.fetch(uid, '(RFC822)')
            msg_object = email.message_from_bytes(raw_msg[0][1])

            msg_from = msg_object['from']
            msg_to = msg_object['To']
            msg_subject = msg_object['subject']

            body, attachment = self.__get_body_attachment(msg_object)
            self.messages.append(
                {'id': uid, 'from': msg_from, 'to': msg_to, 'subject': msg_subject, 'attachment': attachment, 'body': body})

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
        print("From: {}\nTo: {}\nSubject:{}\n{}".format(
            message['from'], message['to'], message['subject'], message['body']))

        # If message has attachment, we save it on "./attachments/"
        attachment = message['attachment']
        if (isinstance(attachment, dict)):
            print("saving attachment to: {}\n\n".format(
                attachment['filepath']))
            file = open(attachment['filepath'], "wb")
            file.write(attachment['part'].get_payload(decode=True))
            file.close()

    def create_mailbox(self, name):
        self.mail.create(name)
        self.load_mailbox()

    def delete_mailbox(self, name):
        self.mail.delete(name)
        self.load_mailbox()

    def move_message(self, m_id, folder_name):
        if "[Gmail]" in folder_name:
            # Gets 'pure' Gmail folder root name ("[Gmail]/Trash" becomes '/Trash"'')
            folder_name = folder_name.split("]", 1)[1]
            folder_name = folder_name[:-1]             # Removes last '"'
            folder_name = folder_name.replace("/", "\\")

        uid = self.messages[m_id]['id']
        # Moves message to new folder
        self.mail.store(uid, '+X-GM-LABELS', folder_name)
        # Deletes original message
        self.mail.store(uid, '+FLAGS', '(\Deleted)')


'''
gm = Gmail("redes.ep.teste@gmail.com", "redesach2026")
gm.session_IMAP()
gm.load_mailbox()
'''
