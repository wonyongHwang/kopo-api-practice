# 03 - gRPC (Python)

## 설치
```bash
pip install -r requirements.txt
```

## 프로토 코드 생성
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. todo.proto
```

## 실행
- 서버: `python server.py`
- 클라이언트: `python client.py`
