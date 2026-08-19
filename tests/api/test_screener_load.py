import threading
import time

import requests

API_URL = "http://127.0.0.1:8000/api/v1/screener"
NUM_REQUESTS = 10

results = []
lock = threading.Lock()


def make_request(request_id):
    start = time.perf_counter()

    try:
        response = requests.get(
            API_URL,
            params={"min_roe": 15},
            timeout=10,
        )

        elapsed = time.perf_counter() - start

        with lock:
            results.append(
                {
                    "request": request_id,
                    "status": response.status_code,
                    "time": elapsed,
                }
            )

    except (ConnectionError, TimeoutError, OSError) as exc:
        elapsed = time.perf_counter() - start

        with lock:
            results.append(
                {
                    "request": request_id,
                    "status": "ERROR",
                    "time": elapsed,
                    "error": str(exc),
                }
            )


def test_10_concurrent_screener_requests():
    threads = []

    total_start = time.perf_counter()

    for i in range(NUM_REQUESTS):
        thread = threading.Thread(
            target=make_request,
            args=(i + 1,),
        )

        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    total_elapsed = time.perf_counter() - total_start

    results.sort(key=lambda x: x["request"])

    print("\nScreener Load Test")
    print("=" * 50)

    for result in results:
        print(
            f"Request {result['request']:02d} | "
            f"Status: {result['status']} | "
            f"Time: {result['time']:.4f}s"
        )

    print("=" * 50)
    print(f"Total elapsed time: {total_elapsed:.4f}s")
    print(f"Maximum individual response: " f"{max(r['time'] for r in results):.4f}s")

    assert len(results) == NUM_REQUESTS
    assert all(r["status"] == 200 for r in results)
    assert total_elapsed < 10
