# Docker 실행 가이드

## 0) 단일 서비스 빌드 & 실행 예시 (REST)
```bash
cd 01-rest-flask
docker build -t api-lab-rest .
docker run --rm -p 5000:5000 api-lab-rest
```

## 1) docker-compose로 한 번에 실행
```bash
docker compose build
docker compose up
```
- REST: http://localhost:5000
- SOAP(WSDL): http://localhost:8000/?wsdl
- gRPC: localhost:50051 (클라이언트 필요)
- GraphQL: POST http://localhost:5002/graphql
- WebHooks: http://localhost:5003/webhook
- WebSockets: http://localhost:5004
- WebRTC: http://localhost:5005
```

## 2) 종료
```bash
docker compose down
```
