from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

DB_host = os.getenv('DB_host')
DB_user = os.getenv('DB_user')
DB_password = os.getenv('DB_password')
DB_database = os.getenv('DB_name')

def create_db_connection():
    return mysql.connector.connect(
        host=DB_host,
        user=DB_user,
        password=DB_password,
        database=DB_database
    )

@app.route('/')
def home():
    return render_template('Main Menu/home.html')

@app.route('/login')
def login():
    return render_template('Login/login.html')



if __name__ == '__main__':
    app.run(debug=True)