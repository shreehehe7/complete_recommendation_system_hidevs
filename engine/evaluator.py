import math

class RecommendationEvaluator:

    @staticmethod
    def precision_at_k(recommendations, relevant_items, k):
        if not recommendations or k <= 0:
            return 0.0
        top_k = set(recommendations[:k])
        relevant = set(relevant_items)
        if not top_k:
            return 0.0
        return len(top_k.intersection(relevant)) / len(top_k)

    @staticmethod
    def recall_at_k(recommendations, relevant_items, k):
        if not relevant_items:
            return 0.0
        if not recommendations or k <= 0:
            return 0.0
        top_k = set(recommendations[:k])
        relevant = set(relevant_items)
        return len(top_k.intersection(relevant)) / len(relevant)

    @staticmethod
    def ndcg_at_k(recommendations, relevant_items, k):
        if not recommendations or not relevant_items or k <= 0:
            return 0.0
        relevant_set = set(relevant_items)
        dcg = 0.0
        for i, item in enumerate(recommendations[:k]):
            rel = 1 if item in relevant_set else 0
            dcg += rel / math.log2(i + 2)
        idcg = 0.0
        num_relevant = min(len(relevant_set), k)
        for i in range(num_relevant):
            idcg += 1 / math.log2(i + 2)
        if idcg == 0.0:
            return 0.0
        return dcg / idcg

    @staticmethod
    def evaluate_all(recommendations_dict, ground_truth_dict, k):
        if not recommendations_dict or not ground_truth_dict:
            return {'precision@k': 0.0, 'recall@k': 0.0, 'ndcg@k': 0.0}
        total_users = 0
        sum_precision = 0.0
        sum_recall = 0.0
        sum_ndcg = 0.0
        for user_id, recs in recommendations_dict.items():
            if user_id in ground_truth_dict:
                truth = ground_truth_dict[user_id]
                sum_precision += RecommendationEvaluator.precision_at_k(recs, truth, k)
                sum_recall += RecommendationEvaluator.recall_at_k(recs, truth, k)
                sum_ndcg += RecommendationEvaluator.ndcg_at_k(recs, truth, k)
                total_users += 1
        if total_users == 0:
            return {'precision@k': 0.0, 'recall@k': 0.0, 'ndcg@k': 0.0}
        return {f'precision@{k}': sum_precision / total_users, f'recall@{k}': sum_recall / total_users, f'ndcg@{k}': sum_ndcg / total_users}