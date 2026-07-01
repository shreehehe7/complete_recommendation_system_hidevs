# Complete AI Recommendation System

A production-ready recommendation system built as a full-stack application. It features a SQLite data layer, a pluggable recommendation engine with hybrid scoring, a FastAPI backend, and a modern glassmorphism frontend dashboard.

## 🚀 Features

- **Hybrid Recommendation Engine**: Combines collaborative filtering, content-based matching, and popularity heuristics.
- **Cold Start Handling**: Recommends personalized popular content for users with no interaction history based on their stated interests.
- **REST API**: Built with FastAPI for high performance, featuring auto-generated Swagger UI docs.
- **Premium Dashboard**: A responsive, dark-mode frontend built with pure HTML/CSS/JS (vanilla) leveraging CSS Grid, Flexbox, and backdrop filters.
- **Telemetry & Metrics**: Built-in request tracing, response time tracking, and caching hit/miss stats.
- **Comprehensive Testing**: Unit tests, integration tests, and simulated concurrent load tests.

## 📁 Project Structure

```text
day30_capstone/
├── api/                  # FastAPI Application
├── data/                 # SQLite Database and Repository layer
├── engine/               # Core AI Recommendation Logic
├── frontend/             # Dashboard UI
├── scripts/              # Seeding, Evaluation, and Load Testing
├── tests/                # Pytest Test Suite
```

## 🛠️ Setup & Installation

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   pip install -r requirements.txt
   ```

2. Seed the database with sample users, content, and interactions:
   ```bash
   python scripts/seed_data.py
   ```

## 🏃‍♂️ Running the System

1. Start the API Server (which also serves the frontend):
   ```bash
   uvicorn api.app:app --reload
   ```

2. Open the dashboard in your browser:
   **http://localhost:8000**

3. Access the auto-generated API Documentation:
   **http://localhost:8000/docs**

## 🧪 Testing & Evaluation

Run the unit and integration tests:
```bash
pytest tests/ -v
```

Generate the Evaluation Report (Precision/Recall/NDCG):
```bash
python scripts/evaluate.py
```

Run the Load Test (simulates 10 concurrent users):
```bash
# Ensure the API server is running first!
python scripts/load_test.py
```
