import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'zametka.db')

class Storage:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.create_table()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS pages (
            title TEXT PRIMARY KEY,
            content TEXT
        )
        """
        self.conn.execute(query)
        self.conn.commit()

    def save_page(self, title: str, content: str):
        query = """
        INSERT INTO pages (title, content) VALUES (?, ?)
        ON CONFLICT(title) DO UPDATE SET content=excluded.content
        """
        self.conn.execute(query, (title, content))
        self.conn.commit()

    def load_page(self, title: str) -> str:
        query = "SELECT content FROM pages WHERE title = ?"
        cur = self.conn.execute(query, (title,))
        result = cur.fetchone()
        return result[0] if result else ""

    def get_all_titles(self):
        query = "SELECT title FROM pages"
        cur = self.conn.execute(query)
        return [row[0] for row in cur.fetchall()]

    def delete_page(self, title: str):
        query = "DELETE FROM pages WHERE title = ?"
        self.conn.execute(query, (title,))
        self.conn.commit()

    def rename_page(self, old_title: str, new_title: str):
        query = """
        UPDATE pages SET title = ? WHERE title = ?
        """
        self.conn.execute(query, (new_title, old_title))
        self.conn.commit()
