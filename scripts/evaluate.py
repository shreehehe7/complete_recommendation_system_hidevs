import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.database import Database
from data.repositories import UserRepository
from engine.orchestrator import RecommendationOrchestrator
from engine.evaluator import RecommendationEvaluator

def run_evaluation():
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recommendation.db")
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}. Please run seed_data.py first.")
        return

    db = Database(db_path)
    user_repo = UserRepository(db)
    orchestrator = RecommendationOrchestrator(db)
    
    users = user_repo.get_all()
    
    # Define ground truth for evaluation based on the seeded data
    ground_truth = {
        1: ['C11', 'C19', 'C14'], # ML/Data Science
        2: ['C22', 'C12', 'C20'], # Web/JS
        3: ['C13', 'C5', 'C9'],   # DevOps/Cloud
        4: ['C22', 'C10', 'C21'], # Backend/Python
        5: ['C14', 'C8', 'C11'],  # Data Science
        6: ['C17', 'C18'],        # Security/DevOps
        7: ['C15', 'C7', 'C20'],  # Design/CSS
        8: ['C16', 'C4'],         # Mobile/APIs
        9: ['C2', 'C11', 'C19'],  # AI/NLP
        # User 10 is cold start, no ground truth to evaluate against
    }
    
    strategies = ['collaborative', 'content', 'hybrid']
    results = {}
    
    print("Running evaluation...")
    
    for strategy in strategies:
        print(f"Evaluating strategy: {strategy}")
        recommendations_dict = {}
        
        for user in users:
            if user.id not in ground_truth:
                continue # Skip cold start user for metric calc
                
            # Clear cache to get true processing time
            orchestrator.cache.clear()
            
            recs, _ = orchestrator.get_recommendations(user.id, limit=5, strategy=strategy)
            recommendations_dict[user.id] = [r['item_id'] for r in recs]
            
        metrics = RecommendationEvaluator.evaluate_all(recommendations_dict, ground_truth, k=5)
        results[strategy] = metrics
        
    # Generate Markdown Report
    report_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "evaluation_report.md")
    
    with open(report_path, "w") as f:
        f.write("# Recommendation System Evaluation Report\n\n")
        f.write("## Overall Performance Metrics (k=5)\n\n")
        f.write("| Strategy | Precision@5 | Recall@5 | NDCG@5 |\n")
        f.write("|----------|-------------|----------|--------|\n")
        
        for strategy, metrics in results.items():
            p = metrics.get('precision@5', metrics.get('precision@k', 0.0))
            r = metrics.get('recall@5', metrics.get('recall@k', 0.0))
            n = metrics.get('ndcg@5', metrics.get('ndcg@k', 0.0))
            f.write(f"| {strategy.capitalize()} | {p:.4f} | {r:.4f} | {n:.4f} |\n")
            
        f.write("\n## System Telemetry\n")
        sys_metrics = orchestrator.get_metrics_report()
        f.write("```json\n")
        import json
        f.write(json.dumps(sys_metrics, indent=2))
        f.write("\n```\n")
        
    print(f"Evaluation complete. Report generated at: {report_path}")

if __name__ == "__main__":
    run_evaluation()
