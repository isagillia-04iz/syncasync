import asyncio
import csv
import statistics
import time
import httpx
import requests

URL = "https://api.open-meteo.com/v1/forecast?latitude=14.5995&longitude=120.9842&current_weather=true"
TOTAL_REQUESTS = 50
MAX_CONCURRENCY = 10


def run_sync():
    results = []
    start_total = time.perf_counter()
    with requests.Session() as session:
        for i in range(1, TOTAL_REQUESTS + 1):
            t0 = time.perf_counter()
            try:
                resp = session.get(URL, timeout=10)
                status = resp.status_code
            except Exception:
                status = 0
            latency_ms = (time.perf_counter() - t0) * 1000
            results.append(("sync", i, status, round(latency_ms, 2)))
    total_time = time.perf_counter() - start_total
    return results, total_time


async def fetch_async(client, sem, i):
    async with sem:
        t0 = time.perf_counter()
        try:
            resp = await client.get(URL, timeout=10)
            status = resp.status_code
        except Exception:
            status = 0
        latency_ms = (time.perf_counter() - t0) * 1000
        return ("async", i, status, round(latency_ms, 2))


async def run_async():
    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    start_total = time.perf_counter()
    async with httpx.AsyncClient() as client:
        tasks = [fetch_async(client, sem, i) for i in range(1, TOTAL_REQUESTS + 1)]
        results = await asyncio.gather(*tasks)
    total_time = time.perf_counter() - start_total
    return results, total_time


def summarize(label, results, total_time):
    latencies = [r[3] for r in results if r[2] == 200]
    success_rate = (len(latencies) / len(results)) * 100
    median = statistics.median(latencies) if latencies else 0
    p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 20 else max(latencies, default=0)
    print(f"\n--- {label} ---")
    print(f"Total Wall Time : {total_time:.2f} s")
    print(f"Success Rate    : {success_rate:.1f}%")
    print(f"Median Latency  : {median:.2f} ms")
    print(f"p95 Latency     : {p95:.2f} ms")


if __name__ == "__main__":
    print(f"Running {TOTAL_REQUESTS} sync requests...")
    sync_results, sync_time = run_sync()

    print(f"Running {TOTAL_REQUESTS} async requests (max concurrency={MAX_CONCURRENCY})...")
    async_results, async_time = asyncio.run(run_async())

    with open("results.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["method", "request_id", "status_code", "latency_ms"])
        writer.writerows(sync_results + async_results)

    summarize("Sync (requests.Session)", sync_results, sync_time)
    summarize("Async (httpx + asyncio)", async_results, async_time)
    print("\nSaved raw data to results.csv")