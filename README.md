# Sync vs. Async in Python: Benchmarking 50 Live API Calls (`requests` vs. `httpx`)

When querying external APIs at scale, switching from synchronous to asynchronous requests is standard advice—but how much faster is it in practice, and what is the trade-off in per-request latency?

To measure this instead of guessing, I ran 50 synchronous requests and 50 asynchronous requests against the live Open-Meteo API and logged every response time.

## Test Setup
- **Target Endpoint:** Open-Meteo Forecast API (Manila coordinates, no API key required)
- **Sample Size:** 50 requests per method (100 total)
- **Fairness Controls:**
  - Used `requests.Session()` for the synchronous test so TCP connections are reused (connection pooling), rather than penalizing sync with a fresh handshake on every call.
  - Capped async concurrency at `10` using `asyncio.Semaphore(10)` to reflect realistic production rate-limit handling.
- **Environment:** Python 3.x, tested from the Philippines on [Date].

## Results

| Metric | Sync (`requests.Session`) | Async (`httpx` + `asyncio`) |
| :--- | :---: | :---: |
| **Total Wall Time** | `[X.XX] s` | `[X.XX] s` |
| **Success Rate** | `[100.0]%` | `[100.0]%` |
| **Median Latency (per request)** | `[XXX.XX] ms` | `[XXX.XX] ms` |
| **p95 Latency (per request)** | `[XXX.XX] ms` | `[XXX.XX] ms` |

*Raw request-by-request logs are available in [`results.csv`](./results.csv).*

## Honest Takeaway
- **Wall time drops dramatically:** Async finished all 50 requests roughly `[X]x` faster than sync because it overlaps network I/O wait times instead of blocking sequentially.
- **The trade-off:** *[Fill in what your actual numbers show—for example: "Individual per-request median/p95 latency was slightly higher under async due to concurrent connection overhead, proving that async optimizes total throughput, not single-request speed."]*

## How to Reproduce
```bash
git clone [https://github.com/](https://github.com/)[your-username]/python-api-sync-vs-async-benchmark.git
cd python-api-sync-vs-async-benchmark
pip install -r requirements.txt
python benchmark.py
