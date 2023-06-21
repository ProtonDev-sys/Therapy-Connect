from datetime import date 
import sqlite3

class Therapist():
    def __init__(self, id:int) -> None:
        connection = sqlite3.connect("database.db")
        cursor = connection.execute(f"SELECT * from THERAPIST where THERAPISTID = {id}")
        therapist = cursor.fetchone()
        connection.close()
        if therapist is None:
            print("Therapist ID not found.")
            return 
        self.ID = therapist[0]
        self.ACCOUNTID = therapist[1]
        self.name = therapist[2]
        self.speciality = therapist[3]
        self.date_started = therapist[4]
        self.email = therapist[5]
        self.phone = therapist[6]
        self.location = therapist[7]
