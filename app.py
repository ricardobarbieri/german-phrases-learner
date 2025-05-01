from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import json
import hashlib
import datetime
import smtplib
from email.mime.text import MIMEText
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

USER_DB = "users.json"
PHRASES_FILE = "phrases.json"
PHRASES_PER_PAGE = 40

def load_users():
    if os.path.exists(USER_DB):
        with open(USER_DB, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB, 'w') as f:
        json.dump(users, f, indent=4)

def load_phrases():
    if os.path.exists(PHRASES_FILE):
        with open(PHRASES_FILE, 'r') as f:
            return json.load(f)
    return []

def load_translations(username):
    file_path = f"translations_{username}.json"
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return {}

def save_translations(username, translations):
    with open(f"translations_{username}.json", 'w') as f:
        json.dump(translations, f, indent=4)

def send_recovery_email(email, password):
    sender = "your_email@example.com"
    msg = MIMEText(f"Your password is: {password}")
    msg['Subject'] = 'Password Recovery'
    msg['From'] = sender
    msg['To'] = email

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender, "your_password")
            server.sendmail(sender, email, msg.as_string())
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

def generate_hash(text):
    return hashlib.sha256(text.encode()).hexdigest()

@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('modes'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_users()
        if username in users and users[username]["password"] == password:
            session['username'] = username
            return redirect(url_for('modes'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        users = load_users()
        if username and password and email:
            if username not in users:
                users[username] = {"password": password, "email": email}
                save_users(users)
                return redirect(url_for('login'))
            return render_template('register.html', error="Username already exists")
        return render_template('register.html', error="All fields are required")
    return render_template('register.html')

@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        users = load_users()
        for username, data in users.items():
            if data['email'] == email:
                if send_recovery_email(email, data['password']):
                    return render_template('forgot.html', message="Password sent to email")
                return render_template('forgot.html', error="Failed to send email")
        return render_template('forgot.html', error="Email not found")
    return render_template('forgot.html')

@app.route('/users')
def users():
    users = load_users()
    return render_template('users.html', users=users)

@app.route('/delete_user/<username>')
def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
    return redirect(url_for('users'))

@app.route('/modes')
def modes():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('modes.html')

@app.route('/start_mode/<mode>/<int:time_limit>')
def start_mode(mode, time_limit):
    if 'username' not in session:
        return redirect(url_for('login'))
    session['mode'] = mode
    session['time_limit'] = time_limit
    session['start_time'] = datetime.datetime.now().timestamp()
    return redirect(url_for('main', page=1))

@app.route('/main/<int:page>')
def main(page):
    if 'username' not in session:
        return redirect(url_for('login'))
    
    phrases = load_phrases()
    total_phrases = len(phrases)
    total_pages = (total_phrases + PHRASES_PER_PAGE - 1) // PHRASES_PER_PAGE
    page = max(1, min(page, total_pages))
    start_idx = (page - 1) * PHRASES_PER_PAGE
    end_idx = min(start_idx + PHRASES_PER_PAGE, total_phrases)
    page_phrases = phrases[start_idx:end_idx]

    left_phrases = page_phrases[:len(page_phrases)//2]
    right_phrases = page_phrases[len(page_phrases)//2:]

    for i, phrase in enumerate(left_phrases, start=start_idx + 1):
        phrase['index'] = i
        phrase['index_str'] = str(i)
    for i, phrase in enumerate(right_phrases, start=start_idx + len(left_phrases) + 1):
        phrase['index'] = i
        phrase['index_str'] = str(i)

    translations = load_translations(session['username'])
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    hash_value = generate_hash(session['username'] + today)[:10]

    return render_template('main.html', left_phrases=left_phrases, right_phrases=right_phrases, page=page, total_pages=total_pages, hash_value=hash_value, translations=translations, username=session['username'])

@app.route('/save_translation', methods=['POST'])
def save_translation():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})
    idx = request.form['index']
    translation = request.form['translation']
    translations = load_translations(session['username'])
    translations[idx] = translation
    save_translations(session['username'], translations)
    return jsonify({'status': 'success'})

@app.route('/log_timeout', methods=['POST'])
def log_timeout():
    if 'username' not in session:
        return jsonify({'status': 'error', 'message': 'Not logged in'})
    data = request.get_json()
    elapsed_time = data['elapsed_time']
    mode = session.get('mode', 'unknown')
    with open('logs.txt', 'a') as f:
        f.write(f"Log: Tempo total decorrido no modo {mode}: {elapsed_time:.2f} segundos\n")
    return jsonify({'status': 'success'})

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('mode', None)
    session.pop('time_limit', None)
    session.pop('start_time', None)
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)