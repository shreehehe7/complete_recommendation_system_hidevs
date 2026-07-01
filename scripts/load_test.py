import concurrent.futures
import time
import requests
import statistics

API_URL = "http://localhost:8000/api"

def simulate_user_session(user_id):
    session_times = []
    
    try:
        # Request 1: Load recommendations
        start = time.time()
        res = requests.get(f"{API_URL}/recommend/{user_id}?strategy=hybrid")
        session_times.append((time.time() - start) * 1000)
        
        if res.status_code != 200:
            return {"error": f"Failed with {res.status_code}"}
            
        data = res.json()
        if not data.get("recommendations"):
            return {"error": "No recommendations returned"}
            
        # Request 2: Click an item
        item = data["recommendations"][0]["item_id"]
        start = time.time()
        requests.post(f"{API_URL}/feedback", json={
            "user_id": user_id,
            "content_id": item,
            "interaction_type": "click"
        })
        session_times.append((time.time() - start) * 1000)
        
        # Request 3: Re-load recommendations (Should hit cache)
        start = time.time()
        requests.get(f"{API_URL}/recommend/{user_id}?strategy=hybrid")
        session_times.append((time.time() - start) * 1000)
        
        return {"times": session_times, "success": True}
        
    except Exception as e:
        return {"error": str(e)}

def run_load_test():
    print("Starting Load Test (10 concurrent users)...")
    print("Make sure the API server is running on localhost:8000")
    
    user_ids = list(range(1, 11))
    
    start_total = time.time()
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_user = {executor.submit(simulate_user_session, uid): uid for uid in user_ids}
        for future in concurrent.futures.as_completed(future_to_user):
            results.append(future.result())
            
    total_time = time.time() - start_total
    
    all_times = []
    success_count = 0
    error_count = 0
    
    for r in results:
        if "error" in r:
            error_count += 1
            print(f"Error: {r['error']}")
        else:
            success_count += 1
            all_times.extend(r["times"])
            
    print("\n--- Load Test Results ---")
    print(f"Total Users Simulated: {len(user_ids)}")
    print(f"Successful Sessions: {success_count}")
    print(f"Failed Sessions: {error_count}")
    print(f"Total Time Taken: {total_time:.2f} seconds")
    
    if all_times:
        print(f"\nResponse Times (ms):")
        print(f"  Min: {min(all_times):.2f}")
        print(f"  Max: {max(all_times):.2f}")
        print(f"  Avg: {statistics.mean(all_times):.2f}")
        print(f"  p50: {statistics.median(all_times):.2f}")
        if len(all_times) > 1:
            print(f"  p95: {statistics.quantiles(all_times, n=20)[18]:.2f}")

if __name__ == "__main__":
    run_load_test()
