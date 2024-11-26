import sqlite3
import bcrypt
import re
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.dropdown import DropDown

class StudyPalzApp(App):
    def build(self):
        self.title = "StudyPalz"
        self.setup_database()
        self.main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.create_welcome_page()
        return self.main_layout

    def setup_database(self):
        try:
            connection = sqlite3.connect("aakash.db", timeout=10)
            cursor = connection.cursor()
            cursor.execute(""" 
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    class TEXT NOT NULL
                )
            """)
            connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
        finally:
            if connection:
                connection.close()

    def create_welcome_page(self):
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(Label(text="Welcome to StudyPalz", font_size=24))
        self.main_layout.add_widget(Button(text="Get Started", on_press=lambda x: self.show_login_page()))
        self.main_layout.add_widget(Button(text="About Us", on_press=lambda x: self.show_about_page()))

    def show_login_page(self):
        self.main_layout.clear_widgets()
        self.username_input = TextInput(hint_text='Username', multiline=False)
        self.password_input = TextInput(hint_text='Password', password=True, multiline=False)
        self.main_layout.add_widget(self.username_input)
        self.main_layout.add_widget(self.password_input)
        self.main_layout.add_widget(Button(text="Login", on_press=lambda x: self.login_user()))
        self.main_layout.add_widget(Button(text="Register", on_press=lambda x: self.show_register_page()))

    def show_register_page(self):
        self.main_layout.clear_widgets()
        self.username_input = TextInput(hint_text='Username', multiline=False)
        self.email_input = TextInput(hint_text='Email', multiline=False)
        self.password_input = TextInput(hint_text='Password', password=True, multiline=False)
        self.class_dropdown = DropDown()
        for option in ["11th Grade", "12th Grade", "1st Year"]:
            btn = Button(text=option, size_hint_y=None, height=44)
            btn.bind(on_release=lambda btn: self.class_dropdown.select(btn.text))
            self.class_dropdown.add_widget(btn)
        self.class_button = Button(text='Select Class', on_release=self.class_dropdown.open)
        self.class_dropdown.bind(on_select=lambda instance, x: setattr(self.class_button, 'text', x))

        self.main_layout.add_widget(self.username_input)
        self.main_layout.add_widget(self.email_input)
        self.main_layout.add_widget(self.password_input)
        self.main_layout.add_widget(self.class_button)
        self.main_layout.add_widget(Button(text="Register", on_press=lambda x: self.register_user()))
        self.main_layout.add_widget(Button(text="Back to Login", on_press=lambda x: self.show_login_page()))

    def register_user(self):
        username = self.username_input.text
        email = self.email_input.text
        password = self.password_input.text
        user_class = self.class_button.text

        if not username or not email or not password or not user_class:
            self.show_popup("Error", "All fields are required!")
            return
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            self.show_popup("Error", "Invalid email address!")
            return
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        try:
            connection = sqlite3.connect("aakash.db", timeout=10)
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, class) VALUES (?, ?, ?, ?)",
                (username, email, hashed_password.decode("utf-8"), user_class)
            )
            connection .commit()
            self.show_popup("Success", "Account created!")
            self.show_login_page()
        except sqlite3.IntegrityError:
            self.show_popup("Error", "Username or email already exists!")
        except sqlite3.Error as e:
            self.show_popup("Error", f"Database error: {e}")
        finally:
            if connection:
                connection.close()

    def login_user(self):
        username = self.username_input.text
        password = self.password_input.text
        if not username or not password:
            self.show_popup("Error", "All fields are required!")
            return
        try:
            connection = sqlite3.connect("aakash.db", timeout=10)
            cursor = connection.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
            result = cursor.fetchone()
            if result and bcrypt.checkpw(password.encode("utf-8"), result[0].encode("utf-8")):
                self.show_popup("Success", f"Welcome, {username}!")
                self.show_menu_page()
            else:
                self.show_popup("Error", "Invalid credentials!")
        except sqlite3.Error as e:
            self.show_popup("Error", f"Database error: {e}")
        finally:
            if connection:
                connection.close()

    def show_menu_page(self):
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(Label(text="Menu", font_size=24))
        self.main_layout.add_widget(Button(text="Start Learning", on_press=lambda x: self.show_popup("Feature Coming Soon", "Start learning feature is under development.")))
        self.main_layout.add_widget(Button(text="View Progress", on_press=lambda x: self.show_popup("Feature Coming Soon", "Progress tracking feature is under development.")))
        self.main_layout.add_widget(Button(text="Logout", on_press=lambda x: self.show_login_page()))

    def show_about_page(self):
        self.main_layout.clear_widgets()
        self.main_layout.add_widget(Label(text="About StudyPalz", font_size=24))
        self.main_layout.add_widget(Label(text="StudyPalz is your personal learning companion, designed to help you stay focused, track your progress, and learn effectively."))
        self.main_layout.add_widget(Button(text="Back", on_press=lambda x: self.create_welcome_page()))

    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(0.8, 0.4))
        popup.open()

if __name__ == "__main__":
    StudyPalzApp().run()