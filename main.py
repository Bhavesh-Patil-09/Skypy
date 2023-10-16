from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QMessageBox,
    QTableWidget,
    QCheckBox,
    QTableWidgetItem,
    QAbstractItemView,
)
from utils import authenticate, fetch_all_contacts, create_group
from requests.exceptions import ConnectionError


class Data:
    def __init__(self, value):
        self.value = value


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Skype Login")

        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        # self.username_edit.setText("bhavesh.patil@atmstech.in")
        # self.password_edit.setText("Namdev@09")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.login_button = QPushButton("Login")
        self.login_error_label = QLabel()
        self.login_error_label.setStyleSheet("color: red")
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Email or Phone:"))
        self.layout.addWidget(self.username_edit)
        self.layout.addWidget(QLabel("Password:"))
        self.layout.addWidget(self.password_edit)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.login_error_label)
        self.setLayout(self.layout)
        self.login_button.clicked.connect(self.login)
        self.setGeometry(700, 400, 500, 250)

    def login(self):
        # Authenticate user
        username = self.username_edit.text()
        password = self.password_edit.text()
        if all([username, password]):
            try:
                _skype_obj = authenticate(username, password)
                if _skype_obj:
                    self.window2 = DataWindow(_skype_obj)
                    self.window2.show()
                    self.hide()
                else:
                    self.login_error_label.setText("Invalid username or password")
            except ConnectionError:
                self.login_error_label.setText("Please check your internet connection.")
            except Exception as e:
                self.login_error_label.setText(f"{str(e)}")
        else:
            self.login_error_label.setText("Username or password cannot be blank.")


class DataWindow(QWidget):
    def __init__(self, obj):
        super().__init__()
        self.skype_obj = obj
        self.contact_list = self.fetch_contacts()
        self.group_edit = QLineEdit()
        self.group_edit.setText("Default Group 1")
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Select users to create a group:"))
        # self.layout.addWidget(self.group_edit)
        # self.data_label = QLabel(f"Data value: {self.skype_obj}")
        # self.forward_button = QPushButton("Forward Data")
        # self.layout = QVBoxLayout()
        # self.layout.addWidget(self.data_label)
        # self.layout.addWidget(self.forward_button)
        # self.setLayout(self.layout)
        # self.forward_button.clicked.connect(self.forward_data)
        # self.setGeometry(500, 400, 600, 300)

        self.setWindowTitle("Create Group")

        # Create a table widget and add it to the window
        self.table_widget = QTableWidget(self)
        self.table_widget.setGeometry(50, 50, 300, 200)

        # Set the number of rows and columns in the table
        self.table_widget.setRowCount(len(self.contact_list))
        self.table_widget.setColumnCount(4)

        # Set the header labels for the rows and columns
        self.table_widget.setHorizontalHeaderLabels(
            ["Select", "Name", "Id", "Authorized"]
        )

        # Set the checkboxes for each row
        for i in range(self.table_widget.rowCount()):
            chkbox = QCheckBox(self)
            chkbox.setChecked(False)
            self.table_widget.setCellWidget(i, 0, chkbox)
            self.table_widget.setItem(
                i, 1, QTableWidgetItem(self.contact_list[i].name.first)
            )
            self.table_widget.setItem(i, 2, QTableWidgetItem(self.contact_list[i].id))
            if self.contact_list[i].authorised:
                self.table_widget.setItem(i, 3, QTableWidgetItem("Yes"))
            else:
                self.table_widget.setItem(i, 3, QTableWidgetItem("No"))

        # Set the table to allow selection of entire rows
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Add a delete button to the window
        self.delete_button = QPushButton("Add Group", self)
        self.delete_button.setGeometry(50, 250, 110, 30)

        self.layout.addWidget(self.table_widget)
        self.layout.addWidget(self.delete_button)
        self.setLayout(self.layout)
        self.delete_button.clicked.connect(self.get_checked_rows)
        self.setGeometry(200, 200, 550, 300)

    def get_checked_rows(self):
        self.userlist = []
        # Iterate through the rows and delete the ones that are checked
        for i in range(self.table_widget.rowCount()):
            chkbox = self.table_widget.cellWidget(i, 0)
            if chkbox:
                if chkbox.checkState() == Qt.CheckState.Checked:
                    user_id = self.table_widget.item(i, 2)
                    self.userlist.append(user_id.text())
                else:
                    continue
            else:
                continue

        print(self.userlist)
        # title = self.group_edit.text()
        cg = create_group(self.skype_obj, "", self.userlist)
        if cg:
            QMessageBox.information(self, "Success", "Successfully created group")
        else:
            QMessageBox.critical(self, "Error", "Creation unsuccessful")

    def fetch_contacts(self):
        contacts = fetch_all_contacts(obj=self.skype_obj)
        return contacts

    def forward_data(self):
        self.window3 = ForwardWindow(self.data)
        self.window3.show()

    def closeEvent(self, event):
        """Generate 'question' dialog on clicking 'X' button in title bar.
        Reimplement the closeEvent() event handler to include a 'Question'
        dialog with options on how to proceed - Save, Close, Cancel buttons
        """
        reply = QMessageBox.question(
            self,
            "Message",
            "Are you sure you want to quit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.No:
            event.ignore()
        else:
            event.accept()


class ForwardWindow(QWidget):
    def __init__(self, data):
        super().__init__()
        self.data = data
        self.data_label = QLabel(f"Data value: {self.data.value}")
        self.layout = QVBoxLayout()
        self.layout.addWidget(QLabel("Forwarded Data:"))
        self.layout.addWidget(self.data_label)
        self.setLayout(self.layout)


if __name__ == "__main__":
    app = QApplication([])
    window1 = LoginWindow()
    window1.show()
    app.exec_()
