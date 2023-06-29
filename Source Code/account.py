import sqlite3
from bcrypt import hashpw, checkpw, gensalt
import uuid
import time
import random

permission_levels = {
    "admin": 1,
    "therapist": 2,
    "user": 3
}


class Account():
    def __init__(self, id=None) -> None:
        self.valid = id and True or False
        self.session_token = None
        self.username = None

    def account_exists(self, username: str, phone: int) -> bool:
        # checks if any of the details are already part of an account
        conn = sqlite3.connect("database.db")
        c = conn.cursor()
        c.execute("SELECT * FROM ACCOUNT WHERE username = ?", (username,))
        result = c.fetchone()
        if result:
            conn.close()
            return 1
        c.execute("SELECT * FROM CUSTOMER WHERE PHONENUMBER = ?", (phone,))
        result = c.fetchone()
        conn.close()
        if result:
            return 2

        return False

    def signup(self, username: str, password: str, account_type: str, connection=None) -> bool:
        origin = connection
        if not connection:
            connection = sqlite3.connect("database.db")
        already_exist = connection.execute(
            "SELECT * FROM ACCOUNT WHERE USERNAME = ?", (username,))
        already_exist = already_exist.fetchone()
        while already_exist:
            username = username + str(random.randint(1, 9))
            already_exist = connection.execute(
                "SELECT * FROM ACCOUNT WHERE USERNAME = ?", (username,))
            already_exist = already_exist.fetchone()
        current_date_time = time.strftime(
            "%Y-%m-%d %H:%M:%S", time.localtime())
        permission_level = permission_levels[account_type]
        hashed_password = hashpw(password.encode(), gensalt()).decode()
        connection.execute("INSERT INTO ACCOUNT (USERNAME, PASSWORD, CREATIONDATE, PERMISSIONLEVEL, ACCOUNTTYPE, SESSION_TOKEN) \
                   VALUES (?, ?, ?, ?, ?, '')", (username, hashed_password, current_date_time, permission_level, account_type))
        connection.commit()
        account_id = connection.execute(
            f"SELECT * FROM ACCOUNT WHERE PASSWORD = ?", (hashed_password, ))
        account_id = account_id.fetchone()
        if not origin:
            connection.close()
        return (True, account_id)

    def login(self, username: str, password: str) -> bool:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT * FROM ACCOUNT WHERE USERNAME = ?", (self.username, ))
        result = cursor.fetchone()
        if result:
            if checkpw(password.encode(), result[2].encode()):
                self.valid = True
                return True
        return False

    def get_session_token(self) -> str:
        if self.session_token == None:
            self.session_token = str(uuid.uuid4())
            connection = sqlite3.connect("database.db")
            cursor = connection.cursor()
            cursor.execute("UPDATE ACCOUNT SET SESSION_TOKEN = ? WHERE USERNAME = ?",
                           (self.session_token, self.username))
            connection.commit()
            connection.close()
        print("get session token", self.session_token)
        return self.session_token

    def set_session_token(self, session_token: str) -> str:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            f"SELECT SESSION_TOKEN FROM ACCOUNT WHERE USERNAME = ?", (self.username,))
        result = cursor.fetchone()
        connection.close()
        if result and result[0] == session_token:
            print("GENERATE NEW SESSION TOKEN")
            new_session_token = self.get_session_token()
            return new_session_token

        return False

    def validate_session_token(self, session_token) -> bool:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute(
            "SELECT SESSION_TOKEN FROM ACCOUNT WHERE USERNAME = ?", (self.username,))
        result = cursor.fetchone()
        connection.close()
        if result and result[0] == session_token:
            return True
        return False
