# Task Practical - Backend, DevOps & Data Engineering

Stack: Python 3.12, Flask, SQLite, Docker, GitHub Actions, HTML/JS.

## Setup (VS Code terminal)
```
python -m venv .venv
.venv\Scripts\Activate.ps1          # Windows PowerShell
# source .venv/bin/activate         # macOS/Linux
pip install -r requirements.txt
```

## Q1  REST API
```
python app.py                        # http://127.0.0.1:5000
python -m unittest -v                # automated tests (3 pass)
```
| Method | URL | Success | Errors |
|---|---|---|---|
| POST | /tasks `{"title":"x"}` | 201 | 400 empty title |
| GET | /tasks | 200 | |
| GET | /tasks/<id> | 200 | 404 |
| PUT | /tasks/<id> `{"title","status"}` | 200 | 400 / 404 |
| DELETE | /tasks/<id> | 200 | 404 |
| GET | /health | 200 | |

## Q2  Docker + CI/CD
```
docker build -t task-api .
docker run --rm -p 5000:5000 task-api
curl -i http://127.0.0.1:5000/tasks      # 200 and []
git init && git add . && git commit -m "Task API" && git branch -M main
git remote add origin YOUR_REPO_URL && git push -u origin main
```
GitHub Actions: `ci.yml` (syntax, tests, docker build) and `data-pipeline.yml`.

## Q3  Performance / observability
```
curl -w "\nHTTP Status: %{http_code}\nTime: %{time_total}s\n" -o /dev/null http://127.0.0.1:5000/tasks
python load_test.py                       # 10 users x 10 loops (or: python load_test.py URL THREADS LOOPS)
```
Every request is logged with its latency in the server terminal and sent back in the `X-Response-Time-ms` header.
Record YOUR measured numbers; they differ per machine.

## Q4  Data pipeline
```
python pipeline.py                        # input.csv -> output.json (+ rejected.json)
```
Exit code is 1 if no valid rows (quality gate for CI).

## Q5  Frontend
```
python app.py                             # terminal 1
python -m http.server 8000                # terminal 2 -> open http://127.0.0.1:8000
```
Test: add task, empty title, Complete/Edit/Delete, stop API (error message), restart (recovery).

Or run everything at once: `bash run_demo.sh`
