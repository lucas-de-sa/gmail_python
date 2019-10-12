import poplib  # Library for the Simple Mail Transfer Protocol
import os
import email    # Library for managing email messages
from email.parser import Parser
from email.header import decode_header
from email.utils import parseaddr

"""
POP3 code adapted from:
https://www.code-learner.com/python-use-pop3-to-read-email-example/
https://pythonprogramminglanguage.com/read-gmail-using-python/
"""


class Gmail_POP:
    ''' Implements the applications of a gmail account with POP3. '''

    pop_server = "pop.gmail.com"

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.server = None
        self.mails = None
        self.messages = []

    # Start POP3 Gmail session
    def session_POP(self):
        self.server = poplib.POP3_SSL(self.pop_server)
        self.server.user(self.username)
        self.server.pass_(self.password)

        welcome = self.server.getwelcome().decode('utf-8')
        print("{}\n".format(welcome))

    # Get how many messages you have in total
    def total_messages(self):
        m_num, size = self.server.stat()
        print('Messages:{}. Size: {}\n'.format(m_num, size))

    # Get all email IDs
    def get_mails(self):
        resp, mails, octets = self.server.list()
        self.mails = mails

    def __get_body_attachment(self, msg_object):
        body = ''
        attachment = None
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
                        os.getcwd() + "\\attachments_POP3", filename)
                else:
                    filepath = os.path.join(
                        os.getcwd() + "/attachments_POP3", filename)

                attachment = {'filepath': filepath, 'part': part}

        return body, attachment

    # Download all e-mail messages and store them in a dictionary
    def set_mailbox(self):
        mails = self.mails

        # Iterate through all emails. Mail ids are [b'1', b'2', ...].
        # If we wish to retrieve message b'1' we would need to send index '1' to server.retr() and so on
        for mail_id in range(0, len(mails)):
            # lines are each line of the original message
            resp, lines, octets = self.server.retr(mail_id + 1)

            # Turn message content into message object
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            # parser of RFC 2822 and MIME email messages. Turns the message content into a message object
            msg_object = Parser().parsestr(msg_content)

            msg_from = msg_object['from']
            msg_to = msg_object['To']
            msg_subject = msg_object['subject']

            body, attachment = self.__get_body_attachment(msg_object)
            self.messages.append(
                {'id': mails[mail_id], 'from': msg_from, 'to': msg_to, 'subject': msg_subject, 'attachment': attachment, 'body': body})

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

    def get_messages(self):
        messages = self.messages

        print("You have {} e-mail messages".format(len(messages)))
        for i in range(len(messages)):
            message = messages[i]
            print("Current ID: {}\tUnique Mail ID: {}\tSubject:{} From: {}\tTo: {}".format(
                i, message['id'], message['subject'], message['from'], message['to']))
        print("")
