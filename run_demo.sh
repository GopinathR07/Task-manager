#!/usr/bin/env bash
# One-command demo of Q1, Q3, Q4. Usage: bash run_demo.sh   (Windows: use Git Bash/WSL)
set -e
rm -f tasks.db
python app.py > server.log 2>&1 & PID=$!
sleep 2; B=http://127.0.0.1:5000
echo "== Q1 CRUD =="
curl -s -i -X POST $B/tasks -H "Content-Type: application/json" -d '{"title":"Complete practical exam"}' | head -1
curl -s $B/tasks; curl -s $B/tasks/1
curl -s -X PUT $B/tasks/1 -H "Content-Type: application/json" -d '{"title":"Exam completed","status":"completed"}'
curl -s -w "HTTP %{http_code}\n" -X POST $B/tasks -H "Content-Type: application/json" -d '{}'
curl -s -w "HTTP %{http_code}\n" $B/tasks/999
curl -s -X DELETE $B/tasks/1
echo "== Q3 timing + load =="
curl -s -w "HTTP Status: %{http_code}\nTime: %{time_total}s\n" -o /dev/null $B/tasks
python load_test.py
kill $PID
echo "== Q1 tests =="; python -m unittest 2>&1 | tail -3
echo "== Q4 pipeline =="; python pipeline.py
