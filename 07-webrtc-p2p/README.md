# 07 - WebRTC (브라우저 + 간단 시그널링)

## 개요
- 브라우저 두 개(같은 PC의 서로 다른 창 또는 다른 기기)에서 접속하여 영상/음성 P2P 연결
- 시그널링은 Flask-SocketIO로 매우 단순화(모든 사용자에게 브로드캐스트)

## 실행
```bash
pip install -r requirements.txt
python signaling_server.py
```
- 두 브라우저에서 `http://localhost:5005` 접속
- 각 창에서 `Start` → 한 쪽에서 `Call` → 다른 쪽에 자동으로 `Answer` 처리
- 카메라/마이크 권한 허용 필요
