import json
import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
CORS(app)

# Файлы базы данных
CHAT_FILE = 'chat.json'
USERS_FILE = 'users.json'

def load_db(file):
    if not os.path.exists(file) or os.path.getsize(file) == 0: 
        return {} if file == USERS_FILE else []
    try:
        with open(file, 'r', encoding='utf-8') as f: 
            return json.load(f)
    except: 
        return {} if file == USERS_FILE else []

def save_db(file, data):
    with open(file, 'w', encoding='utf-8') as f: 
        json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index(): 
    return render_template_string(HTML_CODE)

@app.route('/auth', methods=['POST'])
def auth():
    try:
        data = request.json
        u, p = data.get('user', '').strip(), data.get('pass', '').strip()
        users = load_db(USERS_FILE)
        
        if data.get('action') == 'reg':
            if u in users: 
                return jsonify({"status": "error", "msg": "Ник занят, бро!"})
            users[u] = p
            save_db(USERS_FILE, users)
            return jsonify({"status": "ok"})
        else:
            if users.get(u) == p: 
                return jsonify({"status": "ok"})
            return jsonify({"status": "error", "msg": "Неверно!"})
    except: 
        return jsonify({"status": "error", "msg": "Сервер упал, сорян"})

@app.route('/send', methods=['POST'])
def send():
    try:
        history = load_db(CHAT_FILE)
        history.append(request.json)
        save_db(CHAT_FILE, history)
        return jsonify({"status": "ok"})
    except: 
        return jsonify({"status": "error"})

@app.route('/get')
def get(): 
    return jsonify(load_db(CHAT_FILE))

# --- ВЕСЬ HTML, CSS И JS В ОДНОЙ ПЕРЕМЕННОЙ ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Gaph Chat | Hanif Edition</title>
    
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    
    <style>
        body { 
            background: #0f0f0f; 
            color: #e0e0e0; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            min-height: 100vh; 
            margin: 0; 
        }
        #auth-screen, #chat-screen { 
            padding: 25px; 
            width: 100%; 
            max-width: 380px; 
            background: #181818; 
            border-radius: 12px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.8); 
            border: 1px solid #333;
        }
        h2 { text-align: center; color: #007bff; margin-bottom: 20px; }
        #chat-box { 
            height: 60vh; 
            border: 1px solid #333; 
            overflow-y: auto; 
            padding: 10px; 
            margin-bottom: 15px; 
            background: #111; 
            border-radius: 8px; 
            display: flex;
            flex-direction: column;
        }
        .msg { 
            margin: 4px 0; 
            padding: 10px; 
            border-radius: 8px; 
            background: #252525; 
            word-wrap: break-word;
            border-left: 3px solid #007bff;
        }
        .msg b { color: #007bff; }
        input { 
            display: block; 
            width: 100%; 
            padding: 12px; 
            margin: 10px 0; 
            border-radius: 6px; 
            box-sizing: border-box; 
            border: 1px solid #444; 
            background: #222; 
            color: #fff; 
            outline: none;
        }
        input:focus { border-color: #007bff; }
        button { 
            padding: 12px; 
            width: 100%; 
            border-radius: 6px; 
            background: #007bff; 
            color: white; 
            border: none; 
            margin-top: 8px; 
            cursor: pointer; 
            font-weight: bold; 
            text-transform: uppercase;
            transition: 0.2s;
        }
        button:hover { background: #0056b3; transform:
