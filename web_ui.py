from flask import Flask, render_template_string, request, redirect, url_for
import json
import os

from codex_clone import run_agent_task

app = Flask(__name__)
TASKS_FILE = "tasks.json"


def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE) as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        description = request.form["description"]
        diff = run_agent_task(description)
        task = {
            "id": len(load_tasks()) + 1,
            "description": description,
            "diff": diff,
            "pr": None,
        }
        tasks = load_tasks()
        tasks.insert(0, task)
        save_tasks(tasks)
        return redirect(url_for("index"))
    tasks = load_tasks()
    return render_template_string(INDEX_TEMPLATE, tasks=tasks)


@app.route("/task/<int:task_id>")
def task_detail(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return "Task not found", 404
    return render_template_string(TASK_TEMPLATE, task=task)


@app.route("/task/<int:task_id>/create_pr", methods=["POST"])
def create_pr(task_id):
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if not task:
        return "Task not found", 404
    if not task.get("pr"):
        # In a real setup, integrate with GitHub or other PR system here
        task["pr"] = f"PR for task {task_id}"
        save_tasks(tasks)
    return redirect(url_for("task_detail", task_id=task_id))


INDEX_TEMPLATE = """
<!doctype html>
<title>Tasks</title>
<h1>Tasks</h1>
<form method="post">
  <input name="description" placeholder="New task" required>
  <button type="submit">Add</button>
</form>
<ul>
{% for task in tasks %}
  <li><a href="{{ url_for('task_detail', task_id=task.id) }}">Task {{ task.id }}: {{ task.description }}</a></li>
{% else %}
  <li>No tasks yet.</li>
{% endfor %}
</ul>
"""

TASK_TEMPLATE = """
<!doctype html>
<title>Task {{ task.id }}</title>
<h1>Task {{ task.id }}</h1>
<p>{{ task.description }}</p>
<h2>Diff</h2>
<pre style="background:#f8f8f8;padding:1em;">{{ task.diff }}</pre>
{% if task.pr %}
<p>PR: {{ task.pr }}</p>
{% else %}
<form method="post" action="{{ url_for('create_pr', task_id=task.id) }}">
  <button type="submit">Create PR</button>
</form>
{% endif %}
<p><a href="{{ url_for('index') }}">Back</a></p>
"""

if __name__ == "__main__":
    app.run(debug=True)
