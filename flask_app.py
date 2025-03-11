from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Hash function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database setup
def get_db_connection():
    conn = sqlite3.connect("segrebot_database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/segrebot/')
def home():
    print(session)
    if 'username' in session:
        
        with sqlite3.connect("segrebot_database.db") as conn:
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
    with sqlite3.connect("segrebot_database.db") as conn:
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
        
        with sqlite3.connect("segrebot_database.db") as conn:
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
        
        with sqlite3.connect("segrebot_database.db") as conn:
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
def get_db_connection():
    conn = sqlite3.connect("segrebot_database.db")
    conn.row_factory = sqlite3.Row
    return conn
@app.route("/segrebot/rewards", methods=["POST"])
def add_reward():
    data = request.get_json()
    code = data.get("code")
    points = data.get("points")
    
    if not code or not isinstance(points, int):
        return jsonify({"error": "Invalid input"}), 400
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO rewards (code, points, redeemer) VALUES (?, ?, NULL)", (code, points))
        conn.commit()
        conn.close()
        return jsonify({"message": "Reward added successfully"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Code already exists"}), 400
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
