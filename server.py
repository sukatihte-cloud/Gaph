import os
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, render_template_string, request, jsonify
from flask_cors import CORS
from waitress import serve

app = Flask(__name__)
CORS(app)

DB_URL = os.environ.get("DATABASE_URL")

def get_db():
    return psycopg2.connect(DB_URL, cursor_factory=RealDictCursor)

@app.route('/')
def index():
    return "<h1>Чат Ханифа живет тут!</h1><p>Если видишь это, значит сервер работает.</p>"

@app.route('/send', methods=['POST'])
def send():
    data = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (username, content) VALUES (%s, %s)", (data['user'], data['text']))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"status": "ok"})

@app.route('/get')
def get():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT username as user, content as text FROM messages ORDER BY created_at DESC LIMIT 50")
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(messages)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    serve(app, host='0.0.0.0', port=port)
