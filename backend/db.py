import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="ojas@new2006",
        database="lost_found",
        autocommit=True
    )