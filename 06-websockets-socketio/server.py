from flask import Flask, render_template_string, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

INDEX = '''
<!doctype html>
<html>
  <body>
    <h3>WebSocket Chat (Flask-SocketIO)</h3>
    <input id="msg" placeholder="message"/>
    <button onclick="send()">Send</button>
    <ul id="log"></ul>
    <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
    <script>
      const socket = io();
      socket.on('chat', (m) => {
        const li = document.createElement('li');
        li.textContent = m;
        document.getElementById('log').appendChild(li);
      });
      function send(){
        const v = document.getElementById('msg').value;
        socket.emit('chat', v);
        document.getElementById('msg').value='';
      }
    </script>
  </body>
</html>
'''

@app.get("/")
def index():
    return render_template_string(INDEX)

@socketio.on('chat')
def on_chat(message):
    emit('chat', f"[{request.sid[:5]}] {message}", broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5004, debug=True)
