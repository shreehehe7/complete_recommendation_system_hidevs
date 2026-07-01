import sys
import os
import random
from datetime import datetime, timedelta

# Add parent directory to path to allow importing from data module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import Database
from data.repositories import UserRepository, ContentRepository, SkillRepository, InteractionRepository

def seed_database():
    print("Initializing Database...")
    db = Database("recommendation.db")
    db.create_tables()
    db.clear_database()
    
    user_repo = UserRepository(db)
    content_repo = ContentRepository(db)
    skill_repo = SkillRepository(db)
    interaction_repo = InteractionRepository(db)
    
    # 1. Create Skills
    skills = [
        ('S1', 'Python'), ('S2', 'JavaScript'), ('S3', 'Machine Learning'),
        ('S4', 'Web Development'), ('S5', 'DevOps'), ('S6', 'Docker'),
        ('S7', 'Data Science'), ('S8', 'AI'), ('S9', 'CSS'),
        ('S10', 'React'), ('S11', 'APIs'), ('S12', 'Backend'),
        ('S13', 'Cloud Computing'), ('S14', 'UI/UX Design'), ('S15', 'NLP')
    ]
    for s_id, s_name in skills:
        skill_repo.create(s_id, s_name)
    print(f"Created {len(skills)} skills.")

    # 2. Create Content
    content_items = [
        ('C1', 'Intro to Python Programming', 'course', 'beginner', 120, ['S1']),
        ('C2', 'Advanced Machine Learning', 'course', 'advanced', 85, ['S1', 'S3', 'S8']),
        ('C3', 'React Fundamentals', 'tutorial', 'beginner', 150, ['S2', 'S4', 'S10']),
        ('C4', 'Building REST APIs with FastAPI', 'tutorial', 'intermediate', 110, ['S1', 'S11', 'S12']),
        ('C5', 'Docker for Beginners', 'article', 'beginner', 95, ['S5', 'S6']),
        ('C6', 'Deep Learning with PyTorch', 'course', 'advanced', 70, ['S1', 'S3', 'S8']),
        ('C7', 'CSS Grid & Flexbox Mastery', 'tutorial', 'intermediate', 130, ['S4', 'S9', 'S14']),
        ('C8', 'Data Visualization with Matplotlib', 'tutorial', 'intermediate', 80, ['S1', 'S7']),
        ('C9', 'Cloud Architecture on AWS', 'course', 'advanced', 60, ['S5', 'S13']),
        ('C10', 'SQL Database Design', 'article', 'beginner', 105, ['S12']),
        ('C11', 'Natural Language Processing', 'course', 'advanced', 55, ['S1', 'S8', 'S15']),
        ('C12', 'JavaScript ES6+ Features', 'article', 'intermediate', 140, ['S2', 'S4']),
        ('C13', 'Kubernetes Orchestration', 'tutorial', 'advanced', 45, ['S5', 'S6', 'S13']),
        ('C14', 'Statistics for Data Science', 'course', 'intermediate', 75, ['S7']),
        ('C15', 'UI/UX Design Principles', 'article', 'beginner', 115, ['S14']),
        ('C16', 'Flutter Mobile App Development', 'course', 'intermediate', 90, []),
        ('C17', 'Network Security Fundamentals', 'course', 'intermediate', 65, []),
        ('C18', 'Git Version Control', 'article', 'beginner', 160, ['S5']),
        ('C19', 'TensorFlow for AI Projects', 'tutorial', 'advanced', 50, ['S1', 'S3', 'S8']),
        ('C20', 'Responsive Web Design', 'tutorial', 'beginner', 125, ['S4', 'S9']),
        ('C21', 'Python Testing with Pytest', 'article', 'intermediate', 85, ['S1', 'S12']),
        ('C22', 'GraphQL API Development', 'tutorial', 'intermediate', 70, ['S2', 'S11', 'S12'])
    ]
    
    for c_id, title, category, difficulty, popularity, c_skills in content_items:
        content_repo.create(c_id, title, category, difficulty, popularity)
        for s_id in c_skills:
            skill_repo.add_content_skill(c_id, s_id)
    print(f"Created {len(content_items)} content items.")

    # 3. Create Users
    users = [
        (1, 'Alice Chen', ['Python', 'Machine Learning', 'Data Science']),
        (2, 'Bob Martinez', ['Web Development', 'JavaScript', 'React']),
        (3, 'Carol Williams', ['DevOps', 'Cloud Computing', 'Docker']),
        (4, 'David Kim', ['Python', 'APIs', 'Backend']),
        (5, 'Eva Johnson', ['Data Science', 'Statistics', 'R']),
        (6, 'Frank Brown', ['Cybersecurity', 'Networking']),
        (7, 'Grace Lee', ['UI/UX Design', 'CSS']),
        (8, 'Henry Davis', ['Mobile', 'Flutter', 'Swift']),
        (9, 'Ivy Wilson', ['AI', 'Deep Learning', 'NLP']),
        (10, 'Jack Taylor', []) # Cold start user
    ]
    
    for u_id, name, interests in users:
        user_repo.create(name, interests, user_id=u_id)
    print(f"Created {len(users)} users.")

    # 4. Create Interactions (Simulated Behavior)
    print("Generating interactions...")
    
    def add_interaction(u_id, c_id, i_type, rating=None):
        # We bypass repository here to set created_at slightly in the past
        with db.get_connection() as conn:
            days_ago = random.randint(0, 30)
            created_at = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d %H:%M:%S')
            conn.execute(
                "INSERT INTO interactions (user_id, content_id, type, rating, created_at) VALUES (?, ?, ?, ?, ?)",
                (u_id, c_id, i_type, rating, created_at)
            )
            conn.commit()

    # User 1: ML/Python focus
    add_interaction(1, 'C1', 'complete', rating=5)
    add_interaction(1, 'C2', 'rate', rating=4)
    add_interaction(1, 'C6', 'rate', rating=5)
    add_interaction(1, 'C8', 'view')
    add_interaction(1, 'C11', 'click')
    
    # User 2: Web Dev focus
    add_interaction(2, 'C3', 'complete', rating=5)
    add_interaction(2, 'C7', 'rate', rating=4)
    add_interaction(2, 'C12', 'view')
    add_interaction(2, 'C20', 'complete', rating=5)
    
    # User 3: DevOps focus
    add_interaction(3, 'C5', 'rate', rating=4)
    add_interaction(3, 'C9', 'view')
    add_interaction(3, 'C13', 'rate', rating=5)
    add_interaction(3, 'C18', 'complete', rating=5)
    
    # User 4: Backend/Python focus
    add_interaction(4, 'C1', 'rate', rating=4)
    add_interaction(4, 'C4', 'complete', rating=5)
    add_interaction(4, 'C10', 'view')
    add_interaction(4, 'C21', 'rate', rating=4)
    add_interaction(4, 'C22', 'click')

    # User 5: Data Science focus
    add_interaction(5, 'C8', 'rate', rating=5)
    add_interaction(5, 'C14', 'complete', rating=4)
    
    # User 6: Security focus
    add_interaction(6, 'C17', 'rate', rating=5)
    
    # User 7: Design focus
    add_interaction(7, 'C7', 'view')
    add_interaction(7, 'C15', 'rate', rating=5)
    add_interaction(7, 'C20', 'rate', rating=4)
    
    # User 8: Mobile focus
    add_interaction(8, 'C16', 'complete', rating=5)
    
    # User 9: AI/Deep Learning focus
    add_interaction(9, 'C2', 'view')
    add_interaction(9, 'C6', 'complete', rating=5)
    add_interaction(9, 'C11', 'rate', rating=4)
    add_interaction(9, 'C19', 'rate', rating=5)
    
    # User 10: Cold Start (No interactions)
    
    print("Database seeding complete!")

if __name__ == "__main__":
    seed_database()
