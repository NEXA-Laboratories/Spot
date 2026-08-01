import sqlite3
import os

class LocalMemory:
    def __init__(self, db_path="data/memory.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # Explicit long-term facts
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS long_term_facts (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
            """)
            # Short-term conversational log
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS conversation_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_fact(self, key: str, value: str):
        with self.conn:
            self.conn.execute(
                "INSERT OR REPLACE INTO long_term_facts (key, value) VALUES (?, ?)",
                (key.lower().strip(), value.strip())
            )

    def get_fact(self, key: str) -> str:
        cursor = self.conn.cursor()
        cursor.execute("SELECT value FROM long_term_facts WHERE key = ?", (key.lower().strip(),))
        row = cursor.fetchone()
        return row[0] if row else None

    def add_history(self, role: str, content: str):
        with self.conn:
            self.conn.execute(
                "INSERT INTO conversation_history (role, content) VALUES (?, ?)",
                (role, content)
            )

    def get_recent_history(self, limit=5):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content FROM conversation_history ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        rows = cursor.fetchall()
        return list(reversed(rows))

    def clear_short_term(self):
        with self.conn:
            self.conn.execute("DELETE FROM conversation_history")