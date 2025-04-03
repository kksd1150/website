# admin_app.py
import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = "hr.db"  # ต้องเป็นไฟล์เดียวกับที่ app.py ใช้อยู่

class AdminMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Admin App (Desktop) - Manage Employees")

        self.container = QWidget()
        self.layout = QVBoxLayout()

        self.btn_goto_add_user = QPushButton("เพิ่มผู้ใช้ใหม่")
        self.btn_goto_add_user.clicked.connect(self.show_add_user_form)

        self.btn_reload_users = QPushButton("ดูรายชื่อผู้ใช้ (Reload)")
        self.btn_reload_users.clicked.connect(self.load_user_table)

        self.table_users = QTableWidget()
        self.table_users.setColumnCount(6)
        self.table_users.setHorizontalHeaderLabels([
            "ID", "Username", "Manager?", "LeaveBalance", "JobTitle", "Section"
        ])

        top_btn_layout = QHBoxLayout()
        top_btn_layout.addWidget(self.btn_goto_add_user)
        top_btn_layout.addWidget(self.btn_reload_users)

        self.layout.addLayout(top_btn_layout)
        self.layout.addWidget(self.table_users)
        self.container.setLayout(self.layout)
        self.setCentralWidget(self.container)

        self.ensure_table_user()
        self.load_user_table()

    def ensure_table_user(self):
        """
        สร้างตาราง user ถ้าไม่พบ
        """
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        create_user_sql = """
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_manager INTEGER DEFAULT 0,
            leave_balance INTEGER DEFAULT 20,
            job_title TEXT DEFAULT '',
            section TEXT DEFAULT ''
        );
        """
        c.execute(create_user_sql)
        conn.commit()
        conn.close()

    def load_user_table(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, username, is_manager, leave_balance, job_title, section FROM user")
        rows = c.fetchall()
        conn.close()

        self.table_users.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, value in enumerate(row_data):
                item = QTableWidgetItem(str(value))
                item.setFlags(item.flags() ^ Qt.ItemIsEditable)
                self.table_users.setItem(row_idx, col_idx, item)

    def show_add_user_form(self):
        self.add_user_dialog = AddUserDialog(parent=self)
        self.add_user_dialog.show()

class AddUserDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_win = parent
        self.setWindowTitle("Add New User")

        self.layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.input_username = QLineEdit()
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        self.checkbox_manager = QCheckBox()
        self.checkbox_manager.setChecked(False)
        self.input_leavebalance = QLineEdit("20")
        self.input_jobtitle = QLineEdit()
        self.input_section = QLineEdit()

        form_layout.addRow("Username:", self.input_username)
        form_layout.addRow("Password:", self.input_password)
        form_layout.addRow("Manager?:", self.checkbox_manager)
        form_layout.addRow("LeaveBalance:", self.input_leavebalance)
        form_layout.addRow("JobTitle:", self.input_jobtitle)
        form_layout.addRow("Section:", self.input_section)

        self.btn_save = QPushButton("Save User")
        self.btn_save.clicked.connect(self.save_user)

        self.layout.addLayout(form_layout)
        self.layout.addWidget(self.btn_save)
        self.setLayout(self.layout)

    def save_user(self):
        username = self.input_username.text().strip()
        password = self.input_password.text().strip()
        is_manager_val = 1 if self.checkbox_manager.isChecked() else 0
        leavebalance_str = self.input_leavebalance.text().strip()
        jobtitle = self.input_jobtitle.text().strip()
        section = self.input_section.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Warning", "กรุณากรอก username/password")
            return

        try:
            leavebalance = int(leavebalance_str)
        except ValueError:
            QMessageBox.warning(self, "Warning", "LeaveBalance ต้องเป็นตัวเลข")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM user WHERE username = ?", (username,))
        row = c.fetchone()
        if row:
            QMessageBox.warning(self, "Warning", f"Username '{username}' มีแล้วในระบบ")
            conn.close()
            return

        password_hash = generate_password_hash(password)
        sql = """
            INSERT INTO user
            (username, password_hash, is_manager, leave_balance, job_title, section)
            VALUES (?,?,?,?,?,?)
        """
        c.execute(sql, (username, password_hash, is_manager_val, leavebalance, jobtitle, section))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", f"User '{username}' created.")
        self.close()

        if self.parent_win:
            self.parent_win.load_user_table()

def main():
    app = QApplication(sys.argv)
    mainwindow = AdminMainWindow()
    mainwindow.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
