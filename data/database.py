import sqlite3
import os

class Database:
    def __init__(self, db_path="recommendation.db"):
        self.db_path = db_path
        
    def get_connection(self):
        """Returns a connection to the SQLite database with row factory enabled."""
        if self.db_path == ":memory:":
            conn = sqlite3.connect("file::memory:?cache=shared", uri=True)
        else:
            conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        """Creates the necessary tables for the recommendation system."""
        queries = [
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                interests TEXT, -- JSON string
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS content (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT,
                popularity INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS skills (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS user_skills (
                user_id INTEGER,
                skill_id TEXT,
                proficiency INTEGER CHECK(proficiency BETWEEN 1 AND 5),
                PRIMARY KEY (user_id, skill_id),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS content_skills (
                content_id TEXT,
                skill_id TEXT,
                PRIMARY KEY (content_id, skill_id),
                FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE,
                FOREIGN KEY (skill_id) REFERENCES skills(id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                content_id TEXT,
                type TEXT NOT NULL, -- view, click, rate, complete
                rating INTEGER CHECK(rating BETWEEN 1 AND 5),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (content_id) REFERENCES content(id) ON DELETE CASCADE
            )
            """
        ]
        
        # Additional indexing for performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_interactions_user_id ON interactions(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_interactions_content_id ON interactions(content_id);",
            "CREATE INDEX IF NOT EXISTS idx_content_category ON content(category);"
        ]
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            for query in queries:
                cursor.execute(query)
            for index in indexes:
                cursor.execute(index)
            conn.commit()
            
    def clear_database(self):
        """Clears all data from the tables, useful for testing and seeding."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM interactions")
            cursor.execute("DELETE FROM content_skills")
            cursor.execute("DELETE FROM user_skills")
            cursor.execute("DELETE FROM skills")
            cursor.execute("DELETE FROM content")
            cursor.execute("DELETE FROM users")
            conn.commit()
