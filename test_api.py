"""Automated tests for Q1 (API) - run with: python -m unittest -v"""
import os
import tempfile
import unittest

os.environ["TASKS_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
import app as task_app  # noqa: E402


class TaskApiTests(unittest.TestCase):
    def setUp(self):
        task_app.initialize_db()
        self.c = task_app.app.test_client()

    def test_full_crud(self):
        r = self.c.post("/tasks", json={"title": "Complete practical exam"})
        self.assertEqual(r.status_code, 201)
        tid = r.get_json()["id"]
        self.assertEqual(r.get_json()["status"], "pending")
        self.assertEqual(self.c.get("/tasks").status_code, 200)
        self.assertEqual(self.c.get(f"/tasks/{tid}").get_json()["title"], "Complete practical exam")
        r = self.c.put(f"/tasks/{tid}", json={"title": "Exam completed", "status": "completed"})
        self.assertEqual(r.get_json()["status"], "completed")
        self.assertEqual(self.c.delete(f"/tasks/{tid}").status_code, 200)
        self.assertEqual(self.c.get(f"/tasks/{tid}").status_code, 404)

    def test_validation(self):
        self.assertEqual(self.c.post("/tasks", json={}).status_code, 400)
        self.assertEqual(self.c.post("/tasks", json={"title": "   "}).status_code, 400)
        self.assertEqual(self.c.post("/tasks", json={"title": 5}).status_code, 400)
        self.assertEqual(self.c.put("/tasks/1", json={"title": "x", "status": "bad"}).status_code, 400)

    def test_not_found(self):
        self.assertEqual(self.c.get("/tasks/99999").status_code, 404)
        self.assertEqual(self.c.delete("/tasks/99999").status_code, 404)
        self.assertEqual(self.c.put("/tasks/99999", json={"title": "x", "status": "pending"}).status_code, 404)


if __name__ == "__main__":
    unittest.main()
