# 3주차 실습직무 - 강사 가능시간 API

Python, FastAPI, Uvicorn, MySQL을 사용하여 강사 가능시간 DB와 조회 API를 구현한 실습입니다.

## 폴더 구성

```text
backend/
  app/
    db.py
    main.py
  docs/
    api_spec.md
    feedback_response.md
    table_definition.md
    tutor_available_time_sample.csv
  sql/
    01_schema.sql
    02_seed.sql
  .env.example
  requirements.txt
```

## 실행 순서

1. 패키지를 설치합니다.

```bash
pip install -r requirements.txt
```

2. `.env.example`을 참고하여 `.env` 파일을 생성합니다.

```text
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=본인 MySQL 비밀번호
DB_NAME=dozon_internship
```

3. MySQL에서 SQL 파일을 순서대로 실행합니다.

```bash
mysql --default-character-set=utf8mb4 -u root -p -e "source sql/01_schema.sql"
mysql --default-character-set=utf8mb4 -u root -p -e "source sql/02_seed.sql"
```

4. FastAPI 서버를 실행합니다.

```bash
uvicorn app.main:app --reload
```

이미 8000 포트를 다른 서버가 사용 중이면 아래처럼 8001 포트로 실행합니다.

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

5. Swagger와 API를 확인합니다.

```text
http://localhost:8000/docs
http://localhost:8000/api/v1/tutors/tutor1/available-times
```

8001 포트로 실행한 경우:

```text
http://localhost:8001/docs
http://localhost:8001/api/v1/tutors/tutor1/available-times
```
