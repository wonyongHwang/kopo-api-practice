# API Lab — 7가지 API 통신 방식 실습

Python을 이용해 **REST, SOAP, gRPC, GraphQL, Webhook, WebSocket, WebRTC**를 비교하고 직접 호출하는 실습 프로젝트입니다. 이 문서의 명령어는 **저장소 최상위 디렉터리에서 Docker Compose로 실행한 환경**을 기준으로 합니다.

> **주의:** 교육용 최소 예제입니다. 인증, 영속 저장, 입력 검증, 운영 보안 설정이 충분하지 않으므로 운영 환경에 그대로 배포하지 마세요. 아래 응답 예시는 컨테이너를 새로 실행한 초기 상태를 가정합니다.

## 목차

- [1. 프로젝트 구성](#1-프로젝트-구성)
- [2. 시작하기](#2-시작하기)
- [3. REST — Flask](#3-rest--flask)
- [4. SOAP — Spyne](#4-soap--spyne)
- [5. gRPC — Python](#5-grpc--python)
- [6. GraphQL — Graphene](#6-graphql--graphene)
- [7. Webhook — Flask](#7-webhook--flask)
- [8. WebSocket — Flask-SocketIO](#8-websocket--flask-socketio)
- [9. WebRTC — P2P 및 Signaling](#9-webrtc--p2p-및-signaling)
- [10. 프로토콜 비교](#10-프로토콜-비교)
- [11. Docker 관리 및 문제 해결](#11-docker-관리-및-문제-해결)

## 1. 프로젝트 구성

| 폴더 | 방식 | Docker 서비스명 | 호스트 포트 | 주요 경로·메서드 |
|---|---|---|---:|---|
| `01-rest-flask/` | REST / JSON | `rest` | 5001 | `GET/POST /todos`, `GET/PUT/DELETE /todos/{id}` |
| `02-soap-spyne/` | SOAP / XML | `soap` | 8000 | `GET /?wsdl`, `POST /` (`add_todo`, `get_todo`) |
| `03-grpc-python/` | gRPC / Protobuf | `grpc` | 50051 | `todo.TodoService/ListTodos`, `AddTodo` |
| `04-graphql-graphene/` | GraphQL / JSON | `graphql` | 5002 | `GET /`, `POST /graphql` |
| `05-webhooks-flask/` | HTTP Webhook | `webhooks` | 5003 | `POST /webhook` |
| `06-websockets-socketio/` | Socket.IO | `websockets` | 5004 | `GET /`, `/socket.io/`, 이벤트 `chat` |
| `07-webrtc-p2p/` | WebRTC + Socket.IO | `webrtc` | 5005 | `GET /`, `/socket.io/`, 이벤트 `signal` |

실제 포트 매핑은 저장소 루트의 `docker-compose.yml`을 따릅니다. 특히 REST는 컨테이너 내부 5000번이지만 **호스트에서는 5001번**으로 접속합니다.

## 2. 시작하기

### 사전 준비

- Docker Desktop 또는 Docker Engine + Docker Compose v2
- `curl`
- gRPC 테스트 시 `grpcurl` (선택)
- 브라우저 (WebSocket 및 WebRTC 실습)

```bash
# 저장소 루트에서 실행
# 전체 API 이미지 빌드 및 백그라운드 실행
docker compose up -d --build

# 실행 상태 확인
docker compose ps

# REST만 실행하려는 경우
docker compose up -d --build rest

# 전체 종료
docker compose down
```

> 최신 버전은 `docker-compose`(하이픈) 대신 `docker compose`(공백) 명령어를 권장합니다. `docker ps`가 실패한다면 Docker Engine이 실행 중인지 먼저 확인하세요.

---

## 3. REST — Flask

- **소스:** `01-rest-flask/app.py`
- **주소:** `http://localhost:5001`
- **특징:** HTTP 메서드와 리소스 경로로 CRUD 구현. 요청/응답은 JSON입니다.
- **적용 예:** 웹·모바일 백엔드, 관리자 API, 일반 CRUD 서비스.

| Method | Endpoint | 설명 | 성공 코드 |
|---|---|---|---|
| GET | `/todos` | 목록 조회 | 200 |
| GET | `/todos/{id}` | 단건 조회 | 200 |
| POST | `/todos` | 새 Todo 생성 | 201 |
| PUT | `/todos/{id}` | Todo 수정 | 200 |
| DELETE | `/todos/{id}` | Todo 삭제 | 204 |

```bash
# 목록 조회
curl -X GET http://localhost:5001/todos

# 단건 조회
curl -X GET http://localhost:5001/todos/1

# 생성: 초기 데이터가 유지되어 있다면 id=3
curl -X POST http://localhost:5001/todos \
  -H 'Content-Type: application/json' \
  -d '{"title":"Docker 실습하기"}'

# 수정 (위 생성된 id=3 가정)
curl -X PUT http://localhost:5001/todos/3 \
  -H 'Content-Type: application/json' \
  -d '{"title":"Docker 실습 완료","done":true}'

# 삭제 (위 생성된 id=3 가정)
curl -i -X DELETE http://localhost:5001/todos/3

# 없는 리소스: HTTP 404 확인
curl -i http://localhost:5001/todos/999
```

초기 목록:

```json
[
  {"id": 1, "title": "REST 실습 준비", "done": false},
  {"id": 2, "title": "Postman 설치", "done": true}
]
```

> Todo 데이터는 Python 메모리에 저장됩니다. 컨테이너 프로세스가 재시작되면 초기화됩니다.

---

## 4. SOAP — Spyne

- **소스:** `02-soap-spyne/server.py`
- **주소:** `http://localhost:8000/`
- **WSDL:** `http://localhost:8000/?wsdl`
- **네임스페이스:** `api.todo.soap`
- **특징:** SOAP Envelope(XML)로 RPC를 호출하며 WSDL로 서비스 명세를 확인할 수 있습니다.
- **적용 예:** 레거시 기업 시스템 및 계약 기반 시스템 연동.

| Method | 경로·동작 | 설명 |
|---|---|---|
| GET | `/?wsdl` | 서비스 명세 조회 |
| POST | `/` → `add_todo` | 매개변수 수신 후 결과 문자열 반환 |
| POST | `/` → `get_todo` | 샘플 결과 문자열 반환 |

```bash
# WSDL 조회
curl 'http://localhost:8000/?wsdl'

# macOS에서 XML 보기 좋게 출력 (xmllint 사용 가능 시)
curl -s 'http://localhost:8000/?wsdl' | xmllint --format -
```

**SOAP `add_todo` 호출**

```bash
curl -X POST http://localhost:8000/ \
  -H 'Content-Type: text/xml; charset=utf-8' \
  -H 'SOAPAction: "add_todo"' \
  --data-binary '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:todo="api.todo.soap">
  <soapenv:Body>
    <todo:add_todo>
      <todo:todo_id>1</todo:todo_id>
      <todo:title>SOAP 실습</todo:title>
      <todo:done>false</todo:done>
    </todo:add_todo>
  </soapenv:Body>
</soapenv:Envelope>'
```

**SOAP `get_todo` 호출**

```bash
curl -X POST http://localhost:8000/ \
  -H 'Content-Type: text/xml; charset=utf-8' \
  -H 'SOAPAction: "get_todo"' \
  --data-binary '<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:todo="api.todo.soap">
  <soapenv:Body>
    <todo:get_todo>
      <todo:todo_id>1</todo:todo_id>
    </todo:get_todo>
  </soapenv:Body>
</soapenv:Envelope>'
```

> **구현 범위:** `add_todo`는 실제 DB에 저장하지 않고 `Added: ...`라는 문자열만 반환합니다. `get_todo` 역시 실제 조회 없이 `Todo(id=..., title='Demo', done=false)`라는 샘플 문자열을 반환합니다. 서버의 WSDL에 정의된 XML 스키마에 맞춰 요청해야 합니다.

---

## 5. gRPC — Python

- **소스:** `03-grpc-python/server.py`, `03-grpc-python/todo.proto`
- **주소:** `localhost:50051` (HTTP REST 경로가 아닌 gRPC 서비스)
- **특징:** HTTP/2와 Protocol Buffers로 정의된 RPC를 호출합니다.
- **적용 예:** 내부 마이크로서비스, 강한 타입 계약을 사용하는 서비스 간 통신.

프로젝트의 `todo.proto`:

```protobuf
syntax = "proto3";
package todo;

service TodoService {
  rpc ListTodos (Empty) returns (TodoList) {}
  rpc AddTodo (NewTodo) returns (Todo) {}
}
```

| RPC | 입력 | 출력 | 기능 |
|---|---|---|---|
| `todo.TodoService/ListTodos` | `Empty` | `TodoList` | 목록 조회 |
| `todo.TodoService/AddTodo` | `NewTodo` | `Todo` | 추가 |

**grpcurl 설치**

```bash
# macOS
brew install grpcurl

```

```bash
# Linux (Ubuntu)
ARCH=$(dpkg --print-architecture)
VER=1.9.4
FILE="grpcurl_${VER}_linux_${ARCH}.deb"
curl -fLO "https://github.com/fullstorydev/grpcurl/releases/download/v$VER/$FILE"
sudo apt install "./$FILE"
grpcurl -version
```

**요청 예제** — 저장소 루트에서 실행:

```bash
# proto 파일을 지정해 서비스 및 메서드 확인
# 서버에 Reflection이 구현되어 있지 않으므로 -proto 옵션이 필요
grpcurl -plaintext \
  -import-path ./03-grpc-python -proto todo.proto \
  localhost:50051 list

grpcurl -plaintext \
  -import-path ./03-grpc-python -proto todo.proto \
  localhost:50051 list todo.TodoService

# 목록 조회
grpcurl -plaintext \
  -import-path ./03-grpc-python -proto todo.proto \
  -d '{}' localhost:50051 todo.TodoService/ListTodos

# Todo 추가
grpcurl -plaintext \
  -import-path ./03-grpc-python -proto todo.proto \
  -d '{"title":"gRPC 실습하기"}' \
  localhost:50051 todo.TodoService/AddTodo
```

초기 목록에는 `id=1`, `title="gRPC 실습 준비"`, `done=false`인 Todo가 있습니다. Protobuf JSON 출력은 기본값 필드(`false` 등)를 생략할 수 있습니다. `grpcurl -emit-defaults` 옵션으로 출력할 수 있습니다.

`curl`로 원시 gRPC 프레임을 보내는 심화 예제 (응답은 바이너리):

```bash
# curl이 HTTP/2 prior knowledge 기능을 지원하는 경우
printf '\x00\x00\x00\x00\x00' | \
  curl --http2-prior-knowledge -s \
    -H 'Content-Type: application/grpc' \
    -H 'TE: trailers' \
    --data-binary @- \
    http://localhost:50051/todo.TodoService/ListTodos | xxd
```

> 일반적인 `curl`은 Protobuf 응답 해석까지 제공하지 않으므로 **`grpcurl` 사용을 권장**합니다. gRPC는 Unary 외에도 스트리밍 RPC를 지원하지만, 이 프로젝트의 두 RPC는 모두 Unary입니다.

---

## 6. GraphQL — Graphene

- **소스:** `04-graphql-graphene/app.py`
- **주소:** `http://localhost:5002/graphql`
- **특징:** 하나의 Endpoint에서 Query·Mutation을 수행하며 클라이언트가 반환 필드를 선택합니다.
- **적용 예:** 화면별 데이터 요구사항이 다양한 웹·모바일 앱.

| Method | 경로 | 기능 |
|---|---|---|
| GET | `/` | `POST /graphql` 안내 문자열 |
| POST | `/graphql` | `todos` Query, `createTodo` Mutation |

```bash
# 기본 안내
curl http://localhost:5002/

# 전체 필드 목록 조회
curl -X POST http://localhost:5002/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ todos { id title done } }"}'

# title만 반환받기
curl -X POST http://localhost:5002/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ todos { title } }"}'

# 새로운 Todo 추가
curl -X POST http://localhost:5002/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation { createTodo(title: \"GraphQL 실습하기\") { ok todo { id title done } } }"}'

# GraphQL Variables를 사용한 생성
curl -X POST http://localhost:5002/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"mutation Create($title: String!) { createTodo(title: $title) { ok todo { id title done } } }", "variables":{"title":"Variables 실습"}}'

# Schema introspection (쿼리 및 뮤테이션 이름)
curl -X POST http://localhost:5002/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ __schema { queryType { name fields { name } } mutationType { name fields { name } } } }"}'

# 존재하지 않는 필드 요청 → GraphQL 오류
curl -i -X POST http://localhost:5002/graphql \
  -H 'Content-Type: application/json' \
  -d '{"query":"{ todos { id price } }"}'
```

> Python 클래스 속성은 `create_todo`이지만 Graphene의 자동 camelCase 변환으로 GraphQL API에서는 **`createTodo`**로 호출합니다. 초기 데이터는 `GraphQL 실습 준비` Todo 한 건이며 메모리에 저장됩니다.

---

## 7. Webhook — Flask

- **소스:** `05-webhooks-flask/server.py`
- **주소:** `http://localhost:5003/webhook`
- **특징:** 외부 시스템이 특정 이벤트 발생 시 등록된 수신 URL로 HTTP 요청을 보냅니다. 이 예제는 요청의 `X-Event-Name` 헤더와 JSON 본문을 로그로 출력합니다.
- **적용 예:** 결제 완료, 코드 Push 알림, 주문 상태 변경.

```bash
# Todo 생성 이벤트
curl -X POST http://localhost:5003/webhook \
  -H 'Content-Type: application/json' \
  -H 'X-Event-Name: todo.created' \
  -d '{"id":1,"title":"Webhook 실습","done":false}'

# 결제 완료 이벤트 (실습용 가상 데이터)
curl -X POST http://localhost:5003/webhook \
  -H 'Content-Type: application/json' \
  -H 'X-Event-Name: payment.completed' \
  -d '{"payment_id":"PAY-001","amount":35000,"currency":"KRW","status":"completed"}'

# X-Event-Name 생략: event = unknown
curl -X POST http://localhost:5003/webhook \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hello Webhook"}'

# 이벤트 로그 확인
docker compose logs -f webhooks
```

응답 예:

```json
{"received": true, "event": "todo.created"}
```

> 이 예제는 이벤트를 **수신**하기만 합니다. 실제 외부 Webhook 공급자 등록·서명 검증·재시도·비동기 처리는 구현되어 있지 않습니다.

---

## 8. WebSocket — Flask-SocketIO

- **소스:** `06-websockets-socketio/server.py`
- **주소:** `http://localhost:5004/`
- **특징:** Socket.IO를 통해 `chat` 이벤트를 주고받으며 서버가 모든 연결 사용자에게 메시지를 브로드캐스트합니다.
- **적용 예:** 채팅, 실시간 알림, 공동 편집.

| 경로·이벤트 | 용도 |
|---|---|
| `GET /` | 채팅 HTML 페이지 |
| `/socket.io/` | Engine.IO/Socket.IO 연결 |
| `chat` | 채팅 전송 및 브로드캐스트 |

```bash
# HTML 페이지 확인
curl http://localhost:5004/

# Socket.IO polling 연결 핸드셰이크 확인
curl 'http://localhost:5004/socket.io/?EIO=4&transport=polling'
```

**curl로 Socket.IO 이벤트 전송 실습:** 이 예제는 WebSocket 자체가 아니라 Socket.IO의 **HTTP polling 전송**을 사용합니다. 동일한 터미널에서 순서대로 실행하고, 연결이 타임아웃되지 않도록 주의하세요.

```bash
# 1. Engine.IO session ID 획득
SID=$(curl -s 'http://localhost:5004/socket.io/?EIO=4&transport=polling' \
  | cut -c 2- | python3 -c 'import sys,json; print(json.load(sys.stdin)["sid"])')
echo "$SID"

# 2. Socket.IO 기본 네임스페이스 연결 (40)
curl -X POST "http://localhost:5004/socket.io/?EIO=4&transport=polling&sid=$SID" \
  -H 'Content-Type: text/plain' --data-binary '40'

# 3. 연결 승인 패킷 확인
curl "http://localhost:5004/socket.io/?EIO=4&transport=polling&sid=$SID"

# 4. chat 이벤트 전송 (42[이벤트,데이터])
curl -X POST "http://localhost:5004/socket.io/?EIO=4&transport=polling&sid=$SID" \
  -H 'Content-Type: text/plain' \
  --data-binary '42["chat","Hello WebSocket"]'

# 5. 반환 메시지 polling (필요하면 여러 번 확인)
curl --max-time 5 "http://localhost:5004/socket.io/?EIO=4&transport=polling&sid=$SID"
```

응답 예: `42["chat","[abc12] Hello WebSocket"]` (세션 식별자 앞 5자는 매번 달라집니다).

**권장 실습:** 브라우저 두 개에서 `http://localhost:5004/`를 열고 한쪽에서 메시지를 보내 양쪽에 표시되는지 확인합니다. 이 방법이 실시간 양방향 통신을 체감하기에 좋습니다.

---

## 9. WebRTC — P2P 및 Signaling

- **소스:** `07-webrtc-p2p/signaling_server.py`
- **주소:** `http://localhost:5005/`
- **특징:** Socket.IO는 Offer·Answer·ICE Candidate **시그널링만 중계**합니다. 실제 미디어 통신은 `RTCPeerConnection`으로 수행합니다.
- **적용 예:** 화상 회의, 음성 통화, P2P 실시간 서비스.

| 경로·이벤트 | 용도 |
|---|---|
| `GET /` | 영상 통화 HTML 페이지 |
| `/socket.io/` | 시그널링 연결 |
| `signal` + `offer` | SDP 연결 제안 |
| `signal` + `answer` | SDP 연결 응답 |
| `signal` + `candidate` | ICE 연결 후보 전달 |

```bash
# 브라우저 HTML 확인
curl http://localhost:5005/

# Socket.IO 시그널링 엔진 핸드셰이크
curl 'http://localhost:5005/socket.io/?EIO=4&transport=polling'
```

**curl로 시그널링 메시지 형식 확인:**

```bash
# 1. 세션 발급
SID=$(curl -s 'http://localhost:5005/socket.io/?EIO=4&transport=polling' \
  | cut -c 2- | python3 -c 'import sys,json; print(json.load(sys.stdin)["sid"])')

# 2. Socket.IO 연결
curl -X POST "http://localhost:5005/socket.io/?EIO=4&transport=polling&sid=$SID" \
  -H 'Content-Type: text/plain' --data-binary '40'

# 3. 연결 승인 확인
curl "http://localhost:5005/socket.io/?EIO=4&transport=polling&sid=$SID"

# 4. Offer 형식 전송 (가짜 SDP: 실제 P2P 연결 불가)
curl -X POST "http://localhost:5005/socket.io/?EIO=4&transport=polling&sid=$SID" \
  -H 'Content-Type: text/plain' \
  --data-binary '42["signal",{"type":"offer","sdp":"DEMO_SDP"}]'

# 5. Answer 형식 전송 (가짜 SDP)
curl -X POST "http://localhost:5005/socket.io/?EIO=4&transport=polling&sid=$SID" \
  -H 'Content-Type: text/plain' \
  --data-binary '42["signal",{"type":"answer","sdp":"DEMO_SDP"}]'

# 6. ICE Candidate 형식 전송 (가짜 Candidate)
curl -X POST "http://localhost:5005/socket.io/?EIO=4&transport=polling&sid=$SID" \
  -H 'Content-Type: text/plain' \
  --data-binary '42["signal",{"type":"candidate","candidate":{"candidate":"DEMO_CANDIDATE","sdpMid":"0","sdpMLineIndex":0}}]'
```

> 위 문자열은 **시그널링 형식 학습용 가짜 데이터**입니다. `curl`만으로 실제 WebRTC 미디어 연결은 성립하지 않습니다. 서버가 이벤트를 다른 클라이언트로 브로드캐스트하므로, 실제 통화 중인 사용자에게 가짜 메시지를 보내지 마세요.

**권장 브라우저 실습:**

1. `http://localhost:5005/`를 서로 다른 브라우저 탭 두 개에서 엽니다.
2. 양쪽에서 **Start**를 눌러 카메라·마이크 접근을 허용합니다.
3. 한쪽에서 **Call**을 눌러 SDP Offer를 생성합니다.
4. 상대편은 Offer를 받아 자동으로 Answer를 생성합니다.
5. ICE Candidate를 교환한 뒤 영상·음성 연결을 확인합니다.
6. **Hang Up**으로 종료합니다.

> 로컬 `localhost` 환경에서 테스트하는 것이 간단합니다. 실제 타 기기 접속은 HTTPS 등 보안 컨텍스트, 방화벽, 네트워크 조건에 따라 달라집니다. 이 소스는 Google STUN 서버만 설정했고 TURN 서버·방 관리·접속 인증은 구현하지 않았습니다. `Hang Up` 이후 재접속을 위해서는 페이지를 새로 고쳐야 할 수 있습니다.

---

## 10. 프로토콜 비교

| 방식 | 핵심 통신 특성 | 데이터·메시지 형식 | 적합한 용도 | 실습 도구 |
|---|---|---|---|---|
| REST | 리소스 중심 HTTP 요청/응답 | JSON | CRUD, 공개·모바일 API | `curl` |
| SOAP | WSDL로 기술되는 계약 기반 RPC | SOAP XML | 레거시·기업 간 연동 | `curl`, SoapUI |
| gRPC | Protobuf 기반 RPC, HTTP/2 | 바이너리 Protobuf | 내부 서비스 간 통신 | `grpcurl` |
| GraphQL | 클라이언트가 필드 선택, Query·Mutation | GraphQL + JSON | 복합 데이터 조회 | `curl` |
| Webhook | 이벤트 발행자가 수신 URL로 요청 | 일반적으로 POST + JSON | 결제·상태 변화 알림 | `curl` |
| Socket.IO | 이벤트 기반 양방향 통신 | Socket.IO 이벤트 프레임 | 채팅·실시간 알림 | 브라우저, Socket.IO 클라이언트 |
| WebRTC | SDP/ICE 시그널링 후 P2P 미디어 | 음성·영상·데이터 | 화상통화·음성통화 | 브라우저 |

- **REST vs GraphQL:** REST는 경로와 HTTP 메서드로 동작을 구분하는 반면, GraphQL은 보통 한 경로에서 조회·변경 요청과 반환 필드를 기술합니다.
- **SOAP vs gRPC:** SOAP은 XML 기반 메시지와 WSDL 중심이고, gRPC는 Protobuf 스키마와 생성된 클라이언트 코드를 활용합니다.
- **Webhook vs WebSocket:** Webhook은 이벤트가 발생했을 때 HTTP로 통지하고, WebSocket/Socket.IO는 연결을 유지하며 실시간 상호작용합니다.
- **WebSocket vs WebRTC:** WebSocket은 주로 애플리케이션 메시지 교환에, WebRTC는 실시간 미디어·P2P 데이터 통신에 사용합니다. 본 예제는 WebRTC 연결 협상을 위해 Socket.IO를 별도로 이용합니다.

## 11. Docker 관리 및 문제 해결

```bash
# 전체/개별 실행
docker compose up -d --build
docker compose up -d --build rest

# 실행 상태 및 로그
docker compose ps
docker compose logs -f
docker compose logs -f rest
docker compose logs -f soap
docker compose logs -f grpc
docker compose logs -f graphql
docker compose logs -f webhooks
docker compose logs -f websockets
docker compose logs -f webrtc

# 컨테이너 재시작 / 종료
docker compose restart rest
docker compose stop rest
docker compose down
```

**자주 발생하는 문제**

| 증상 | 점검 사항 |
|---|---|
| `Error while fetching server API version` | Docker Desktop/Engine 실행 상태(`docker ps`), Compose v2(`docker compose version`) 확인 |
| REST에 `localhost:5000` 접속 실패 | Compose의 호스트 포트는 **5001**입니다. `http://localhost:5001/todos` 사용 |
| `grpcurl`이 서비스에 접근하지 못함 | gRPC 서버 실행 확인, `-plaintext`, `-proto todo.proto`, `-import-path` 지정 |
| GraphQL 필드 오류 | 스키마에 존재하는 필드만 조회. Python `create_todo`의 GraphQL 이름은 `createTodo` |
| Socket.IO `unknown sid` | 연결이 만료되었거나 세션 ID가 바뀜. 핸드셰이크부터 다시 시작 |
| WebRTC 영상이 보이지 않음 | 브라우저 권한, HTTPS/localhost 보안 컨텍스트, ICE 연결·방화벽 확인 |

### 실습 관련 주의

- REST, gRPC, GraphQL의 Todo 목록은 각각 **독립적인 메모리 저장소**입니다. 서로 데이터가 공유되지 않습니다.
- SOAP의 `add_todo`는 DB에 저장하지 않습니다.
- Webhook 수신 서버는 요청 이벤트를 **로그로 출력**할 뿐 다른 API를 호출하지 않습니다.
- WebSocket·WebRTC 예제는 인증과 사용자별 방 분리가 없는 간단한 데모입니다.
- Docker Compose의 서비스명을 기준으로 `docker compose logs -f <서비스명>` 명령어를 사용합니다.

---
