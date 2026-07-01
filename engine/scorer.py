from .similarity import SimilarityCalculator

class RecommendationScorer:

    def __init__(self, user_ratings, item_features, item_popularities=None):
        self.user_ratings = user_ratings
        self.item_features = item_features
        self.item_popularities = item_popularities or {}
        self.scorers = {}
        self.weights = {}
        self.add_scorer('relevance', self._relevance_scorer, 0.5)
        self.add_scorer('popularity', self._popularity_scorer, 0.3)
        self.add_scorer('recency', self._recency_scorer, 0.2)

    def add_scorer(self, name, function, weight):
        self.scorers[name] = function
        self.weights[name] = weight

    def _relevance_scorer(self, user_id, item_id, context=None):
        if user_id not in self.user_ratings or item_id not in self.item_features:
            return 0.5
        target_ratings = self.user_ratings[user_id]
        user_features = set()
        for item, rating in target_ratings.items():
            if rating >= 3 and item in self.item_features:
                user_features.update(self.item_features[item])
        item_features_set = self.item_features[item_id]
        return SimilarityCalculator.jaccard_similarity(user_features, item_features_set)

    def _popularity_scorer(self, user_id, item_id, context=None):
        if not self.item_popularities:
            return 0.5
        max_pop = max(self.item_popularities.values()) if self.item_popularities else 1
        if max_pop == 0:
            return 0.5
        pop = self.item_popularities.get(item_id, 0)
        return pop / max_pop

    def _recency_scorer(self, user_id, item_id, context=None):
        if context and 'timestamps' in context and (item_id in context['timestamps']):
            pass
        return 0.5

    def calculate_score(self, user_id, item_id, context=None):
        total_weight = sum(self.weights.values())
        if total_weight == 0:
            return (0.0, {})
        final_score = 0.0
        individual_scores = {}
        for name, scorer in self.scorers.items():
            score = scorer(user_id, item_id, context)
            weighted_score = score * (self.weights[name] / total_weight)
            final_score += weighted_score
            individual_scores[name] = score
        return (final_score, individual_scores)

    def rank_candidates(self, user_id, candidates, context=None, limit=10):
        scored_candidates = []
        for item_id in candidates:
            score, individual_scores = self.calculate_score(user_id, item_id, context)
            explanation_parts = []
            for name, s in individual_scores.items():
                if s > 0.6:
                    explanation_parts.append(f'High {name} ({s:.2f})')
                elif s > 0.3:
                    explanation_parts.append(f'Moderate {name} ({s:.2f})')
            explanation = ' + '.join(explanation_parts) if explanation_parts else 'Default recommendation'
            scored_candidates.append({'item_id': item_id, 'score': score, 'explanation': explanation})
        scored_candidates.sort(key=lambda x: x['score'], reverse=True)
        return scored_candidates[:limit]