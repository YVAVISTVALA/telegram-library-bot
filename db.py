import psycopg2
from config import DB_CONFIG

def conn():
    return psycopg2.connect(**DB_CONFIG)

def ensure_schema():
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    title TEXT,
                    topic TEXT,
                    message_id BIGINT UNIQUE
                )
                """
            )

def search_books(q):
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(
                """
                SELECT title, topic, message_id
                FROM books
                WHERE title ILIKE %s OR topic ILIKE %s
                LIMIT 5
                """,
                (f"%{q}%", f"%{q}%")
            )
            return cur.fetchall()

def upsert_book(title, topic, message_id):
    with conn() as c:
        with c.cursor() as cur:
            cur.execute(
                """
                INSERT INTO books (title, topic, message_id)
                VALUES (%s, %s, %s)
                ON CONFLICT (message_id)
                DO UPDATE SET title = EXCLUDED.title, topic = EXCLUDED.topic
                """,
                (title, topic, message_id)
            )
