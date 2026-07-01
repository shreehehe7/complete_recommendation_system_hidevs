import json
from .models import User, Content, Skill, UserSkill, ContentSkill, Interaction
from .database import Database

class UserRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, user_id: int) -> User:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            return User.from_row(row) if row else None

    def get_all(self):
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM users").fetchall()
            return [User.from_row(row) for row in rows]

    def create(self, name: str, interests: list, user_id: int = None) -> int:
        with self.db.get_connection() as conn:
            interests_str = json.dumps(interests)
            if user_id is not None:
                cursor = conn.execute(
                    "INSERT INTO users (id, name, interests) VALUES (?, ?, ?)",
                    (user_id, name, interests_str)
                )
            else:
                cursor = conn.execute(
                    "INSERT INTO users (name, interests) VALUES (?, ?)",
                    (name, interests_str)
                )
            conn.commit()
            return cursor.lastrowid

class ContentRepository:
    def __init__(self, db: Database):
        self.db = db

    def get_by_id(self, content_id: str) -> Content:
        with self.db.get_connection() as conn:
            row = conn.execute("SELECT * FROM content WHERE id = ?", (content_id,)).fetchone()
            return Content.from_row(row) if row else None

    def get_all(self):
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM content").fetchall()
            return [Content.from_row(row) for row in rows]

    def get_popular(self, limit: int = 10):
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM content ORDER BY popularity DESC LIMIT ?", (limit,)).fetchall()
            return [Content.from_row(row) for row in rows]

    def create(self, id: str, title: str, category: str, difficulty: str, popularity: int = 0) -> str:
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO content (id, title, category, difficulty, popularity) VALUES (?, ?, ?, ?, ?)",
                (id, title, category, difficulty, popularity)
            )
            conn.commit()
            return id
            
    def get_all_features(self) -> dict:
        """Returns a dictionary of content_id -> set of skill_ids for Content-based filtering."""
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT content_id, skill_id FROM content_skills").fetchall()
            features = {}
            for row in rows:
                c_id = row['content_id']
                if c_id not in features:
                    features[c_id] = set()
                features[c_id].add(row['skill_id'])
            
            # Ensure all content is in features dict, even if no skills
            all_content = self.get_all()
            for c in all_content:
                if c.id not in features:
                    features[c.id] = set()
                    
            return features
            
    def get_all_popularities(self) -> dict:
        """Returns a dictionary of content_id -> popularity score."""
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT id, popularity FROM content").fetchall()
            return {row['id']: row['popularity'] for row in rows}

class SkillRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(self, id: str, name: str) -> str:
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO skills (id, name) VALUES (?, ?)",
                (id, name)
            )
            conn.commit()
            return id

    def add_content_skill(self, content_id: str, skill_id: str):
        with self.db.get_connection() as conn:
            conn.execute(
                "INSERT INTO content_skills (content_id, skill_id) VALUES (?, ?)",
                (content_id, skill_id)
            )
            conn.commit()

class InteractionRepository:
    def __init__(self, db: Database):
        self.db = db

    def create(self, user_id: int, content_id: str, type: str, rating: int = None) -> int:
        with self.db.get_connection() as conn:
            cursor = conn.execute(
                "INSERT INTO interactions (user_id, content_id, type, rating) VALUES (?, ?, ?, ?)",
                (user_id, content_id, type, rating)
            )
            
            # If it's a rating or complete, boost popularity
            if type in ('rate', 'complete', 'click'):
                boost = 5 if type == 'rate' and rating and rating >= 4 else (2 if type == 'complete' else 1)
                conn.execute("UPDATE content SET popularity = popularity + ? WHERE id = ?", (boost, content_id))
                
            conn.commit()
            return cursor.lastrowid

    def get_by_user(self, user_id: int):
        with self.db.get_connection() as conn:
            rows = conn.execute("SELECT * FROM interactions WHERE user_id = ? ORDER BY created_at DESC", (user_id,)).fetchall()
            return [Interaction.from_row(row) for row in rows]
            
    def get_user_ratings(self, user_id: int) -> dict:
        """Returns {content_id: rating} for a given user."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT content_id, rating FROM interactions WHERE user_id = ? AND rating IS NOT NULL", 
                (user_id,)
            ).fetchall()
            return {row['content_id']: row['rating'] for row in rows}
            
    def get_all_user_ratings(self) -> dict:
        """Returns {user_id: {content_id: rating}} for all users."""
        with self.db.get_connection() as conn:
            rows = conn.execute(
                "SELECT user_id, content_id, rating FROM interactions WHERE rating IS NOT NULL"
            ).fetchall()
            ratings = {}
            for row in rows:
                u_id = row['user_id']
                if u_id not in ratings:
                    ratings[u_id] = {}
                ratings[u_id][row['content_id']] = row['rating']
            return ratings
