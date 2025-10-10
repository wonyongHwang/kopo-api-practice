import grpc
from concurrent import futures
import time

import todo_pb2, todo_pb2_grpc

todos = [
    todo_pb2.Todo(id=1, title="gRPC 실습 준비", done=False),
]

class TodoService(todo_pb2_grpc.TodoServiceServicer):
    def ListTodos(self, request, context):
        return todo_pb2.TodoList(items=todos)

    def AddTodo(self, request, context):
        new_id = max([t.id for t in todos] or [0]) + 1
        t = todo_pb2.Todo(id=new_id, title=request.title, done=False)
        todos.append(t)
        return t

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    todo_pb2_grpc.add_TodoServiceServicer_to_server(TodoService(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server on 0.0.0.0:50051")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
