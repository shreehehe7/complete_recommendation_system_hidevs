from dataclasses import dataclass
from typing import Optional, List, Dict
import json

@dataclass
class User:
    id: int
    name: str
    interests: List[str]
    created_at: str

    @classmethod
    def from_row(cls, row):
        interests_list = json.loads(row['interests']) if row['interests'] else []
        return cls(
            id=row['id'],
            name=row['name'],
            interests=interests_list,
            created_at=row['created_at']
        )

@dataclass
class Content:
    id: str
    title: str
    category: str
    difficulty: str
    popularity: int
    created_at: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            title=row['title'],
            category=row['category'],
            difficulty=row['difficulty'],
            popularity=row['popularity'],
            created_at=row['created_at']
        )

@dataclass
class Skill:
    id: str
    name: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            name=row['name']
        )

@dataclass
class UserSkill:
    user_id: int
    skill_id: str
    proficiency: int

    @classmethod
    def from_row(cls, row):
        return cls(
            user_id=row['user_id'],
            skill_id=row['skill_id'],
            proficiency=row['proficiency']
        )

@dataclass
class ContentSkill:
    content_id: str
    skill_id: str

    @classmethod
    def from_row(cls, row):
        return cls(
            content_id=row['content_id'],
            skill_id=row['skill_id']
        )

@dataclass
class Interaction:
    id: int
    user_id: int
    content_id: str
    type: str
    rating: Optional[int]
    created_at: str

    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            user_id=row['user_id'],
            content_id=row['content_id'],
            type=row['type'],
            rating=row['rating'],
            created_at=row['created_at']
        )
