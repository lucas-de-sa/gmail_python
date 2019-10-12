from gmail import Gmail
from gmail_POP3 import Gmail_POP
import os


class App:
    ''' Terminal User Interface '''

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.gmail = Gmail(username, password)

        self.__clear_screen()

        print("Logged in as: {}\nThis is an App for using Gmail on your terminal!\n\n".format(
            self.username))

        self.main_menu()

    def __clear_screen(self):
        if (os.name == 'nt'):
            os.system('cls')
        else:
            os.system('clear')

    def send(self):
        recipient = input(
            "Type in the address of who you want to send an e-mail: ")
        subject = input("Type in the subject: ")
        print("Type in the body (enter a blank line when you`re finished): ")

        body = ""
        stopword = ""
        while True:
            line = input()
            if line.strip() == stopword:
                break
            body += "%s\n" % line

        self.gmail.send_message(recipient, subject, body)

        self.__clear_screen()
        print("message sent to {}\n\n".format(recipient))
        self.main_menu()

    def select_folder(self, mode='Read'):
        if (mode == 'Read'):
            print("From which folder would you like to read?\n")
        if (mode == 'Move_Message'):
            print("Select Folder to Move Message:")
        self.gmail.list_mailboxes()

        folders = self.gmail.folders
        total_mailboxes = len(folders) - 1
        selection = int(input())

        print(total_mailboxes, selection)

        if (selection <= total_mailboxes):
            self.__clear_screen()
            return folders[selection]
        else:
            self.__clear_screen()
            print(total_mailboxes)
            print("Please select a valid folder number.")
            self.select_folder()

    def read_folder(self):
        folder = self.select_folder()
        self.gmail.set_mailbox(folder)
        self.gmail.get_messages()

        if (len(self.gmail.messages) == 0):
            self.main_menu()

        total_messages = len(self.gmail.messages)
        selection = int(input("Select which e-mail to read:\n"))

        self.__clear_screen()
        self.gmail.read_message(selection)

    def read_POP3(self):
        gm = Gmail_POP(self.username, self.password)
        gm.session_POP()

        print("Downloading all messages.\n")
        gm.get_mails()
        gm.set_mailbox()

        gm.get_messages()
        selection = int(input("Select which e-mail to read:\n"))

        self.__clear_screen()
        gm.read_message(selection)

    def create_folder(self):
        folders = self.gmail.folders
        print("These are the current folders\n")
        self.gmail.list_mailboxes()

        selection = input(
            "Type in the name of the new folder (special symbols are prone to errors). If you want to create a subfolder you'll have to type in the full path, IE: 'Parent_Folder/Child_Folder':\n")
        name = '"{}"'.format(selection)

        if (name in folders):
            self.__clear_screen()
            print("You can't create two mailboxes with the same name.")
            self.create_folder()

        self.gmail.create_mailbox(name)
        self.__clear_screen()
        print("You created '{}'\nThis is the updated Folder List:\n".format(name))
        self.gmail.list_mailboxes()
        self.main_menu()

    def delete_folder(self):
        folders = self.gmail.folders
        print("These are the current folders\n")
        self.gmail.list_mailboxes()

        selection = input(
            "Type in the name of the folder you'd like to delete (DON'T TRY DELETING ANYTHING THAT'S DEFAULT FROM GMAIL):\n")
        name = '"{}"'.format(selection)

        if (name not in folders):
            self.__clear_screen()
            print(
                "You can't delete '{}' because it's not listed. A typo ocurred, perhaps?".format(name))
            self.delete_folder()

        self.gmail.delete_mailbox(name)
        self.__clear_screen()
        print("You deleted '{}'\nThis is the updated Folder List:\n".format(name))
        self.gmail.list_mailboxes()
        self.main_menu()

    def move_message(self):
        folder = self.select_folder()
        self.gmail.set_mailbox(folder)
        self.gmail.get_messages()

        if (len(self.gmail.messages) == 0):
            self.__clear_screen()
            print(
                "No messages in this folder. Please choose a folder that contains a message.\n")
            self.move_message()

        total_messages = len(self.gmail.messages)
        m_id = int(input("Select which e-mail to move:\n"))
        print("")

        destination_folder = self.select_folder(mode='Move_Message')
        self.gmail.move_message(m_id, destination_folder)

        print("Message moved to {}\n".format(destination_folder))
        self.main_menu()

    def folders_ops(self):
        selection = input(
            "Type what you would like to do and press Enter:\n1 - Create Folder\n2 - Delete Folder\n3 - Move e-mail between folders\n9 - Main Menu\n\n")

        if (selection == "1"):
            self.__clear_screen()
            self.create_folder()
        elif (selection == "2"):
            self.gmail.session_IMAP()
            self.__clear_screen()
            self.delete_folder()
            self.gmail.logout_IMAP()
            self.main_menu()
        elif (selection == "3"):
            self.__clear_screen()
            self.move_message()
        elif (selection == "9"):
            exit()
        else:
            self.__clear_screen()
            print("Please select 1, 2 or 3\n\n")
            self.main_menu()

    def main_menu(self):
        selection = input(
            "Type what you would like to do and press Enter:\n1 - Send e-mails\n2 - Read e-mails (IMAP)\n3 - Read e-mails (POP3)\n4 - Folders\n9 - Exit\n\n")

        if (selection == "1"):
            self.__clear_screen()
            self.send()
        elif (selection == "2"):
            self.gmail.session_IMAP()
            self.__clear_screen()
            self.read_folder()
            self.gmail.logout_IMAP()
            self.main_menu()
        elif (selection == "3"):
            self.__clear_screen()
            self.read_POP3()
            self.main_menu()
        elif (selection == "4"):
            self.__clear_screen()
            self.folders_ops()
        elif (selection == "9"):
            exit()
        else:
            self.__clear_screen()
            print("Please select 1, 2 or 3\n\n")
            self.main_menu()

# user = "redes.ep.teste@gmail.com"       # Remetente
# password = "redesach2026"

# gm = Gmail(user, password)
# gm.list_mailboxes()


def main():
    user = "redes.ep.teste@gmail.com"       # Remetente
    password = "redesach2026"
    app = App(user, password)


if __name__ == "__main__":
    main()
