import pytest
import os
import sys
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.similarity import SimilarityCalculator
from engine.candidate_gen import CandidateGenerator
from engine.scorer import RecommendationScorer
from engine.evaluator import RecommendationEvaluator
from engine.orchestrator import RecommendationOrchestrator
from data.database import Database

def test_similarity_calculator():
    assert math.isclose(SimilarityCalculator.cosine_similarity([1, 0], [1, 0]), 1.0)
    assert SimilarityCalculator.cosine_similarity([1, 0], [0, 1]) == 0.0
    assert math.isclose(SimilarityCalculator.jaccard_similarity({'a', 'b'}, {'b', 'c'}), 1/3)

def test_candidate_generator():
    user_ratings = {
        1: {'C1': 5, 'C2': 4},
        2: {'C1': 3, 'C3': 5}
    }
    item_features = {
        'C1': {'S1', 'S2'},
        'C2': {'S1'},
        'C3': {'S2', 'S3'}
    }
    
    gen = CandidateGenerator(user_ratings, item_features)
    pop = gen.popularity_candidates(limit=2)
    assert len(pop) == 2
    assert 'C1' in pop # Most popular since rated by both
    
    collab = gen.collaborative_candidates(1, limit=1)
    assert 'C3' in collab # User 2 liked C3, and User 2 is similar to User 1
    
def test_scorer():
    user_ratings = {1: {'C1': 5}}
    item_features = {'C1': {'S1'}, 'C2': {'S1'}, 'C3': {'S2'}}
    item_pop = {'C1': 10, 'C2': 5, 'C3': 2}
    
    scorer = RecommendationScorer(user_ratings, item_features, item_pop)
    ranked = scorer.rank_candidates(1, ['C2', 'C3'], limit=2)
    
    assert len(ranked) == 2
    assert ranked[0]['item_id'] == 'C2' # Shares feature S1 and more popular

def test_evaluator():
    recs = ['C1', 'C2', 'C3']
    truth = ['C2', 'C4']
    
    p5 = RecommendationEvaluator.precision_at_k(recs, truth, 5)
    assert p5 == 1 / 3
    
    r5 = RecommendationEvaluator.recall_at_k(recs, truth, 5)
    assert r5 == 1 / 2

@pytest.fixture
def mock_db():
    db = Database(":memory:")
    db.create_tables()
    db.clear_database()
    return db

def test_orchestrator(mock_db):
    orch = RecommendationOrchestrator(mock_db)
    
    # Add dummy data
    orch.user_repo.create("Test User", ["Python"], user_id=1)
    orch.content_repo.create("C1", "Python Course", "course", "beginner", 10)
    
    # Cold start test
    recs, rt = orch.get_recommendations(1, limit=1, strategy='hybrid')
    assert len(recs) == 1
    assert recs[0]['item_id'] == "C1"
    
    # Metrics check
    metrics = orch.get_metrics_report()
    assert metrics['total_requests'] == 1
    assert metrics['cache_misses'] == 1
    
    # Cache hit check
    recs2, rt2 = orch.get_recommendations(1, limit=1, strategy='hybrid')
    metrics2 = orch.get_metrics_report()
    assert metrics2['total_requests'] == 2
    assert metrics2['cache_hits'] == 1
