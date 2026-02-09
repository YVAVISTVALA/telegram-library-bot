import psycopg2
from config import DB_CONFIG

def conn():
    return psycopg2.connect(**DB_CONFIG)

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
