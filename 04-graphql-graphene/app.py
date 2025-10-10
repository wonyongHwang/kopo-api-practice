from flask import Flask, request, jsonify
import graphene

class Todo(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    done = graphene.Boolean()

# in-memory
TODOS = [
    {"id": 1, "title": "GraphQL 실습 준비", "done": False}
]

class Query(graphene.ObjectType):
    todos = graphene.List(Todo)

    def resolve_todos(root, info):
        return TODOS

class CreateTodo(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
    ok = graphene.Boolean()
    todo = graphene.Field(lambda: Todo)

    def mutate(root, info, title):
        new_id = max([t["id"] for t in TODOS] or [0]) + 1
        t = {"id": new_id, "title": title, "done": False}
        TODOS.append(t)
        return CreateTodo(ok=True, todo=t)

class Mutation(graphene.ObjectType):
    create_todo = CreateTodo.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

app = Flask(__name__)

def _format_error(err):
    # GraphQLError는 .formatted를 제공합니다.
    return getattr(err, "formatted", {"message": str(err)})

@app.post("/graphql")
def graphql_endpoint():
    payload = request.get_json(silent=True) or {}
    query = payload.get("query")
    variables = payload.get("variables")

    if not query:
        return jsonify({"errors": [{"message": "Missing 'query'"}]}), 400

    # Graphene 3에서는 execute / execute_sync 모두 사용 가능
    result = schema.execute(query, variable_values=variables)
    # result: ExecutionResult(data=<dict or None>, errors=<list or None>)

    resp = {}
    if result.errors:
        resp["errors"] = [_format_error(e) for e in result.errors]
    if result.data is not None:
        resp["data"] = result.data

    return jsonify(resp), (400 if result.errors else 200)
    
@app.get("/")
def index():
    return "POST /graphql"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
