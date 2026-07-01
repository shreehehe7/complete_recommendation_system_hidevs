import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import Database
from data.repositories import UserRepository, ContentRepository, SkillRepository, InteractionRepository

@pytest.fixture
def test_db():
    # Use an in-memory database for testing
    db = Database(":memory:")
    db.create_tables()
    db.clear_database()
    return db

def test_database_creation(test_db):
    with test_db.get_connection() as conn:
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        table_names = [t['name'] for t in tables]
        assert 'users' in table_names
        assert 'content' in table_names
        assert 'skills' in table_names
        assert 'interactions' in table_names

def test_user_repository(test_db):
    repo = UserRepository(test_db)
    user_id = repo.create("Test User", ["Python", "AI"])
    assert user_id == 1
    
    user = repo.get_by_id(1)
    assert user.name == "Test User"
    assert "Python" in user.interests

def test_content_and_skills(test_db):
    c_repo = ContentRepository(test_db)
    s_repo = SkillRepository(test_db)
    
    c_repo.create("C1", "Test Content", "course", "beginner", 10)
    s_repo.create("S1", "Python")
    s_repo.add_content_skill("C1", "S1")
    
    features = c_repo.get_all_features()
    assert "C1" in features
    assert "S1" in features["C1"]
    
    popular = c_repo.get_popular(1)
    assert len(popular) == 1
    assert popular[0].id == "C1"

def test_interaction_repository(test_db):
    u_repo = UserRepository(test_db)
    c_repo = ContentRepository(test_db)
    i_repo = InteractionRepository(test_db)
    
    u_repo.create("User 1", [], user_id=1)
    c_repo.create("C1", "Content 1", "course", "beginner", 0)
    
    i_id = i_repo.create(1, "C1", "rate", 5)
    assert i_id > 0
    
    ratings = i_repo.get_user_ratings(1)
    assert "C1" in ratings
    assert ratings["C1"] == 5
    
    # Check if popularity increased
    c = c_repo.get_by_id("C1")
    assert c.popularity == 5 # 5 points for rating >= 4
