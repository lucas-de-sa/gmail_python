import smtplib  # Library for the Simple Mail Transfer Protocol
import imaplib  # Library for the Internet Message Access Protocol
import email    # Library for managing email messages
import ssl
import base64
import os


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

    def __session_SMTP(self):
        server = smtplib.SMTP_SSL(
            self.smtp_server, self.smtp_port, context=self.context)
        server.login(self.username, self.password)
        self.session = server

    def __session_IMAP(self):
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

    def __check_folder(self, recipient_folder):
        resp, _ = self.mail.select(recipient_folder)
        if resp != 'OK':
            print("ERROR: Unable to open '{}' folder. Please check if the name's correct and try again.".format(
                recipient_folder))
            sys.exit(1)

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

    def list_folders(self):
        self.__session_IMAP()
        mail = self.mail
        resp, data = mail.list('""', '*')
        for mbox in data:
            flags, separator, name = self.__parse_mailbox(bytes.decode(mbox))
            fmt = '{0}    : [Flags = {1}; Separator = {2}'
            print(fmt.format(name, flags, separator))

    def set_folder(self, recipient_folder='Inbox'):
        self.__session_IMAP()
        mail = self.mail

        self.__check_folder(recipient_folder)
        mbox_response, msg_numbers = mail.search(None, 'ALL')

        self.messages = []
        attachment = None
        # Itera por cada mensagem em uma pasta de e-mails
        for num in msg_numbers[0].split():
            fetch_resp, raw_msg = mail.fetch(num, '(RFC822)')
            msg_object = email.message_from_bytes(raw_msg[0][1])
            msg_subject = msg_object['subject']
            msg_from = msg_object['from']

            if (msg_subject != 'Test 3 - Attachments'):
                continue

            body, attachment = self.__get_body_attachment(msg_object)
            self.messages.append(
                {'num': num, 'subject': msg_subject, 'attachment': attachment, 'body': body})
        self.__logout_IMAP()


user = "redes.ep.teste@gmail.com"       # Remetente
password = "redesach2026"

recipient = "redes.ep.teste@gmail.com"  # Destinatário
subject = "This is a test"
body = "Sending this goddamn e-mail"

gm = Gmail(user, password)
#gm.send_message(recipient, subject, body)
#gm.set_folder(recipient_folder='"Folder 01/Children_Folder_01"')
gm.set_folder()
a = gm.messages[0]['attachment']

fp = open(a['filepath'], 'wb')
fp.write(a['part'].get_payload(decode=True))
fp.close()

# gm.list_folders()
# test commit
