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

## 조건 기반 가능 강사 검색 API

- 기능: 요일, 시작시간, 학습시간을 기준으로 가능한 강사 목록 조회
- Method: `POST`
- URL: `/api/v1/tutors/available-search`
- 인증: 없음

### Request Body

| 이름 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| days | number[] | Y | 요일 목록. 0=월, 1=화, 2=수, 3=목, 4=금 |
| startTime | string | Y | 수업 시작시간. `HH:MM` 형식, 5분 단위 |
| durationMinutes | number | Y | 학습시간. 1분 이상 정수 |

```json
{
  "days": [0, 2, 4],
  "startTime": "13:00",
  "durationMinutes": 23
}
```

### Response 200

조건에 맞는 강사가 있는 경우

```json
{
  "days": [0, 2, 4],
  "startTime": "13:00",
  "requestedEndTime": "13:23",
  "durationMinutes": 23,
  "availableTutors": [
    {
      "tutorId": "tutor1",
      "tutorName": "강사1",
      "availableDays": [
        {
          "dayOfWeek": 0,
          "dayName": "월"
        },
        {
          "dayOfWeek": 2,
          "dayName": "수"
        },
        {
          "dayOfWeek": 4,
          "dayName": "금"
        }
      ]
    }
  ]
}
```

조건은 정상이나 가능한 강사가 없는 경우

```json
{
  "days": [1, 3],
  "startTime": "13:15",
  "requestedEndTime": "13:35",
  "durationMinutes": 20,
  "availableTutors": []
}
```

### Response 400

검색 조건이 잘못된 경우

```json
{
  "detail": "시작시간은 5분 단위로 입력해 주세요."
}
```

### 검색 기준

- 요청한 모든 요일에 해당 시간만큼 가능한 강사만 반환합니다.
- `durationMinutes`는 5분 단위로 올림하지 않고 입력된 1분 단위 값을 그대로 사용합니다.
- 예를 들어 `13:00` 시작, `23분` 수업이면 검색 종료 기준과 응답의 `requestedEndTime`은 `13:23`입니다.

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
