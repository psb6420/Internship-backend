# 강사 가능시간 조회 API 명세서

## API 개요

- 기능: 강사 아이디로 가능시간 목록 조회
- Method: `GET`
- URL: `/api/v1/tutors/{tutor_id}/available-times`
- 예시 URL: `/api/v1/tutors/tutor1/available-times`
- 인증: 없음

## Path Parameters

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| tutor_id | string | Y | 강사 아이디. 예: tutor1 |

## Response 200

강사 가능시간 조회 성공

```json
{
  "tutorId": "tutor1",
  "tutorName": "강사1",
  "availableTimes": [
    {
      "dayOfWeek": 1,
      "dayName": "월",
      "slots": [
        {
          "startTime": "13:00",
          "endTime": "13:05"
        },
        {
          "startTime": "13:05",
          "endTime": "13:10"
        }
      ]
    }
  ]
}
```

## Response 404

강사 가능시간 데이터가 없는 경우

```json
{
  "detail": "강사 가능시간 데이터가 없습니다."
}
```

## Swagger 확인

FastAPI 실행 후 아래 주소에서 Swagger 문서를 확인할 수 있습니다.

```text
http://localhost:8000/docs
```

## 실행 예시

```bash
uvicorn app.main:app --reload
```

```bash
curl http://localhost:8000/api/v1/tutors/tutor1/available-times
```
