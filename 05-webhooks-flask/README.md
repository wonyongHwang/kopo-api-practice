# 05 - WebHooks (Flask)

## 설치 & 실행
```bash
pip install -r requirements.txt
python server.py
```

## 테스트
```bash
curl -X POST http://localhost:5003/webhook \
  -H "Content-Type: application/json" \
  -H "X-Event-Name: demo.push" \
  -d '{"repo":"example","action":"push"}'
```
