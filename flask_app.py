from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import sqlite3
import hashlib

app = Flask(__name__)
app.secret_key = 'S3Gr3b0t2025!'

extension = "./"

# Hash function for passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Database setup
def get_db_connection():
    conn = sqlite3.connect(f"{extension}segrebot_database.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/segrebot/')
def home():
    print(session)
    if 'username' in session:
        
        with sqlite3.connect(f"{extension}segrebot_database.db") as conn:
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
    name = request.form['name']
    
    with sqlite3.connect(f"{extension}segrebot_database.db") as conn:
        cursor = conn.cursor()
        
        # Check if the reward exists and is not redeemed
        cursor.execute("SELECT points, redeemer FROM rewards WHERE code=?", (code,))
        reward = cursor.fetchone()
        
        if reward and (reward[1] is None or reward[1] == ''):  # Code exists and is not redeemed
            cursor.execute("UPDATE users SET points = points + ? WHERE username=?", (reward[0], session['username']))
            cursor.execute("UPDATE rewards SET redeemer = ? WHERE code=?", (session['username'], code))
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
        
        with sqlite3.connect(f"{extension}segrebot_database.db") as conn:
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
        
        with sqlite3.connect(f"{extension}segrebot_database.db") as conn:
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


@app.route("/segrebot/admin/")
def segrebot_admin_index():
    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    return render_template("segrebot_admin.html", users=users)

@app.route("/segrebot/admin/rewards")
def segrebot_admin_rewards():
    conn = get_db_connection()
    rewards = conn.execute("SELECT * FROM rewards").fetchall()
    conn.close()
    return render_template("segrebot_admin_rewards.html", rewards=rewards)

@app.route("/segrebot/admin/delete_user/<int:id>")
def segrebot_admin_delete_user(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("User deleted successfully!", "danger")
    return redirect(url_for("segrebot_admin_index"))

@app.route("/segrebot/admin/update_user", methods=["POST"])
def segrebot_admin_update_user():
    id = request.form["id"]
    name = request.form["name"]
    grade_section = request.form["grade_section"]
    username = request.form["username"]
    points = request.form["points"]
    
    conn = get_db_connection()
    conn.execute("UPDATE users SET name = ?, grade_section = ?, username = ?, points = ? WHERE id = ?", 
                 (name, grade_section, username, points, id))
    conn.commit()
    conn.close()
    flash("User updated successfully!", "info")
    return redirect(url_for("segrebot_admin_index"))
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=8000)
