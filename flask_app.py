from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Hash function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database setup
def init_db():
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            grade_section TEXT NOT NULL,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL,
                            points INTEGER DEFAULT 0)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS rewards (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            code TEXT UNIQUE NOT NULL,
                            points INTEGER NOT NULL,
                            is_redeemed INTEGER DEFAULT 0)''')
        conn.commit()

init_db()

@app.route('/segrebot/')
def home():
    print(session)
    if 'username' in session:
        
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT points FROM users WHERE username=?", (session['username'],))
            points = cursor.fetchone()[0]
        return render_template('segrebot_dashboard.html', username=session['username'], points=points)
    return redirect(url_for('login'))

@app.route('/segrebot/redeem', methods=['POST'])
def redeem():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    code = request.form['code']
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT points, is_redeemed FROM rewards WHERE code=?", (code,))
        reward = cursor.fetchone()
        
        if reward and reward[1] == 0:  # Code exists and is not redeemed
            cursor.execute("UPDATE users SET points = points + ? WHERE username=?", (reward[0], session['username']))
            cursor.execute("UPDATE rewards SET is_redeemed=1 WHERE code=?", (code,))
            conn.commit()
            flash("Reward redeemed successfully!", "success")
        else:
            flash("Invalid or already redeemed code.", "error")
    
    return redirect(url_for('home'))

@app.route('/segrebot/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        grade_section = request.form['grade_section']
        username = request.form['username']
        password = hash_password(request.form['password'])  # Hash password
        
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (name, grade_section, username, password, points) VALUES (?, ?, ?, ?, 0)", 
                               (name, grade_section, username, password))
                conn.commit()
                flash("Signup successful! Please login.", "success")
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash("Username already exists. Try a different one.", "error")
    
    return render_template('segrebot_signup.html')

@app.route('/segrebot/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = hash_password(request.form['password'])  # Hash input password
        
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            user = cursor.fetchone()
            print(user)
            if user:
                session['username'] = username
                
                return redirect(url_for('home'))
            else:
                # flash("Invalid credentials.", "error")
                return render_template('segrebot_login.html', error = "Invalid credentials.")
    
    return render_template('segrebot_login.html')

@app.route('/segrebot/logout')
def logout():
    session.pop('username', None)
    flash("Logged out successfully.", "success")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
