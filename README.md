# Sync vs. Async in Python: Benchmarking 50 Live API Calls (`requests` vs. `httpx`)

When querying external APIs at scale, switching from synchronous to asynchronous requests is standard advice—but how much faster is it in practice, and what is the trade-off in per-request latency?

To measure this instead of guessing, I ran 50 synchronous requests and 50 asynchronous requests against the live Open-Meteo API and logged every response time.

## Test Setup
- **Target Endpoint:** Open-Meteo Forecast API (Manila coordinates, no API key required)
- **Sample Size:** 50 requests per method (100 total)
- **Fairness Controls:**
  - Used `requests.Session()` for the synchronous test so TCP connections are reused (connection pooling), rather than penalizing sync with a fresh handshake on every call.
  - Capped async concurrency at `10` using `asyncio.Semaphore(10)` to reflect realistic production rate-limit handling.
- **Environment:** Python 3.13, tested from the Philippines on November 24, 2026.

## Results

| Metric | Sync (`requests.Session`) | Async (`httpx` + `asyncio`) |
| :--- | :---: | :---: |
| **Total Wall Time** | `15.93 s` | `2.74 s` |
| **Success Rate** | `100.0%` | `100.0%` |
| **Median Latency (per request)** | `306.98 ms` | `304.83 ms` |
| **p95 Latency (per request)** | `368.68 ms` | `872.78 ms` |

*Raw request-by-request logs are available in [`results.csv`](./results.csv).*

## Honest Takeaway
- **Wall time drops by ~5.8x:** Async finished all 50 requests in `2.74 s` compared to `15.93 s` for sync, because it overlaps network I/O wait times instead of blocking sequentially.
- **The tail-latency trade-off:** While median per-request latency was nearly identical (`306.98 ms` vs. `304.83 ms`), async's **p95 latency more than doubled** (`872.78 ms` vs. `368.68 ms`). Running 10 concurrent requests introduces queuing and connection overhead—proving that async optimizes total throughput, not worst-case single-request speed.

## How to Reproduce
```bash
git clone [https://github.com/isagillia-04iz/syncasync.git](https://github.com/isagillia-04iz/syncasync.git)
cd syncasync
pip install -r requirements.txt
python benchmark.py
