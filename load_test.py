"""Q3: simple load test (JMeter alternative). Usage: python load_test.py [url] [threads] [loops]"""
import statistics
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

URL = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000/tasks"
THREADS = int(sys.argv[2]) if len(sys.argv) > 2 else 10
LOOPS = int(sys.argv[3]) if len(sys.argv) > 3 else 10


def worker(_):
    times, errors = [], 0
    for _ in range(LOOPS):
        t = time.perf_counter()
        try:
            with urllib.request.urlopen(URL, timeout=10) as r:
                ok = r.status == 200
                r.read()
        except Exception:
            ok = False
        times.append((time.perf_counter() - t) * 1000)
        errors += 0 if ok else 1
    return times, errors


start = time.perf_counter()
with ThreadPoolExecutor(THREADS) as ex:
    results = list(ex.map(worker, range(THREADS)))
elapsed = time.perf_counter() - start

all_t = sorted(t for ts, _ in results for t in ts)
total = len(all_t)
errors = sum(e for _, e in results)
print(f"URL:                  {URL}")
print(f"Total requests:       {total}")
print(f"Successful:           {total - errors}")
print(f"Failed:               {errors}  ({errors / total * 100:.1f}% error)")
print(f"Average response:     {statistics.mean(all_t):.2f} ms")
print(f"Median / 95th pct:    {statistics.median(all_t):.2f} ms / {all_t[int(total * 0.95) - 1]:.2f} ms")
print(f"Min / Max:            {all_t[0]:.2f} ms / {all_t[-1]:.2f} ms")
print(f"Throughput:           {total / elapsed:.1f} requests/sec")
