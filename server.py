import json
import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
CORS(app)

CHAT_FILE = 'chat.json'
USERS_FILE = 'users.json'

def load_db(file):
    if not os.path.exists(file) or os.path.getsize(file) == 0: 
        return {} if file == USERS_FILE else []
    try:
        with open(file, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {} if file == USERS_FILE else []

def save_db(file, data):
    with open(file, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

@app.route('/')
def index(): return render_template_string(HTML_CODE)

@app.route('/auth', methods=['POST'])
def auth():
    try:
        data = request.json
        u, p = data.get('user', '').strip(), data.get('pass', '').strip()
        users = load_db(USERS_FILE)
        if data.get('action') == 'reg':
            if u in users: return jsonify({"status": "error", "msg": "Ник занят, бро!"})
            users[u] = p
            save_db(USERS_FILE, users)
            return jsonify({"status": "ok"})
        else:
            if users.get(u) == p: return jsonify({"status": "ok"})
            return jsonify({"status": "error", "msg": "Неверно!"})
    except: return jsonify({"status": "error", "msg": "Сервер упал, сорян"})

@app.route('/send', methods=['POST'])
def send():
    try:
        history = load_db(CHAT_FILE)
        history.append(request.json)
        save_db(CHAT_FILE, history)
        return jsonify({"status": "ok"})
    except: return jsonify({"status": "error"})

@app.route('/get')
def get(): return jsonify(load_db(CHAT_FILE))

HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { background: #121212; color: white; font-family: sans-serif; }
        #auth-screen, #chat-screen { padding: 20px; }
        #chat-box { height: 50vh; border: 1px solid #444; overflow-y: scroll; padding: 10px; margin-bottom: 10px; background: #222; }
        .msg { margin: 5px; padding: 8px; border-radius: 10px; background: #333; }
        input { display: block; width: 100%; padding: 12px; margin: 5px 0; border-radius: 5px; box-sizing: border-box; border: none; }
        button { padding: 12px; width: 100%; border-radius: 5px; background: #007bff; color: white; border: none; margin-top: 5px; }
    </style>
</head>
<body>
    <div id="auth-screen">
        <h2>Чат Ханифа</h2>
        <input id="u" placeholder="Ник">
        <input id="p" type="password" placeholder="Пароль">
        <button onclick="go('login')">Войти</button>
        <button onclick="go('reg')" style="background:#28a745;">Регистрация</button>
    </div>
    <div id="chat-screen" style="display:none;">
        <div id="chat-box"></div>
        <input id="msg" placeholder="Сообщение...">
        <button onclick="send()">Отправить</button>
        <button onclick="logout()" style="background:#dc3545;">Выйти</button>
    </div>
    <script>
        async function fetchSafe(url, options) {
            try {
                let res = await fetch(url, options);
                return await res.json();
            } catch(e) { alert("Лаги!"); throw e; }
        }

        // Функция обработки медиа
        function formatContent(text) {
            const isImage = /\.(jpg|jpeg|png|gif|webp)$/i.test(text);
            const isVideo = /\.(mp4|webm)$/i.test(text);

            if (isImage) {
                return `<br><img src="${text}" style="max-width: 100%; border-radius: 10px; margin-top: 5px;">`;
            } else if (isVideo) {
                return `<br><video src="${text}" controls style="max-width: 100%; border-radius: 10px; margin-top: 5px;"></video>`;
            }
            return text;
        }

        if (sessionStorage.getItem('nick')) showChat();

        async function go(action) {
            let u = document.getElementById('u').value;
            let p = document.getElementById('p').value;
            let data = await fetchSafe('/auth', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: action, user: u, pass: p})
            });
            if (data.status === 'ok') {
                sessionStorage.setItem('nick', u);
                showChat();
            } else { alert(data.msg); }
        }

        function showChat() {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('chat-screen').style.display = 'block';
            update();
            setInterval(update, 3000);
        }

        function logout() { sessionStorage.removeItem('nick'); location.reload(); }

        async function send() {
            let txt = document.getElementById('msg').value;
            if(!txt) return;
            await fetchSafe('/send', { 
                method:'POST', 
                headers:{'Content-Type':'application/json'}, 
                body:JSON.stringify({user: sessionStorage.getItem('nick'), text: txt}) 
            });
            document.getElementById('msg').value = ''; update();
        }

        async function update() {
            let data = await fetchSafe('/get');
            document.getElementById('chat-box').innerHTML = data.map(m => 
                `<div class="msg"><b>${m.user}</b>: ${formatContent(m.text)}</div>`
            ).join('');
            document.getElementById('chat-box').scrollTop = document.getElementById('chat-box').scrollHeight;
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("Чат запущен на http://localhost:5000")
    serve(app, host='0.0.0.0', port=5000)
