import os
import sys
import json
import io
import traceback
import contextlib
import webbrowser
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit,
    QMessageBox, QHBoxLayout, QDialog, QTextEdit, QComboBox, QFileDialog,
    QTreeWidget, QTreeWidgetItem, QInputDialog, QSplitter
)
from PyQt5.QtCore import Qt

# ======================================================
#  FIXED — USER DATA SAVES IN AppData/Roaming
# ======================================================

APPDATA = os.getenv("APPDATA")
CESTUDIO_FOLDER = os.path.join(APPDATA, "CEStudio")
USER_DIR = os.path.join(CESTUDIO_FOLDER, "Users")
CURRENT_USER_FILE = os.path.join(CESTUDIO_FOLDER, "current_user.json")

os.makedirs(USER_DIR, exist_ok=True)

# ======================================================
# LANGUAGE CONFIG
# ======================================================
LANGUAGE_EXTENSIONS = {
    "Python": ".py",
    "JavaScript": ".js",
    "HTML": ".html",
    "CSS": ".css",
    "Java": ".java",
    "C": ".c",
    "C++": ".cpp",
    "C#": ".cs",
    "Go": ".go",
    "Rust": ".rs",
    "Kotlin": ".kt",
    "Ruby": ".rb",
    "PHP": ".php",
    "TypeScript": ".ts",
    "Scala": ".scala",
    "Perl": ".pl",
    "Lua": ".lua",
}

WEB_LANGUAGES = ["HTML", "CSS", "JavaScript"]

# ======================================================
# MAIN CLASS
# ======================================================
class CEStudioApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CE Studio")
        self.setGeometry(300, 200, 1200, 700)
        self.setStyleSheet("background-color: #1e1e1e; color: white; font-family: Arial;")

        # Try auto-login
        if os.path.exists(CURRENT_USER_FILE):
            try:
                with open(CURRENT_USER_FILE, "r") as f:
                    data = json.load(f)
                    username = data.get("username")
                    if username and os.path.exists(os.path.join(USER_DIR, username)):
                        self.open_studio()
                        return
            except:
                pass

        # Show login if not logged in
        self.init_login_screen()

    # ======================================================
    # LOGIN / SIGNUP
    # ======================================================

    def init_login_screen(self):
        self.clear_layout()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("CE Studio Login")
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter Username")
        self.username_input.setStyleSheet(self.input_style())
        layout.addWidget(self.username_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self.input_style())
        layout.addWidget(self.password_input)

        login_btn = QPushButton("Login")
        login_btn.setStyleSheet(self.button_style())
        login_btn.clicked.connect(self.login)
        layout.addWidget(login_btn)

        signup_btn = QPushButton("Sign Up")
        signup_btn.setStyleSheet(self.button_style(True))
        signup_btn.clicked.connect(self.init_signup_screen)
        layout.addWidget(signup_btn)

        self.setLayout(layout)

    def init_signup_screen(self):
        self.clear_layout()

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        title = QLabel("Create CE Studio Account")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 22px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        self.new_username = QLineEdit()
        self.new_username.setPlaceholderText("Choose Username")
        self.new_username.setStyleSheet(self.input_style())
        layout.addWidget(self.new_username)

        self.new_password = QLineEdit()
        self.new_password.setPlaceholderText("Choose Password")
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setStyleSheet(self.input_style())
        layout.addWidget(self.new_password)

        create_btn = QPushButton("Create Account")
        create_btn.setStyleSheet(self.button_style())
        create_btn.clicked.connect(self.create_account)
        layout.addWidget(create_btn)

        back_btn = QPushButton("Back to Login")
        back_btn.setStyleSheet(self.button_style(True))
        back_btn.clicked.connect(self.init_login_screen)
        layout.addWidget(back_btn)

        self.setLayout(layout)

    def create_account(self):
        username = self.new_username.text().strip()
        password = self.new_password.text().strip()

        if not username or not password:
            self.show_message("Please enter both username and password.")
            return

        user_path = os.path.join(USER_DIR, username)
        if os.path.exists(user_path):
            self.show_message("Username already exists!")
            return

        os.makedirs(user_path)

        with open(os.path.join(user_path, "account.json"), "w") as f:
            json.dump({"username": username, "password": password}, f)

        self.show_message("Account created successfully!", True)
        self.init_login_screen()

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()  # FIXED

        user_folder = os.path.join(USER_DIR, username)
        account_file = os.path.join(user_folder, "account.json")

        if not os.path.exists(account_file):
            self.show_message("User not found! Please sign up.")
            return

        with open(account_file, "r") as f:
            data = json.load(f)

        if data.get("password") != password:
            self.show_message("Incorrect password!")
            return

        with open(CURRENT_USER_FILE, "w") as f:
            json.dump({"username": username}, f)

        self.show_message("Login successful!", True)
        self.open_studio()

    # ======================================================
    # MAIN MENU
    # ======================================================

    def open_studio(self):
        self.clear_layout()

        main_layout = QVBoxLayout()
        top_bar = QHBoxLayout()

        editor_btn = QPushButton("Editor")
        editor_btn.setStyleSheet(self.button_style())
        editor_btn.clicked.connect(self.open_editor)
        top_bar.addWidget(editor_btn)

        store_btn = QPushButton("Marketplace")
        store_btn.setStyleSheet(self.button_style())
        store_btn.clicked.connect(self.open_marketplace)
        top_bar.addWidget(store_btn)

        logout_btn = QPushButton("Log Out")
        logout_btn.setStyleSheet(self.button_style(True))
        logout_btn.clicked.connect(self.logout)
        top_bar.addWidget(logout_btn)

        main_layout.addLayout(top_bar)

        welcome = QLabel("Welcome to CE Studio!", self)
        welcome.setAlignment(Qt.AlignCenter)
        welcome.setStyleSheet("font-size: 20px; font-weight: bold; margin-top: 50px;")
        main_layout.addWidget(welcome)

        self.setLayout(main_layout)

    # ======================================================
    # MARKETPLACE
    # ======================================================
    def open_marketplace(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("CE Studio Marketplace")
        dlg.setGeometry(400, 200, 400, 250)

        layout = QVBoxLayout()
        label = QLabel("Marketplace Coming Soon!")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        close = QPushButton("Close")
        close.clicked.connect(dlg.accept)
        layout.addWidget(close)

        dlg.setLayout(layout)
        dlg.exec_()

    # ======================================================
    # EDITOR UI
    # ======================================================

    def open_editor(self):
        self.clear_layout()

        main_splitter = QSplitter(Qt.Horizontal)

        # EXPLORER PANEL
        explorer_widget = QWidget()
        explorer_layout = QVBoxLayout()

        self.explorer = QTreeWidget()
        self.explorer.setHeaderLabels(["Name", "Type"])
        self.explorer.setColumnWidth(0, 200)
        self.explorer.itemDoubleClicked.connect(self.open_file_from_tree)  # <-- clickable
        explorer_layout.addWidget(self.explorer)

        load_btn = QPushButton("Load Folder")
        load_btn.setStyleSheet(self.button_style())
        load_btn.clicked.connect(self.load_folder)
        explorer_layout.addWidget(load_btn)

        add_file_btn = QPushButton("Add File")
        add_file_btn.setStyleSheet(self.button_style())
        add_file_btn.clicked.connect(self.add_file_to_folder)
        explorer_layout.addWidget(add_file_btn)

        explorer_widget.setLayout(explorer_layout)
        main_splitter.addWidget(explorer_widget)

        # EDITOR + TERMINAL PANEL
        editor_splitter = QSplitter(Qt.Vertical)

        # EDITOR SECTION
        editor_widget = QWidget()
        editor_layout = QVBoxLayout()

        back_btn = QPushButton("← Back")
        back_btn.setStyleSheet(self.button_style(True))
        back_btn.clicked.connect(self.open_studio)
        editor_layout.addWidget(back_btn)

        self.lang_select = QComboBox()
        self.lang_select.setEditable(True)
        self.lang_select.addItems(list(LANGUAGE_EXTENSIONS.keys()))
        self.lang_select.setStyleSheet("padding: 5px; font-size: 14px;")
        editor_layout.addWidget(self.lang_select)

        self.code_editor = QTextEdit()
        self.code_editor.setStyleSheet("""
            background-color: #1e1e1e;
            color: #ffffff;
            font-family: Consolas, monospace;
            font-size: 14px;
        """)
        editor_layout.addWidget(self.code_editor)

        button_row = QHBoxLayout()

        run_btn = QPushButton("Run")
        run_btn.setStyleSheet(self.button_style())
        run_btn.clicked.connect(self.run_code)
        button_row.addWidget(run_btn)

        save_btn = QPushButton("Save")
        save_btn.setStyleSheet(self.button_style())
        save_btn.clicked.connect(self.save_code)
        button_row.addWidget(save_btn)

        load_btn = QPushButton("Load")
        load_btn.setStyleSheet(self.button_style())
        load_btn.clicked.connect(self.load_code)
        button_row.addWidget(load_btn)

        editor_layout.addLayout(button_row)

        editor_widget.setLayout(editor_layout)
        editor_splitter.addWidget(editor_widget)

        # TERMINAL SECTION
        terminal_widget = QWidget()
        terminal_layout = QVBoxLayout()

        self.terminal_label = QLabel("Terminal: No folder loaded")
        terminal_layout.addWidget(self.terminal_label)

        self.terminal_output = QTextEdit()
        self.terminal_output.setReadOnly(True)
        self.terminal_output.setStyleSheet("""
            background-color: #111;
            color: #00ff00;
            font-family: Consolas;
            font-size: 12px;
        """)
        terminal_layout.addWidget(self.terminal_output)

        self.terminal_input = QLineEdit()
        self.terminal_input.setPlaceholderText("Enter command and press Enter")
        self.terminal_input.setStyleSheet("""
            background-color: #222;
            color: white;
            padding: 5px;
        """)
        self.terminal_input.returnPressed.connect(self.run_terminal_command)
        terminal_layout.addWidget(self.terminal_input)

        terminal_widget.setLayout(terminal_layout)
        editor_splitter.addWidget(terminal_widget)

        main_splitter.addWidget(editor_splitter)

        layout = QVBoxLayout()
        layout.addWidget(main_splitter)

        self.setLayout(layout)

    # ======================================================
    # EXPLORER FUNCTIONS
    # ======================================================

    def load_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.current_folder = folder_path
            self.terminal_label.setText(f"Terminal: {folder_path}")
            self.explorer.clear()
            self.add_folder_to_tree(folder_path, self.explorer.invisibleRootItem())

    def add_folder_to_tree(self, path, parent_item):
        for item_name in os.listdir(path):
            item_path = os.path.join(path, item_name)
            if os.path.isdir(item_path):
                folder_item = QTreeWidgetItem([item_name, "Folder"])
                parent_item.addChild(folder_item)
                self.add_folder_to_tree(item_path, folder_item)
            else:
                file_item = QTreeWidgetItem([item_name, os.path.splitext(item_name)[1]])
                parent_item.addChild(file_item)

    def add_file_to_folder(self):
        if not hasattr(self, "current_folder"):
            self.show_message("Load a folder first!")
            return

        file_name, ok = QInputDialog.getText(self, "Add File", "File name (with extension):")
        if ok and file_name:
            new_path = os.path.join(self.current_folder, file_name)
            with open(new_path, "w", encoding="utf-8") as f:
                f.write("")
            self.load_folder()

    # ======================================================
    # CLICKABLE EXPLORER FUNCTIONS
    # ======================================================
    def open_file_from_tree(self, item, column):
        file_path = self.get_full_path_from_item(item)
        if os.path.isfile(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.code_editor.setPlainText(content)
                # Set language automatically
                ext = os.path.splitext(file_path)[1]
                for lang, lang_ext in LANGUAGE_EXTENSIONS.items():
                    if lang_ext == ext:
                        self.lang_select.setCurrentText(lang)
                        break
                self.show_message(f"Loaded {os.path.basename(file_path)}", True)
            except Exception as e:
                self.show_message(f"Failed to load file: {str(e)}")

    def get_full_path_from_item(self, item):
        parts = []
        while item is not None:
            parts.insert(0, item.text(0))
            item = item.parent()
        return os.path.join(self.current_folder, *parts)

    # ======================================================
    # RUN / SAVE / LOAD CODE
    # ======================================================

    def run_code(self):
        code = self.code_editor.toPlainText()
        lang = self.lang_select.currentText()

        if lang in WEB_LANGUAGES:
            html_file = os.path.join(CESTUDIO_FOLDER, "temp_preview.html")
            html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body>
{code if lang == "HTML" else ""}
<script>{code if lang == "JavaScript" else ""}</script>
</body>
</html>
"""
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(html)
            webbrowser.open(f"file://{html_file}")
            return

        if lang == "Python":
            buffer = io.StringIO()
            try:
                with contextlib.redirect_stdout(buffer), contextlib.redirect_stderr(buffer):
                    exec(code, {})
            except Exception:
                buffer.write(traceback.format_exc())
            out = buffer.getvalue()
        else:
            out = f"Running {lang} not supported yet."

        dlg = QDialog(self)
        dlg.setWindowTitle("Output")
        layout = QVBoxLayout()
        txt = QTextEdit()
        txt.setReadOnly(True)
        txt.setPlainText(out)
        layout.addWidget(txt)
        close = QPushButton("Close")
        close.clicked.connect(dlg.accept)
        layout.addWidget(close)
        dlg.setLayout(layout)
        dlg.resize(600, 400)
        dlg.exec_()

    def save_code(self):
        code = self.code_editor.toPlainText()
        lang = self.lang_select.currentText()
        ext = LANGUAGE_EXTENSIONS.get(lang, ".txt")

        file, _ = QFileDialog.getSaveFileName(self, "Save", "", f"*{ext}")
        if file:
            if not file.endswith(ext):
                file += ext
            with open(file, "w", encoding="utf-8") as f:
                f.write(code)
            self.show_message("File saved!", True)

    def load_code(self):
        lang = self.lang_select.currentText()
        ext = LANGUAGE_EXTENSIONS.get(lang, "*")

        file, _ = QFileDialog.getOpenFileName(self, "Load", "", f"*{ext}")
        if file:
            with open(file, "r", encoding="utf-8") as f:
                self.code_editor.setPlainText(f.read())
            self.show_message("File loaded!", True)

    # ======================================================
    # TERMINAL
    # ======================================================

    def run_terminal_command(self):
        if not hasattr(self, "current_folder"):
            self.show_message("Load a folder first!")
            return

        cmd = self.terminal_input.text().strip()
        if not cmd:
            return

        self.terminal_output.append(f"> {cmd}")

        try:
            result = subprocess.run(
                cmd, shell=True, cwd=self.current_folder,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            self.terminal_output.append(result.stdout + result.stderr)
        except Exception as e:
            self.terminal_output.append(str(e))

        self.terminal_input.clear()

    # ======================================================
    # LOGOUT
    # ======================================================
    def logout(self):
        if os.path.exists(CURRENT_USER_FILE):
            os.remove(CURRENT_USER_FILE)
        self.init_login_screen()

    # ======================================================
    # UTILS
    # ======================================================
    def input_style(self):
        return """
        QLineEdit {
            padding: 10px;
            border: 1px solid #555;
            border-radius: 5px;
            background-color: #2e2e2e;
            color: white;
            font-size: 14px;
        }
        QLineEdit:focus {
            border: 1px solid #0078d7;
        }
        """

    def button_style(self, secondary=False):
        if secondary:
            return """
            QPushButton {
                background-color: #333;
                color: #ccc;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #444;
            }
            """
        return """
        QPushButton {
            background-color: #0078d7;
            color: white;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #005a9e;
        }
        """

    def show_message(self, text, success=False):
        msg = QMessageBox(self)
        msg.setWindowTitle("CE Studio")
        msg.setText(text)
        msg.setIcon(QMessageBox.Information if success else QMessageBox.Warning)
        msg.exec_()

    def clear_layout(self):
        if self.layout() is not None:
            QWidget().setLayout(self.layout())


# ======================================================
# RUN APP
# ======================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CEStudioApp()
    window.show()
    sys.exit(app.exec_())
