from flask import Flask, render_template_string
from flask_socketio import SocketIO, emit, join_room, leave_room

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

INDEX = '''
<!doctype html>
<html>
<head><meta charset="utf-8"><title>WebRTC Demo</title></head>
<body>
  <h3>WebRTC P2P (Simple)</h3>
  <video id="local" autoplay playsinline muted style="width:45%;border:1px solid #ccc;"></video>
  <video id="remote" autoplay playsinline style="width:45%;border:1px solid #ccc;"></video>
  <div>
    <button id="start">Start</button>
    <button id="call">Call</button>
    <button id="hangup">Hang Up</button>
  </div>
  <script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
  <script>
    const pc = new RTCPeerConnection({
      iceServers: [{urls: 'stun:stun.l.google.com:19302'}]
    });
    const socket = io();
    let localStream;

    pc.ontrack = (e) => {
      document.getElementById('remote').srcObject = e.streams[0];
    };

    pc.onicecandidate = ({candidate}) => {
      if(candidate) socket.emit('signal', {type:'candidate', candidate});
    };

    document.getElementById('start').onclick = async () => {
      localStream = await navigator.mediaDevices.getUserMedia({audio:true, video:true});
      document.getElementById('local').srcObject = localStream;
      localStream.getTracks().forEach(t => pc.addTrack(t, localStream));
    };

    document.getElementById('call').onclick = async () => {
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      socket.emit('signal', {type:'offer', sdp: offer.sdp});
    };

    document.getElementById('hangup').onclick = () => {
      pc.getSenders().forEach(s => s.track && s.track.stop());
      socket.disconnect();
    };

    socket.on('signal', async (msg) => {
      if(msg.type === 'offer'){
        await pc.setRemoteDescription({type:'offer', sdp: msg.sdp});
        const answer = await pc.createAnswer();
        await pc.setLocalDescription(answer);
        socket.emit('signal', {type:'answer', sdp: answer.sdp});
      } else if(msg.type === 'answer'){
        await pc.setRemoteDescription({type:'answer', sdp: msg.sdp});
      } else if(msg.type === 'candidate'){
        try { await pc.addIceCandidate(msg.candidate); } catch(e){ console.error(e); }
      }
    });
  </script>
</body>
</html>
'''

@app.get("/")
def index():
    return render_template_string(INDEX)

@socketio.on('signal')
def on_signal(msg):
    # 간단 브로드캐스트(동일 룸 없이 모든 클라이언트 간 테스트 용)
    emit('signal', msg, broadcast=True, include_self=False)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5005, debug=True)
