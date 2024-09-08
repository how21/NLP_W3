from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import random
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Load the dataset
try:
    with open("kata-kata.txt", "r", encoding="utf-8") as file:
        words = [line.strip().lower() for line in file if line.strip()]
        print(f"Dataset loaded successfully with {len(words)} words.")
except FileNotFoundError:
    print("Error: Dataset file not found!")
    words = []

# Function to save user data to file
def save_user(email, password):
    with open('user.txt', 'a') as file:
        file.write(f'{email},{password}\n')

# Function to load users from file
def load_users():
    users = {}
    try:
        with open('users.txt', 'r') as file:
            for line in file:
                email, password = line.strip().split(',')
                users[email] = password
    except FileNotFoundError:
        pass  
    return users


# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        valid = True  # Flag untuk memeriksa apakah semua validasi berhasil

        # Validasi email domain @unair.ac.id
        email_regex = r'^[a-zA-Z0-9._%+-]+@unair\.ac\.id$'
        if not re.match(email_regex, email):
            flash('Email harus menggunakan domain unair.ac.id.')
            valid = False  # Jika email tidak valid, set flag validasi ke False

        # Validasi password
        password_regex = r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$'
        if not re.match(password_regex, password):
            flash("Password harus terdiri dari minimal 8 karakter, dengan setidaknya satu huruf, satu angka, dan satu karakter spesial.")
            valid = False  # Jika password tidak valid, set flag validasi ke False

        # Simpan user ke file jika validasi berhasil
        if valid:
            with open("users.txt", "a") as file:
                file.write(f"{email},{password}\n")
            flash('Akun berhasil dibuat, silakan login.')
            return redirect(url_for('login'))
        else:
            return redirect(url_for('signup'))

    return render_template("signup.html")

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Validasi email domain @unair.ac.id
        email_regex = r'^[a-zA-Z0-9._%+-]+@unair\.ac\.id$'
        if not re.match(email_regex, email):
            flash('Pastikan domain email sudah benar "unair.ac.id"')

        # Muat pengguna dari file dan validasi login
        users = load_users()
        if email in users and users[email] == password:
            flash('Login berhasil!')
            return redirect(url_for('index'))  # Redirect ke index.html setelah login berhasil
        else:
            flash('Email atau password salah.')
            return redirect(url_for('login'))

    return render_template('login.html')

def generate_hint(word):
    
    hint = "^"  

    for letter in word:
        choice = random.choice([0, 1, 2])  
        if choice == 0:
            hint += letter  
        elif choice == 1:
            hint += "."  
        else:
            hint += f"[{letter}{chr(random.randint(97, 122))}]"  

    hint += "$"  

    return hint

def mask_word(word):
    return "_" * len(word)

@app.route('/')
def index():
    session['word'] = random.choice(words)
    session['lives'] = 3
    session['points'] = 0
    session['game_over'] = False
    session['hint'] = generate_hint(session['word'])
    print(f"Starting new game with word: {session['word']}")

    return render_template('index.html', 
                        word_masked=mask_word(session['word']), 
                        lives=session['lives'], 
                        points=session['points'], 
                        hint=session['hint'])

@app.route('/guess', methods=['POST'])
def guess():
    if session.get('game_over', False):
        return jsonify({
            "message": "Game is already over.",
            "lives": session['lives'],
            "points": session['points'],
            "game_over": True,
            "correct_word": session['word']
        })

    regex_pattern = request.form.get('pattern', '').lower()
    print(f"User guessed with pattern: {regex_pattern}")

    if not regex_pattern:
        return jsonify({"error": "No pattern provided."})

    try:
        regex = re.compile(regex_pattern)
    except re.error as e:
        return jsonify({"error": f"Invalid regex pattern: {str(e)}"})

    if regex.fullmatch(session['word']):
        # benar, menambahkan poin
        session['points'] += 1
        session['word'] = random.choice(words)
        session['hint'] = generate_hint(session['word'])
        response = {
            "message": "Widih benerr!",
            "points": session['points'],
            "word_masked": mask_word(session['word']),
            "lives": session['lives'],
            "hint": session['hint']
        }
        print(f"Widih benerr!! Moving to next word: {session['word']}")
    else:
        # mengurangi nyawa
        session['lives'] -= 1
        response = {
            "message": "Salah broo",
            "lives": session['lives'],
            "points": session['points'],
            "hint": session['hint'],
            "correct_word": session['word']  
        }
        print(f"Incorrect guess. Lives remaining: {session['lives']}")

        # Cek nyawa
        if session['lives'] <= 0:
            session['game_over'] = True
            response["message"] = "Maaf kamu kalah,"
            response["game_over"] = True

    return jsonify(response)

@app.route('/restart', methods=['POST'])
def restart():
    # Ulang game
    session['word'] = random.choice(words)
    session['lives'] = 3
    session['points'] = 0
    session['game_over'] = False
    session['hint'] = generate_hint(session['word'])
    print(f"Game restarted with new word: {session['word']}")

    return jsonify({
        "word_masked": mask_word(session['word']),
        "lives": session['lives'],
        "points": session['points'],
        "hint": session['hint']
    })

@app.route('/coba')
def coba():
    return render_template('coba.html')

if __name__ == "__main__":
    app.run(debug=True)
