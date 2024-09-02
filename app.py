from flask import Flask, render_template, request, jsonify, session
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
            "message": "Correct!",
            "points": session['points'],
            "word_masked": mask_word(session['word']),
            "lives": session['lives'],
            "hint": session['hint']
        }
        print(f"Correct! Moving to next word: {session['word']}")
    else:
        # mengurangi nyawa
        session['lives'] -= 1
        response = {
            "message": "Incorrect guess.",
            "lives": session['lives'],
            "points": session['points'],
            "hint": session['hint'],
            "correct_word": session['word']  
        }
        print(f"Incorrect guess. Lives remaining: {session['lives']}")

        # Cek nyawa
        if session['lives'] <= 0:
            session['game_over'] = True
            response["message"] = "Game over!"
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


if __name__ == "__main__":
    app.run(debug=True)
