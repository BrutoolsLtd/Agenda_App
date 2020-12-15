# main_window.py
# Author: Esteban Ortega
# Date: 12/12/20

"""Main module to create the agenda app."""

import os
import sys
import sqlite3
import random

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

from PIL import Image

# Create a db connection and cursor if it does not exist.
connection = sqlite3.connect("contacts.db")
cursor = connection.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Contacts
    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
     name TEXT, 
     surname TEXT, 
     phone TEXT, 
     email TEXT, 
     image TEXT, 
     address TEXT )''')
connection.commit()
# connection.close()

# Create a global variable for selected contact.
CONTACT_ID = None


class MainWindow(QWidget):
    """Represents the main window for agenda app."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Agenda")
        self.setGeometry(450, 150, 750, 600)
        self.create_layouts()
        self.create_widgets()
        self.add_widgets()
        self.apply_styles()
        self.connect_signals()

        self.update_contact_list()
        self.display_first_contact()

    def add_widgets(self):
        """Add widgets to layouts."""

        ########################################################################
        # Add widgets to left side
        ########################################################################
        self.button_layout.addWidget(self.button_new)
        self.button_layout.addWidget(self.button_update)
        self.button_layout.addWidget(self.button_delete)
        self.button_layout.addLayout(self.button_layout)
        self.contact_list_layout.addWidget(self.contact_list)
        self.button_layout.addLayout(self.contact_list_layout)

        ########################################################################
        # Add widgets to right side
        ########################################################################
        self.contact_image_layout.addWidget(self.display_image)
        self.display_information_layout.addRow("Name: ", self.display_name)
        self.display_information_layout.addRow("Surname: ", self.display_surname)
        self.display_information_layout.addRow("Phone: ", self.display_phone)
        self.display_information_layout.addRow("Email: ", self.display_email)
        self.display_information_layout.addRow("Address: ", self.display_address)

    def apply_styles(self):
        """Apply styles to widgets."""

        self.setStyleSheet("QGroupBox {font-color:blue; font-size:9pt}")

        self.group_box_information.setStyleSheet("font-size:9pt")

    def create_layouts(self):
        """Creates all layouts for MainWindow."""

        self.main_layout = QHBoxLayout()

        ########################################################################
        # Layout left side
        # Also create a group widget to help with design.
        ########################################################################
        group_box_list = QGroupBox("List of contacts")
        self.left_layout = QVBoxLayout()
        group_box_list.setLayout(self.left_layout)

        self.button_layout = QHBoxLayout()
        self.contact_list_layout = QHBoxLayout()

        self.left_layout.addLayout(self.button_layout)
        self.left_layout.addLayout(self.contact_list_layout)

        ########################################################################
        #Layout right side
        # Here also create widgets to help with design.
        ########################################################################
        self.group_box_information = QGroupBox("Contact Details")
        self.right_layout = QVBoxLayout()
        self.contact_image_layout = QVBoxLayout()
        self.contact_image_layout.setAlignment(Qt.AlignCenter)
        self.display_information_layout = QFormLayout()
        self.right_layout.addLayout(self.contact_image_layout)
        self.right_layout.addLayout(self.display_information_layout)

        self.group_box_information.setLayout(self.right_layout)

        ########################################################################
        # Add left, right layout to main layout and
        # set layout for mainWindow.
        ########################################################################
        self.main_layout.addWidget(group_box_list, 50)
        self.main_layout.addWidget(self.group_box_information, 50)
        self.setLayout(self.main_layout)

    def create_widgets(self):
        """Creates and adds all widgets to MainWindow."""
        ########################################################################
        # Widget for the left side, contact list
        ########################################################################
        self.contact_list = QListWidget()
        self.button_new = QPushButton("New")
        self.button_update = QPushButton("Update")
        self.button_delete = QPushButton("Delete")

        ########################################################################
        # Widget for the right side, Display contact information
        ########################################################################
        self.display_image = QLabel()
        self.display_name = QLabel()
        self.display_surname = QLabel()
        self.display_phone = QLabel()
        self.display_email = QLabel()
        self.display_address = QLabel()

    def connect_signals(self):
        """Connect widget signals."""

        self.button_new.clicked.connect(self.new_contact)
        self.contact_list.itemClicked.connect(self.on_item_clicked)
        self.button_delete.clicked.connect(self.on_delete)
        self.button_update.clicked.connect(self.on_update)

    def display_first_contact(self):
        """Display first record in database in group_box_information widget."""

        sql = "SELECT * FROM Contacts ORDER BY ROWid ASC LIMIT 1"
        contact = cursor.execute(sql).fetchone()

        if contact is None:

            self.display_name.setText("")
            self.display_surname.setText("")
            self.display_phone.setText("")
            self.display_email.setText("")
            self.display_image.setPixmap(QPixmap("icons/person.png"))
            self.display_address.setText("")

            return

        self.display_name.setText(contact[1])
        self.display_surname.setText(contact[2])
        self.display_phone.setText(contact[3])
        self.display_email.setText(contact[4])
        self.display_image.setPixmap(QPixmap(contact[5]))
        self.display_address.setText(contact[6])

    @staticmethod
    def get_contact(in_id):
        """Get contact info based on selected id.

        Return:
            Return a tuple with contact information.
        """

        sql_query = "SELECT * FROM Contacts WHERE id=?"
        return cursor.execute(sql_query, (in_id,)).fetchone()

    @staticmethod
    def get_all_contacts():
        """Get contacts from database.

        Returns:
            A list of tuples with id, name and surname [(id, name, surname),..]
            """

        sql = "SELECT id, name, surname FROM Contacts"

        return cursor.execute(sql).fetchall()

    def on_delete(self):
        """Deletes the selected record from database."""

        try:
            selected_contact = self.contact_list.currentItem().text()

        except AttributeError:

            QMessageBox.warning(self, "Warning", "You must select a contact!")

            return

        msg_box = QMessageBox.question(self,
                                       "Warning",
                                       "Are you sure?",
                                       QMessageBox.Yes | QMessageBox.No,
                                       QMessageBox.No)

        if msg_box == QMessageBox.Yes:

            id = selected_contact.split("-")[0]
            contact = self.get_contact(id)

            if contact[5] != "icons/person.png" and not contact[5]:
                os.remove(contact[5])

            sql_query = "DELETE FROM Contacts WHERE id=?"
            cursor.execute(sql_query, (id,))
            connection.commit()

            QMessageBox.information(self, "Information", "Contact deleted!")

            self.update_contact_list()

            self.display_first_contact()

    def on_item_clicked(self):
        """Updates contact information display widget."""

        selected_contact = self.contact_list.currentItem().text()
        id = selected_contact.split("-")[0]
        contact = self.get_contact(id)

        self.update_widgets(contact)

    def update_display_contact(self):
        """Updates display contact information widget at update."""

        contact = self.get_contact(CONTACT_ID)

        self.update_widgets(contact)

    def update_widgets(self, inContactTuple):
        """Update widgets to display information.

        Args:
            inContactTuple: Tuple with contact information based on passed id.
        """

        self.display_image.setPixmap(QPixmap(inContactTuple[5]))
        self.display_name.setText(inContactTuple[1])
        self.display_surname.setText(inContactTuple[2])
        self.display_phone.setText(inContactTuple[3])
        self.display_email.setText(inContactTuple[4])
        self.display_address.setText(inContactTuple[6])

    def on_closed_form_window(self):
        """Execute when form window is closed."""

        self.update_display_contact()
        self.update_contact_list()

    def on_update(self):
        """Updates contact on database."""

        if not self.contact_list.currentItem():

            QMessageBox.warning(self, "Warning", "You must select a contact!")

            return

        ########################################################################
        # Create the elements/info for the update window.
        ########################################################################
        global CONTACT_ID
        selected_contact = self.contact_list.currentItem().text()
        CONTACT_ID = selected_contact.split("-")[0]

        self.update_contact_win = ContactForm(status="Update")
        self.update_contact_win.setWindowModality(Qt.ApplicationModal)
        self.update_contact_win.setWindowTitle("Update Contact")

        ########################################################################
        # Populate update window with selected contact.
        ########################################################################
        contact = self.get_contact(CONTACT_ID)

        # Update contact information widget
        self.update_contact_win.NEW_CONTACT_IMAGE = contact[5]
        self.update_contact_win.image_add.setPixmap(QPixmap(contact[5]))
        self.update_contact_win.name_input.setText(contact[1])
        self.update_contact_win.surname_input.setText(contact[2])
        self.update_contact_win.phone_input.setText(contact[3])
        self.update_contact_win.email_input.setText(contact[4])
        self.update_contact_win.address_input.setText(contact[6])

        # Once created the instance we can connect the custom signal.
        self.update_contact_win.newContactClose.connect(self.on_closed_form_window)

        self.update_contact_win.show()

    def update_contact_list(self):
        """Updates contact_list widget with contact data."""

        self.contact_list.clear()

        for contact in self.get_all_contacts():
            compound_string = "{}-{} {}".format(str(contact[0]),
                                                contact[1],
                                                contact[2])
            self.contact_list.addItem(compound_string)

    def new_contact(self):
        """Launch NewContact window."""
        self.new_contact_win = ContactForm()
        self.new_contact_win.setWindowModality(Qt.ApplicationModal)
        self.new_contact_win.setWindowTitle("Add New Contact")

        # Once created the instance we can connect the custom signal.
        self.new_contact_win.newContactClose.connect(self.update_contact_list)

        self.new_contact_win.show()


class ContactForm(QWidget):
    """Window to create or update a contact."""

    # This is the value by default of the image for any contact
    # if there is no image selected.
    NEW_CONTACT_IMAGE = "icons/person.png"

    # Image size for resize.
    SIZE = (128, 128)

    # Define a signal to connect on MainWindow.
    newContactClose = pyqtSignal()

    def __init__(self, status="New"):
        super().__init__()

        self.STATUS = status

        self.setWindowTitle("Algo")
        self.setGeometry(450, 150, 375, 600)
        self.create_layouts()
        self.create_widgets()
        self.apply_styles()
        self.add_widgets()
        self.connect_signals()

    def closeEvent(self, QCloseEvent):
        """Override closeEvent method to be able to update my MainWindow."""

        self.newContactClose.emit()
        super(ContactForm, self).closeEvent(QCloseEvent)

    def add_widgets(self):
        """Add widgets to layouts"""

        ########################################################################
        # Add widgets to image layout
        ########################################################################
        self.image_layout.addWidget(self.image_add)
        self.image_layout.addWidget(self.load_image_button)

        ########################################################################
        # Add widgets to form layout
        ########################################################################
        self.form_layout.addRow(self.name_label, self.name_input)
        self.form_layout.addRow(self.surname_label, self.surname_input)
        self.form_layout.addRow(self.phone_label, self.phone_input)
        self.form_layout.addRow(self.email_label, self.email_input)
        self.form_layout.addRow(self.address_label, self.address_input)
        self.form_layout.addRow("", self.buttonBox)

    def apply_styles(self):
        """Apply styles to widgets."""

        self.setStyleSheet("font-size:9pt")
        self.load_image_button.setStyleSheet("background-color:rgb(255,200,100)")

    def create_layouts(self):
        """Creates all layouts required for NewContact window."""
        self.main_layout = QVBoxLayout()

        self.image_layout = QVBoxLayout()
        self.form_layout = QFormLayout()

        self.main_layout.addLayout(self.image_layout)
        self.main_layout.addLayout(self.form_layout)

        self.setLayout(self.main_layout)

    def create_widgets(self):
        """Creates and adds all widgets to layouts of NewContact window."""

        ########################################################################
        # Widget for the image
        ########################################################################
        self.image_add = QLabel()
        self.image_add.setPixmap(QPixmap(self.NEW_CONTACT_IMAGE))
        self.image_layout.setAlignment(Qt.AlignCenter)

        self.load_image_button = QPushButton("Load picture")

        ########################################################################
        # Widgets for form
        ########################################################################
        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter name")

        self.surname_label = QLabel("Surname:")
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Enter surname")

        self.phone_label = QLabel("Phone:")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Enter phone number")

        self.email_label = QLabel("Email:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter email")

        self.address_label = QLabel("Address:")
        self.address_input = QTextEdit()

        # Create buttons for NewContact window.
        self.buttonBox = QDialogButtonBox()
        if self.STATUS == "New":
            self.buttonBox.addButton("Add", QDialogButtonBox.AcceptRole)
        else:
            self.buttonBox.addButton("Update", QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton(QDialogButtonBox.Cancel)

    def connect_signals(self):
        """Connect widget signals."""

        ########################################################################
        # Connect signals for form widgets
        ########################################################################
        # self.buttonBox.accepted.connect(self.on_add)
        self.buttonBox.accepted.connect(self.on_button_clicked)
        self.buttonBox.rejected.connect(self.close)
        self.load_image_button.clicked.connect(self.upload_image)

    @staticmethod
    def get_contact(in_id):
        """Get contact info based on selected id.

        Return:
            Return a tuple with contact information.
        """

        sql_query = "SELECT * FROM Contacts WHERE id=?"
        return cursor.execute(sql_query, (in_id,)).fetchone()

    def on_add(self):
        """Execute when Add button has been pressed."""

        ########################################################################
        # Creates and Save image in project directory.
        ########################################################################
        if self.NEW_CONTACT_IMAGE != "icons/person.png":
            self.image_name = os.path.basename(self.NEW_CONTACT_IMAGE)
            self.image = Image.open(self.NEW_CONTACT_IMAGE)
            self.image_resized = self.image.resize(self.SIZE)

            new_image_name = "images/{}_{}".format(random.randint(1, 5000),
                                                   self.image_name)
            self.image_resized.save(new_image_name)

        else:

            new_image_name = self.NEW_CONTACT_IMAGE

        ########################################################################
        # Insert data in database.
        ########################################################################
        if (self.name_input.text() and self.surname_input.text() and
            self.phone_input.text()):

            sql = '''INSERT INTO Contacts (name,
                                           surname,
                                           phone,
                                           email,
                                           image,
                                           address)
                                           VALUES(?, ?, ?, ?, ?, ?)'''
            cursor.execute(sql, (self.name_input.text(),
                                 self.surname_input.text(),
                                 self.phone_input.text(),
                                 self.email_input.text(),
                                 new_image_name,
                                 self.address_input.toPlainText()))
            connection.commit()

            ####################################################################
            # Confirm insertion and close window.
            ####################################################################
            add_msg_box = QMessageBox.information(self,
                                                  "Information",
                                                  "Contact added")

            if add_msg_box:
                self.close()
        else:

            QMessageBox.warning(self,
                                "Warning",
                                "name, surname or phone fields can not be empty")

    def on_button_clicked(self):
        """Execute when button add or update is clicked."""

        if "Add" in [button.text() for button in self.buttonBox.buttons()]:

            self.on_add()

            return

        self.on_update()

    def on_update(self):
        """Exceute when update button is pressed."""

        global CONTACT_ID

        contact = self.get_contact(CONTACT_ID)

        if self.NEW_CONTACT_IMAGE == contact[5]:

            new_image_name = contact[5]

        else:

            ####################################################################
            # Creates and Save image in project directory.
            ####################################################################
            self.image_name = os.path.basename(self.NEW_CONTACT_IMAGE)
            self.image = Image.open(self.NEW_CONTACT_IMAGE)
            self.image_resized = self.image.resize(self.SIZE)

            new_image_name = "images/{}_{}".format(random.randint(1, 5000),
                                                   self.image_name)
            self.image_resized.save(new_image_name)

        ########################################################################
        # Insert data in database.
        ########################################################################
        if (self.name_input.text() and self.surname_input.text() and
            self.phone_input.text()):

            sql_query = '''UPDATE Contacts set name=?,
                                               surname=?,
                                               phone=?,
                                               email=?,
                                               image=?,
                                               address=?
                                               WHERE id=?'''

            cursor.execute(sql_query, (self.name_input.text(),
                                       self.surname_input.text(),
                                       self.phone_input.text(),
                                       self.email_input.text(),
                                       new_image_name,
                                       self.address_input.toPlainText(),
                                       CONTACT_ID))

            connection.commit()

            ####################################################################
            # Confirm Update and close window.
            ####################################################################
            add_msg_box = QMessageBox.information(self,
                                                  "Information",
                                                  "Contact Updated")

            if add_msg_box:

                self.close()

        else:

            QMessageBox.warning(self,
                                "Warning",
                                "name, surname or phone fields can not be empty")

    def upload_image(self):
        """Uploads selected image to project directory."""

        self.NEW_CONTACT_IMAGE , ok = QFileDialog.getOpenFileName(
            self, "Upload Image", "", "Image Files (*.jpg *.png)")

        if not ok:

            self.NEW_CONTACT_IMAGE = "icons/person.png"

            return

        # Display selected / uploaded image in widget.
        pixmap = QPixmap(self.NEW_CONTACT_IMAGE)
        resized_pixmap = pixmap.scaledToHeight(128)
        self.image_add.setPixmap(resized_pixmap)


def main():
    """Creates an instance of MainWindow and shows UI."""

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
