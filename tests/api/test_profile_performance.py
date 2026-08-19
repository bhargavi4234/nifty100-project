import time

import requests

API_BASE = "http://127.0.0.1:8000/api/v1/companies"

TICKERS = [
    "ABB",
    "ADANIENSOL",
    "ADANIENT",
    "ADANIGREEN",
    "ADANIPORTS",
]


def test_company_profile_performance():
    results = []

    print("\nCompany Profile Performance")
    print("=" * 55)

    for ticker in TICKERS:
        start = time.perf_counter()

        response = requests.get(
            f"{API_BASE}/{ticker}",
            timeout=10,
        )

        elapsed = time.perf_counter() - start

        results.append(elapsed)

        print(
            f"{ticker:<12} | "
            f"Status: {response.status_code} | "
            f"Time: {elapsed:.4f}s"
        )

        assert response.status_code == 200

    print("=" * 55)
    print(f"Average: {sum(results) / len(results):.4f}s")
    print(f"Maximum: {max(results):.4f}s")

    assert max(results) < 3
