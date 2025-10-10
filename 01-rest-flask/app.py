from flask import Flask, request, jsonify

app = Flask(__name__)

# 메모리 내 간단 DB
todos = [
    {"id": 1, "title": "REST 실습 준비", "done": False},
    {"id": 2, "title": "Postman 설치", "done": True},
]

@app.get("/todos")
def list_todos():
    return jsonify(todos)

@app.get("/todos/<int:todo_id>")
def get_todo(todo_id):
    for t in todos:
        if t["id"] == todo_id:
            return jsonify(t)
    return jsonify({"error": "Not found"}), 404

@app.post("/todos")
def create_todo():
    data = request.get_json(force=True)
    new_id = max([t["id"] for t in todos] or [0]) + 1
    todo = {"id": new_id, "title": data.get("title", ""), "done": False}
    todos.append(todo)
    return jsonify(todo), 201

@app.put("/todos/<int:todo_id>")
def update_todo(todo_id):
    data = request.get_json(force=True)
    for t in todos:
        if t["id"] == todo_id:
            t["title"] = data.get("title", t["title"])
            t["done"] = data.get("done", t["done"])
            return jsonify(t)
    return jsonify({"error": "Not found"}), 404

@app.delete("/todos/<int:todo_id>")
def delete_todo(todo_id):
    global todos
    before = len(todos)
    todos = [t for t in todos if t["id"] != todo_id]
    if len(todos) == before:
        return jsonify({"error": "Not found"}), 404
    return "", 204

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
