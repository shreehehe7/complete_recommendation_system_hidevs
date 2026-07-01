import time
from data.database import Database
from data.repositories import UserRepository, ContentRepository, InteractionRepository
from engine.candidate_gen import CandidateGenerator
from engine.scorer import RecommendationScorer

class RecommendationOrchestrator:
    def __init__(self, db: Database):
        self.db = db
        self.user_repo = UserRepository(db)
        self.content_repo = ContentRepository(db)
        self.interaction_repo = InteractionRepository(db)
        
        self.cache = {}
        self.cache_ttl = 60 # seconds
        self.metrics = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_response_time_ms': 0
        }

    def _get_cache_key(self, user_id: int, strategy: str, limit: int) -> str:
        return f"{user_id}:{strategy}:{limit}"

    def _load_data_for_user(self):
        """Loads required data for CandidateGenerator and RecommendationScorer."""
        user_ratings = self.interaction_repo.get_all_user_ratings()
        item_features = self.content_repo.get_all_features()
        item_popularities = self.content_repo.get_all_popularities()
        return user_ratings, item_features, item_popularities

    def get_recommendations(self, user_id: int, limit: int = 5, strategy: str = 'hybrid'):
        start_time = time.time()
        self.metrics['total_requests'] += 1
        
        cache_key = self._get_cache_key(user_id, strategy, limit)
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if time.time() - entry['timestamp'] < self.cache_ttl:
                self.metrics['cache_hits'] += 1
                response_time_ms = (time.time() - start_time) * 1000
                self.metrics['total_response_time_ms'] += response_time_ms
                return entry['data'], response_time_ms

        self.metrics['cache_misses'] += 1

        # Check if user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None, 0

        # Load data
        user_ratings, item_features, item_popularities = self._load_data_for_user()
        
        # Check cold start
        if user_id not in user_ratings or not user_ratings[user_id]:
            recommendations = self._handle_cold_start(user, item_features, item_popularities, limit)
            strategy = 'cold_start'
        else:
            gen = CandidateGenerator(user_ratings, item_features)
            if strategy == 'collaborative':
                candidates = gen.collaborative_candidates(user_id, limit=limit*2)
            elif strategy == 'content':
                candidates = gen.content_based_candidates(user_id, limit=limit*2)
            else: # hybrid
                candidates = gen.hybrid_candidates(user_id, limit=limit*2)
                
            scorer = RecommendationScorer(user_ratings, item_features, item_popularities)
            scored_candidates = scorer.rank_candidates(user_id, candidates, limit=limit)
            
            # Enrich with content details
            recommendations = self._enrich_candidates(scored_candidates)
            
        response_time_ms = (time.time() - start_time) * 1000
        self.metrics['total_response_time_ms'] += response_time_ms
        
        # Cache results
        self.cache[cache_key] = {
            'timestamp': time.time(),
            'data': recommendations
        }
        
        return recommendations, response_time_ms

    def _handle_cold_start(self, user, item_features, item_popularities, limit):
        # Recommend popular items that match user interests, or just popular items
        popular_content = self.content_repo.get_popular(limit=20)
        
        recommendations = []
        user_interests_lower = [i.lower() for i in user.interests]
        
        # Filter by interests if available
        if user_interests_lower:
            for item in popular_content:
                # Basic text matching or matching category
                if item.category.lower() in user_interests_lower or \
                   any(interest in item.title.lower() for interest in user_interests_lower):
                    recommendations.append({
                        'item_id': item.id,
                        'score': 1.0,
                        'explanation': f"Recommended for new users interested in {item.category}",
                        'title': item.title,
                        'category': item.category,
                        'difficulty': item.difficulty
                    })
                    if len(recommendations) >= limit:
                        break
                        
        # Fallback to popularity
        for item in popular_content:
            if len(recommendations) >= limit:
                break
            if not any(r['item_id'] == item.id for r in recommendations):
                recommendations.append({
                    'item_id': item.id,
                    'score': 0.8,
                    'explanation': "Trending content on the platform",
                    'title': item.title,
                    'category': item.category,
                    'difficulty': item.difficulty
                })
                
        return recommendations

    def _enrich_candidates(self, scored_candidates):
        enriched = []
        for cand in scored_candidates:
            item = self.content_repo.get_by_id(cand['item_id'])
            if item:
                cand['title'] = item.title
                cand['category'] = item.category
                cand['difficulty'] = item.difficulty
                enriched.append(cand)
        return enriched

    def record_feedback(self, user_id: int, content_id: str, interaction_type: str, rating: int = None):
        # Invalidate cache for this user
        keys_to_delete = [k for k in self.cache.keys() if k.startswith(f"{user_id}:")]
        for k in keys_to_delete:
            del self.cache[k]
            
        return self.interaction_repo.create(user_id, content_id, interaction_type, rating)
        
    def get_metrics_report(self):
        total = self.metrics['total_requests']
        avg_rt = self.metrics['total_response_time_ms'] / total if total > 0 else 0
        hit_rate = self.metrics['cache_hits'] / total if total > 0 else 0
        
        return {
            'total_requests': total,
            'cache_hits': self.metrics['cache_hits'],
            'cache_misses': self.metrics['cache_misses'],
            'cache_hit_rate': round(hit_rate, 4),
            'avg_response_time_ms': round(avg_rt, 2),
            'cache_size': len(self.cache)
        }
