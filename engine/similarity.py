import math

class SimilarityCalculator:

    @staticmethod
    def cosine_similarity(vec1, vec2):
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot_product = sum((a * b for a, b in zip(vec1, vec2)))
        norm1 = math.sqrt(sum((a * a for a in vec1)))
        norm2 = math.sqrt(sum((b * b for b in vec2)))
        if norm1 == 0.0 or norm2 == 0.0:
            return 0.0
        return dot_product / (norm1 * norm2)

    @staticmethod
    def jaccard_similarity(set1, set2):
        if not isinstance(set1, set):
            set1 = set(set1)
        if not isinstance(set2, set):
            set2 = set(set2)
        if not set1 and (not set2):
            return 0.0
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        if union == 0:
            return 0.0
        return intersection / union

    @staticmethod
    def pearson_correlation(ratings1, ratings2):
        if not ratings1 or not ratings2 or len(ratings1) != len(ratings2):
            return 0.0
        n = len(ratings1)
        if n == 1:
            return 0.0
        mean1 = sum(ratings1) / n
        mean2 = sum(ratings2) / n
        numerator = sum(((r1 - mean1) * (r2 - mean2) for r1, r2 in zip(ratings1, ratings2)))
        var1 = sum(((r1 - mean1) ** 2 for r1 in ratings1))
        var2 = sum(((r2 - mean2) ** 2 for r2 in ratings2))
        if var1 == 0.0 or var2 == 0.0:
            return 0.0
        return numerator / math.sqrt(var1 * var2)