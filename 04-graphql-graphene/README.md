# 04 - GraphQL (Flask + Graphene)

## 설치 & 실행
```bash
pip install -r requirements.txt
python app.py
```

## 예시 쿼리
- 목록 조회
```json
POST /graphql
{
  "query": "{ todos { id title done } }"
}
```
- 생성
```json
POST /graphql
{
  "query": "mutation($t:String!){ createTodo(title:$t){ ok todo{ id title done } } }",
  "variables": { "t": "새 할일" }
}
```
