# 01 - REST (Flask)

## 설치 & 실행
```bash
pip install -r requirements.txt
python app.py
```
- 목록: `GET http://localhost:5000/todos`
- 생성: `POST http://localhost:5000/todos` JSON: `{"title":"새 할일"}`
- 수정: `PUT http://localhost:5000/todos/1` JSON: `{"done": true}`
- 삭제: `DELETE http://localhost:5000/todos/1`
