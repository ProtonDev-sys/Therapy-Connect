from datetime import date 
import sqlite3

class Customer():
    def __init__(self, id:int) -> None:
        connection = sqlite3.connect("database.db")
        cursor = connection.execute(f"SELECT * from CUSTOMER where CUSTOMERID = {id}")
        therapist = cursor.fetchone()
        connection.close()
        if therapist is None:
            print("Customer ID not found.")
            return 
        self.ID = therapist[0]
        self.ACCOUNTID = therapist[1]
        self.name = therapist[2]
        self.email = therapist[3]
        self.phone = therapist[4]
