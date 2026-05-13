import os
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    # Просто текст, чтобы ты увидел, что сайт ВКЛЮЧИЛСЯ
    return """
    <body style="background: #1a1a1a; color: #00ff00; font-family: monospace; text-align: center; padding-top: 50px;">
        <h1>СЕРВЕР ХАНИФА ОЖИЛ! 🚀</h1>
        <p>Если ты видишь это, значит Render больше не выдает 'Отказано'.</p>
        <hr style="width: 300px; border-color: #333;">
        <p><a href="/check_db" style="color: #00ff00;">Нажми сюда, чтобы проверить базу</a></p>
    </body>
    """

@app.route('/check_db')
def check_db():
    # Пробуем достучаться до базы, но если не выйдет — сайт НЕ УПАДЕТ
    db_url = os.environ.get("DATABASE_URL")
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        return jsonify({"status": "Success", "message": "База данных пожала нам руку! 🤝"})
    except Exception as e:
        return jsonify({"status": "Error", "message": f"Мелстрой всё еще против: {str(e)}"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
