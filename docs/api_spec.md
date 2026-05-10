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
      "dayOfWeek": 0,
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

## 요일 표현 기준

- `dayOfWeek`는 DB에 저장되는 실제 요일 값입니다.
- Python `datetime.now().weekday()` 기준과 맞춰 `0=월, 1=화, 2=수, 3=목, 4=금`으로 사용합니다.
- `dayName`은 DB 저장값이 아니라 사용자가 이해하기 쉽도록 FastAPI에서 변환해 내려주는 표시용 값입니다.

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
