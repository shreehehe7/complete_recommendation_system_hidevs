from .similarity import SimilarityCalculator

class CandidateGenerator:

    def __init__(self, user_ratings, item_features):
        self.user_ratings = user_ratings
        self.item_features = item_features
        for item, features in self.item_features.items():
            if not isinstance(features, set):
                self.item_features[item] = set(features)
        self.all_items = set()
        for items in self.user_ratings.values():
            self.all_items.update(items.keys())
        self.all_items.update(self.item_features.keys())

    def popularity_candidates(self, limit=20):
        item_counts = {item: 0 for item in self.all_items}
        for user_items in self.user_ratings.values():
            for item in user_items:
                item_counts[item] += 1
        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        return [item for item, count in sorted_items[:limit]]

    def collaborative_candidates(self, user_id, limit=20):
        if user_id not in self.user_ratings or not self.user_ratings[user_id]:
            return self.popularity_candidates(limit)
        target_ratings = self.user_ratings[user_id]
        user_similarities = []
        for other_user, other_ratings in self.user_ratings.items():
            if other_user == user_id:
                continue
            all_rated_items = set(target_ratings.keys()).union(other_ratings.keys())
            vec1 = [target_ratings.get(item, 0) for item in all_rated_items]
            vec2 = [other_ratings.get(item, 0) for item in all_rated_items]
            sim = SimilarityCalculator.cosine_similarity(vec1, vec2)
            user_similarities.append((other_user, sim))
        user_similarities.sort(key=lambda x: x[1], reverse=True)
        top_similar_users = [user for user, sim in user_similarities[:5]]
        candidate_scores = {}
        for sim_user in top_similar_users:
            for item, rating in self.user_ratings[sim_user].items():
                if item not in target_ratings and rating >= 4:
                    candidate_scores[item] = candidate_scores.get(item, 0) + rating
        sorted_candidates = sorted(candidate_scores.items(), key=lambda x: x[1], reverse=True)
        return [item for item, score in sorted_candidates[:limit]]

    def content_based_candidates(self, user_id, limit=20):
        if user_id not in self.user_ratings or not self.user_ratings[user_id]:
            return self.popularity_candidates(limit)
        target_ratings = self.user_ratings[user_id]
        user_features = set()
        for item, rating in target_ratings.items():
            if rating >= 3 and item in self.item_features:
                user_features.update(self.item_features[item])
        candidate_scores = []
        for item, features in self.item_features.items():
            if item not in target_ratings:
                sim = SimilarityCalculator.jaccard_similarity(user_features, features)
                candidate_scores.append((item, sim))
        candidate_scores.sort(key=lambda x: x[1], reverse=True)
        return [item for item, sim in candidate_scores[:limit]]

    def hybrid_candidates(self, user_id, limit=30):
        collab = self.collaborative_candidates(user_id, limit)
        content = self.content_based_candidates(user_id, limit)
        popular = self.popularity_candidates(limit)
        hybrid_list = []
        seen = set()
        max_len = max(len(collab), len(content), len(popular))
        for i in range(max_len):
            if i < len(collab) and collab[i] not in seen:
                hybrid_list.append(collab[i])
                seen.add(collab[i])
            if i < len(content) and content[i] not in seen:
                hybrid_list.append(content[i])
                seen.add(content[i])
            if i < len(popular) and popular[i] not in seen:
                hybrid_list.append(popular[i])
                seen.add(popular[i])
            if len(hybrid_list) >= limit:
                break
        return hybrid_list