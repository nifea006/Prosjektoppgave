from flask import Flask, render_template, request, redirect, session, send_from_directory
import mysql.connector
import os
from dotenv import load_dotenv
import bcrypt
import datetime
from werkzeug.utils import secure_filename

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or "dev123"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

DB_host = os.getenv('DB_host')
DB_user = os.getenv('DB_user')
DB_password = os.getenv('DB_password')
DB_database = os.getenv('DB_database')

# ----- Fill out -----

def create_db_connection():
    return mysql.connector.connect(
        host = DB_host or "localhost",
        user = DB_user or "your_user",
        password = DB_password or "your_password",
        database = DB_database or "your_database"
    )

def initialize_database():
    conn = create_db_connection()
    cursor = conn.cursor()

    # users
    cursor.execute("""
         CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            birthday DATE NOT NULL,
            age INT NOT NULL 
            profile_pic VARCHAR(255) DEFAULT 'default.png'
        )
    """)

    # posts
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # comments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # likes
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            post_id INT NOT NULL,
            user_id INT NOT NULL,
            UNIQUE(post_id, user_id),
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # friends
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            friend_id INT NOT NULL,
            UNIQUE(user_id, friend_id),
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (friend_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('Login/login.html')

    email = request.form.get('email')
    password = request.form.get('password')

    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return render_template('Login/login.html', error="Ugyldig e-post eller passord.")

    user_id, hashed_pw = user

    if bcrypt.checkpw(password.encode(), hashed_pw.encode()):
        session['user_id'] = user_id
        session['email'] = email
        return redirect('/')
    else:
        return render_template('Login/login.html', error="Ugyldig e-post eller passord.")


# register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('Register/register.html')

    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')
    password = request.form.get('password')
    confirm = request.form.get('confirm-password')
    birthday = request.form.get('birthday')

    if password != confirm:
        return render_template("Register/register.html", error="Passordene stemmer ikke.")

    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    birthdate = datetime.datetime.strptime(birthday, "%Y-%m-%d")
    age = datetime.datetime.now().year - birthdate.year

    conn = create_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    if cursor.fetchone():
        return render_template("Register/register.html", error="E-post allerede registrert.")

    cursor.execute("""
        INSERT INTO users (email, password, first_name, last_name, birthday, age)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (email, hashed, first_name, last_name, birthday, age))

    conn.commit()
    cursor.close()
    return redirect('/login')


# home
@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")

    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            posts.*, 
            users.first_name, 
            users.last_name, 
            users.profile_pic,
            (SELECT COUNT(*) FROM likes WHERE likes.post_id = posts.id) AS like_count,
            (SELECT COUNT(*) FROM comments WHERE comments.post_id = posts.id) AS comment_count
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)

    posts = cursor.fetchall()

    for post in posts:
        cursor.execute("""
            SELECT comments.content, users.first_name, users.last_name
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE post_id = %s
            ORDER BY comments.created_at ASC
        """, (post["id"],))

        post["comments"] = cursor.fetchall()

    return render_template("Main/index.html", posts=posts)


# create post
@app.route("/post", methods=["POST"])
def create_post():
    if "user_id" not in session:
        return redirect("/login")

    content = request.form.get("content")

    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO posts (user_id, content) VALUES (%s, %s)", 
                   (session["user_id"], content))
    conn.commit()
    cursor.close()
    return redirect("/")


# add comment
@app.route("/comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):
    if "user_id" not in session:
        return redirect("/login")

    content = request.form.get("comment")

    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (post_id, user_id, content) VALUES (%s, %s, %s)",
                   (post_id, session["user_id"], content))
    conn.commit()
    cursor.close()
    return redirect("/")


# like
@app.route("/like/<int:post_id>")
def like(post_id):
    if "user_id" not in session:
        return redirect("/login")

    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO likes (post_id, user_id) VALUES (%s, %s)",
                       (post_id, session["user_id"]))
        conn.commit()
    except:
        pass  # ignore if already liked

    cursor.close()
    return redirect("/")


# friends
@app.route("/friends")
def friends():
    if "user_id" not in session:
        return redirect("/login")

    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT id, first_name, last_name, profile_pic FROM users")

    users = cursor.fetchall()
    cursor.close()
    return render_template("Friends/friends.html", users=users)


# add friends
@app.route("/add_friend/<int:user_id>")
def add_friend(user_id):
    conn = create_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO friends (user_id, friend_id) VALUES (%s, %s)",
                       (session["user_id"], user_id))
        conn.commit()
    except:
        pass

    cursor.close()
    return redirect("/friends")


# profile
@app.route("/profile")
def profile():
    if 'user_id' not in session:
        return redirect('/login')

    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM users WHERE id=%s", (session["user_id"],))
    user = cursor.fetchone()

    cursor.close()
    return render_template("User/profile.html", user=user)


# upload picture
@app.route("/upload_picture", methods=["POST"])
def upload_picture():
    if "user_id" not in session:
        return redirect("/login")

    file = request.files["profile_pic"]
    filename = secure_filename(file.filename)
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(path)

    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET profile_pic=%s WHERE id=%s", (filename, session["user_id"]))
    conn.commit()
    cursor.close()

    return redirect("/profile")


# meassages
@app.route("/messages")
def messages():
    if "user_id" not in session:
        return redirect("/login")

    conn = create_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT messages.*, users.first_name, users.last_name
        FROM messages
        JOIN users ON messages.sender_id = users.id
        WHERE receiver_id = %s
        ORDER BY created_at DESC
    """, (session["user_id"],))

    inbox = cursor.fetchall()
    cursor.close()

    return render_template("Messages/messages.html", inbox=inbox)


# send messages
@app.route("/send_message/<int:user_id>", methods=["POST"])
def send_message(user_id):
    content = request.form.get("content")

    conn = create_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (sender_id, receiver_id, content)
        VALUES (%s, %s, %s)
    """, (session["user_id"], user_id, content))

    conn.commit()
    cursor.close()
    return redirect("/messages")


# settings
@app.route("/settings")
def settings():
    return render_template("Settings/settings.html")


# logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == '__main__':
    app.run(debug=True)