from flask import Flask, render_template, request
import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
import bcrypt
import datetime

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

conn = create_db_connection()

def create_user_table():
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                first_name VACHAR(255) NOT NULL,
                last_name VARCHAR(255) NOT NULL,
                birthday DATE NOT NULL,
                age INT NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
    except Error as e:
        print(f"Error creating table: {e}")

@app.route('/')
def home():
    return render_template('Main Menu/home.html')

@app.route('/login')
def login():
    email = request.args.get('email')
    password = request.args.get('password')
    
    cursour = conn.cursor()
    cursour.execute("SELECT password FROM users WHERE email = %s", (email,))
    result = cursour.fetchone()
    cursour.close()
    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        return "Login successful"
    else:
        return "Invalid email or password", 401
    
    return render_template('Login/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    email = request.form.get('email')
    if not email.endswith('@osloskolen.no'):
        return "Invalid email domain", 400
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()
    if result:
        return "User already exists", 400
    password = request.form.get('password')
    comfirm_password = request.form.get('comfirm-password')
    if comfirm_password != password:
        return "Passwords do not match", 400
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    birthday = request.form.get('birthday')
    age = datetime.datetime.now().year - datetime.datetime.strptime(birthday, '%Y-%m-%d').year

    cursor.execute("""
        INSERT INTO users (email, password, first_name, last_name, birthday, age)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (email, hashed_password, first_name, last_name, birthday, age))
    conn.commit()
    cursor.close()

    return render_template('Register/register.html')



if __name__ == '__main__':
    app.run(debug=True)
    port = int(os.environ.get('PORT', 4000))
    app.run(host='0.0.0.0', port=port)