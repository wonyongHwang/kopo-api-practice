from spyne import Application, rpc, ServiceBase, Integer, Unicode
from spyne.protocol.soap import Soap11
from spyne.model.primitive import Boolean
from spyne.server.wsgi import WsgiApplication

class TodoService(ServiceBase):
    @rpc(Integer, Unicode, Boolean, _returns=Unicode)
    def add_todo(ctx, todo_id, title, done):
        # 실제 DB 대체: 단순 메시지 반환
        return f"Added: id={todo_id}, title={title}, done={done}"

    @rpc(Integer, _returns=Unicode)
    def get_todo(ctx, todo_id):
        return f"Todo(id={todo_id}, title='Demo', done=false)"

soap_app = Application([TodoService], 'api.todo.soap',
                       in_protocol=Soap11(validator='lxml'),
                       out_protocol=Soap11())

wsgi_app = WsgiApplication(soap_app)

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('0.0.0.0', 8000, wsgi_app)
    print("SOAP server listening on http://localhost:8000")
    server.serve_forever()
