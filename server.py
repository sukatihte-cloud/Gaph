import os
import psycopg2

# Берем данные из Environment
DB_PASS = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")

def get_db():
    return psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password=DB_PASS,
        host=DB_HOST,
        port="5432"
    )

# ... остальной код (index, send, get) такой же
