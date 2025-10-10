import grpc
import todo_pb2, todo_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = todo_pb2_grpc.TodoServiceStub(channel)

    print("== List ==")
    resp = stub.ListTodos(todo_pb2.Empty())
    for t in resp.items:
        print(t)

    print("== Add ==")
    new = stub.AddTodo(todo_pb2.NewTodo(title="새 작업"))
    print("added:", new)

    print("== List again ==")
    resp2 = stub.ListTodos(todo_pb2.Empty())
    for t in resp2.items:
        print(t)

if __name__ == "__main__":
    run()
