# import mysql.connector

# def get_connection():
#     return mysql.connector.connect(
#         host="localhost",
#         user="root",
#         password="12345678",
#         database="maternal_db"
#     )

import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():

    # LOCAL DATABASE
    if os.getenv("MYSQLHOST") == "" or os.getenv("MYSQLHOST") is None:

        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345678",
            database="maternal_db"
        )

    # RAILWAY DATABASE
    return mysql.connector.connect(
        host=os.getenv("MYSQLHOST"),
        user=os.getenv("MYSQLUSER"),
        password=os.getenv("MYSQLPASSWORD"),
        database=os.getenv("MYSQLDATABASE"),
        port=int(os.getenv("MYSQLPORT"))
    )