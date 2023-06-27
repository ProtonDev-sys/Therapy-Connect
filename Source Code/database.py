import sqlite3
from therapist import Therapist
from customer import Customer
import random 
import datetime 
from account import Account

class Database():
    def __init__(self) -> None:
        self.therapists = []
        self.users = []            
        connection = sqlite3.connect('database.db')
        cursor = connection.cursor()
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='THERAPIST'")
        if cursor.fetchone() is None:
            self.create_database()

    def create_database(self) -> None:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        try:
            connection.execute("CREATE TABLE \"THERAPIST\" ( \
                \"THERAPISTID\"    INTEGER UNIQUE,           \
                \"ACCOUNTID\"    INTEGER,                     \
                \"THERAPISTNAME\"    VARCHAR(40),                    \
                \"THERAPISTSPECIALITY\"    VARCHAR(30),               \
                \"DATE_STARTED\"    DATE,                      \
                \"THERAPISTEMAIL\"    VARCHAR(55),                    \
                \"PHONENUMBER\"    VARCHAR(12),                    \
                \"LOCATION\"    TEXT,                         \
                PRIMARY KEY(\"THERAPISTID\" AUTOINCREMENT)             \
            );")
            connection.commit()
        except sqlite3.Error as e:
            print("Table already exists")
        
        try:
            connection.execute("CREATE TABLE \"APPOINTMENT\" ( \
                \"APPOINTMENTID\"    INTEGER UNIQUE,              \
                \"THERAPISTID\"    INTEGER,                    \
                \"CUSTOMERID\"    INTEGER,                    \
                \"DATE\"    DATE,                            \
                \"PRICE\"    TEXT,                            \
                \"PAID\"    INTEGER,                            \
                \"NOTES\"   VARCHAR(50),                              \
                PRIMARY KEY(\"APPOINTMENTID\" AUTOINCREMENT)    \
            );")
            connection.commit()
        except sqlite3.Error as e:
            print("Table already exists")
        
        try:
            connection.execute("CREATE TABLE \"CUSTOMER\" ( \
                \"CUSTOMERID\"    INTEGER UNIQUE,              \
                \"ACCOUNTID\"    INTEGER,                    \
                \"CUSTOMERNAME\"    VARCHAR(40),                    \
                \"EMAIL\"    VARCHAR(55),                            \
                \"PHONENUMBER\"    VARCHAR(12),                            \
                PRIMARY KEY(\"CUSTOMERID\" AUTOINCREMENT)    \
            );")
            connection.commit()
        except sqlite3.Error as e:
            print("Table already exists")
        
        try:
            connection.execute("CREATE TABLE \"ACCOUNT\" ( \
                \"ACCOUNTID\"	INTEGER UNIQUE,              \
                \"USERNAME\"	VARCHAR(20),                    \
                \"PASSWORD\"	VARCHAR(70),                    \
                \"CREATIONDATE\"	TEXT,                        \
                \"PERMISSIONLEVEL\"	INTEGER,                 \
                \"ACCOUNTTYPE\"	TEXT,                    \
                \"SESSION_TOKEN\"	VARCHAR(40),                        \
                PRIMARY KEY(\"ACCOUNTID\" AUTOINCREMENT)    \
            );")
            connection.commit()
        except sqlite3.Error as e:
            print("Table already exists")
            
        
        first_names = ["Oliver", "Jack", "Harry", "Jacob", "George", "William", "Charlie", "Thomas", "Daniel", "James"]
        last_names = ["Smith", "Jones", "Taylor", "Brown", "Wilson", "Clark", "Lewis", "Robinson", "Walker", "Young"]
        specialities = ["Cognitive Behavioural Therapy", "Interpersonal Therapy", "Family Therapy", "Art Therapy", "Music Therapy", "Psychodynamic Therapy", "Group Therapy", "Mindfulness-based Therapy"]
        locations = ["London", "Manchester", "Birmingham", "Leeds", "Liverpool", "Newcastle", "Bristol", "Sheffield", "Glasgow", "Edinburgh"]
        for i in range(10):
            firstname = random.choice(first_names)
            lastname = random.choice(last_names)
            full_name = firstname + " " + lastname
            email = firstname.lower() + "." + lastname.lower() + str(random.randint(1,9)) + "@therapist.com"
            speciality = random.choice(specialities)
            location = random.choice(locations)
            phonenumber = random.randint(440000000000, 449999999999)
            date_started = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            new_account = Account()
            result = new_account.signup(firstname+lastname, firstname+lastname[0]+str(random.randint(1,9)), "therapist", connection)
            if result[0] == True:
                cursor.execute(f"INSERT INTO THERAPIST (ACCOUNTID, THERAPISTNAME, THERAPISTSPECIALITY, DATE_STARTED, THERAPISTEMAIL, PHONENUMBER, LOCATION) VALUES ({result[1][0]}, \"{full_name}\", \"{speciality}\", \"{date_started}\", \"{email}\", \"{phonenumber}\", \"{location}\");")
        
        connection.commit()
        connection.close()

    def get_therapists(self) -> list[Therapist]:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        therapists = []
        for row in cursor.execute("SELECT * FROM THERAPIST"):
            therapists.append({
                "ID": row[0],
                "ACCOUNTID": row[1],
                "name": row[2],
                "speciality": row[3],
                "date_started": row[4],
                "email": row[5],
                "phone": row[6],
                "location": row[7]
            })
        connection.close()
        return therapists

    def get_therapist_by_id(self, id:int) -> Therapist:
        connection = sqlite3.connect("database.db")
        cursor = connection.execute("SELECT * from THERAPIST where THERAPISTID = ?", (id,))
        therapist = cursor.fetchone()
        connection.close()
        if therapist is None:
            print("Therapist ID not found.")
            return False
        else:
            return Therapist(id)

    def get_therapist_by_account_id(self, id:int) -> Therapist:
        connection = sqlite3.connect("database.db")
        cursor = connection.execute("SELECT * from THERAPIST where ACCOUNTID = ?", (id,))
        therapist = cursor.fetchone()
        connection.close()
        if therapist is None:
            print("Therapist ID not found.")
            return False
        else:
            return Therapist(therapist[0])

    def get_customer_by_id(self, id:int) -> Customer:
        connection = sqlite3.connect("database.db")
        cursor = connection.execute("SELECT * from CUSTOMER where CUSTOMERID = ?", (id,))
        customer = cursor.fetchone()
        connection.close()
        if customer is None:
            print("Customer ID not found.")
            return False
        else:
            return Customer(id)

    def get_customer_by_account_id(self, id:int) -> Customer:
        connection = sqlite3.connect("database.db")
        cursor = connection.execute("SELECT * from CUSTOMER where ACCOUNTID = ?", (id,))
        customer = cursor.fetchone()
        connection.close()
        if customer is None:
            print("Customer ID not found.")
            return False
        else:
            return Customer(customer[0])



    def add_customer_to_database(self, id: int, fullname: str, email:str, phonenumber: int) -> bool:
        connection = sqlite3.connect("database.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO CUSTOMER (ACCOUNTID, CUSTOMERNAME, EMAIL, PHONENUMBER) VALUES (?, ?, ?, ?)", (id, fullname, email, phonenumber))
        connection.commit()
        connection.close()
        return True

    def get_account_by_username(self, username: str) -> str:
        connection = sqlite3.connect("database.db")
        cursor = connection.execute("SELECT * from ACCOUNT where USERNAME = ?", (username,))
        account = cursor.fetchone()
        connection.close()
        if account is None:
            print("Account not found.")
            return False
        else:
            return account

    def get_account_by_id(self, id: int) -> str:
        connection = sqlite3.connect("database.db")
        cursor = connection.execute("SELECT * from ACCOUNT where ACCOUNTID = ?", (id,))
        account = cursor.fetchone()
        connection.close()
        if account is None:
            print("Account not found.")
            return False
        else:
            return account

