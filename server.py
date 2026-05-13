import os
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from waitress import serve
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

# --- ПОДКЛЮЧЕНИЕ SUPABASE ---
# Эти переменные мы добавим в настройки Render
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(URL, KEY)

@app.route('/')
def index(): 
    return render_template_string(HTML_CODE)

@app.route('/auth', methods=['POST'])
def auth():
    try:
        data = request.json
        u, p = data.get('user', '').strip(), data.get('pass', '').strip()
        
        # Ищем юзера в таблице 'users'
        res = supabase.table("users").select("*").eq("username", u).execute()
        user_data = res.data

        if data.get('action') == 'reg':
            if user_data: 
                return jsonify({"status": "error", "msg": "Ник занят, бро!"})
            # Регаем нового
            supabase.table("users").insert({"username": u, "password": p}).execute()
            return jsonify({"status": "ok"})
        else:
            # Проверяем вход
            if user_data and user_data[0]['password'] == p: 
                return jsonify({"status": "ok"})
            return jsonify({"status": "error", "msg": "Неверно!"})
    except Exception as e: 
        print(f"Ошибка базы: {e}")
        return jsonify({"status": "error", "msg": "Сервер упал, сорян"})

@app.route('/send', methods=['POST'])
def send():
    try:
        data = request.json
        # Сохраняем в таблицу 'messages'
        supabase.table("messages").insert({
            "username": data.get('user'), 
            "content": data.get('text')
        }).execute()
        return jsonify({"status": "ok"})
    except Exception as e:
        print(f"Ошибка отправки: {e}")
        return jsonify({"status": "error"})

@app.route('/get')
def get(): 
    try:
        # Берем последние 50 сообщений
        res = supabase.table("messages").select("*").order("created_at", desc=False).limit(50).execute()
        # Переделываем формат под твой фронтенд (content -> text, username -> user)
        history = [{"user": m['username'], "text": m['content']} for m in res.data]
        return jsonify(history)
    except:
        return jsonify([])

# --- ТВОЙ HTML ОСТАЛСЯ БЕЗ ИЗМЕНЕНИЙ ---
HTML_CODE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Gaph Chat | Hanif Edition</title>
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
    <style>
        body { background: #0f0f0f; color: #e0e0e0; font-family: sans-serif; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; }
        #auth-screen, #chat-screen { padding: 25px; width: 100%; max-width: 380px; background: #181818; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.8); border: 1px solid #333; }
        h2 { text-align: center; color: #007bff; }
        #chat-box { height: 55vh; border: 1px solid #333; overflow-y: auto; padding: 10px; margin-bottom: 15px; background: #111; border-radius: 8px; }
        .msg { margin: 8px 0; padding: 10px; border-radius: 8px; background: #252525; border-left: 3px solid #007bff; }
        input { display: block; width: 100%; padding: 12px; margin: 10px 0; border-radius: 6px; box-sizing: border-box; border: 1px solid #444; background: #222; color: #fff; }
        button { padding: 12px; width: 100%; border-radius: 6px; background: #007bff; color: white; border: none; margin-top: 8px; cursor: pointer; font-weight: bold; }
        button:hover { background: #0056b3; }
        .captcha-container { margin: 20px 0; display: flex; justify-content: center; }
    </style>
</head>
<body>
    <div id="auth-screen">
        <h2>GAPH CHAT</h2>
        <input id="u" placeholder="Никнейм">
        <input id="p" type="password" placeholder="Пароль">
        <div class="captcha-container">
            <div class="g-recaptcha" data-sitekey="6LdrZegsAAAAAKnakLUjs64D_rwf0DCv6kMnrv8C" data-theme="dark"></div>
        </div>
        <button onclick="go('login')">Войти</button>
        <button onclick="go('reg')" style="background:#218838;">Регистрация</button>
    </div>

    <div id="chat-screen" style="display:none;">
        <h2>ОБЩИЙ ЧАТ</h2>
        <div id="chat-box"></div>
        <div style="display:flex; gap: 5px;">
            <input id="msg" placeholder="Сообщение..." onkeypress="if(event.keyCode==13) send()">
            <button onclick="send()" style="width: auto;">➡️</button>
        </div>
        <button onclick="logout()" style="background:#c82333; margin-top: 15px;">Выйти</button>
    </div>

    <script>
        async function fetchSafe(url, options) {
            let res = await fetch(url, options);
            return await res.json();
        }

        function formatContent(text) {
            const isImg = /\.(jpg|jpeg|png|gif|webp)$/i.test(text);
            if (isImg) return `<br><img src="${text}" style="max-width: 100%; border-radius: 8px;">`;
            return text;
        }

        if (sessionStorage.getItem('nick')) showChat();

        async function go(action) {
            let v = grecaptcha.getResponse();
            if(v.length == 0) { alert("Капчу пройди!"); return; }
            let u = document.getElementById('u').value.trim();
            let p = document.getElementById('p').value.trim();
            if(!u || !p) return;

            let data = await fetchSafe('/auth', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({action: action, user: u, pass: p})
            });
            if (data.status === 'ok') {
                sessionStorage.setItem('nick', u);
                showChat();
            } else { alert(data.msg); grecaptcha.reset(); }
        }

        function showChat() {
            document.getElementById('auth-screen').style.display = 'none';
            document.getElementById('chat-screen').style.display = 'block';
            update(); setInterval(update, 3000);
        }

        function logout() { sessionStorage.removeItem('nick'); location.reload(); }

        async function send() {
            let input = document.getElementById('msg');
            let txt = input.value.trim();
            if(!txt) return;
            await fetchSafe('/send', { 
                method:'POST', 
                headers:{'Content-Type':'application/json'}, 
                body:JSON.stringify({user: sessionStorage.getItem('nick'), text: txt}) 
            });
            input.value = ''; update();
        }

        async function update() {
            let data = await fetchSafe('/get');
            const box = document.getElementById('chat-box');
            box.innerHTML = data.map(m => `<div class="msg"><b>${m.user}</b>: ${formatContent(m.text)}</div>`).join('');
            box.scrollTop = box.scrollHeight;
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)
