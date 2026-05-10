# TBL_TUTOR_AVAILABLE_TIME

## 테이블 개요

- 테이블명: `TBL_TUTOR_AVAILABLE_TIME`
- 한글명: 강사 가능시간
- 설명: 강사별 수업 가능 요일과 5분 단위 가능시간을 저장하는 테이블입니다.
- 기준: 수강신청 화면에서 선택 가능한 강사 시간 목록을 조회하기 위한 데이터입니다.

## 컬럼 정의

| 컬럼명 | 데이터 형식 | Null | 비고 |
| --- | --- | --- | --- |
| availabilitySeq | int | N | 강사 가능시간 고유값, PK, Auto Increment |
| tutorId | varchar(20) | N | 강사 아이디. 예: tutor1 |
| tutorName | varchar(50) | N | 강사명. MySQL에서는 `utf8mb4` 문자셋을 사용하므로 `varchar`로 한글 저장 가능 |
| dayOfWeek | tinyint | N | 요일. 0=월, 1=화, 2=수, 3=목, 4=금 |
| slotStartTime | time | N | 가능 시작 시간. 5분 단위 저장 |
| slotEndTime | time | N | 가능 종료 시간. 시작 시간 + 5분 |
| display | char(1) | N | 사용 여부. 1=사용, 0=미사용 |
| regDate | datetime | N | 등록일 |
| modDate | datetime | Y | 수정일 |

## 설계 기준

- 샘플 화면의 체크박스 구조를 기준으로 시간 슬롯을 5분 단위로 저장합니다.
- 한 강사가 같은 요일, 같은 시작 시간에 중복 저장되지 않도록 unique index를 적용합니다.
- MySQL DB는 `utf8mb4` 문자셋을 사용하므로 한글 컬럼도 `varchar`로 정의합니다.
- 요일은 문자열 `월`, `화`, `수`로 저장하지 않고 `tinyint` 숫자로 저장합니다.
- 요일 숫자는 Python `datetime.now().weekday()` 기준과 맞춰 `0=월, 1=화, 2=수, 3=목, 4=금`으로 사용합니다.
- FastAPI 응답의 `dayName`은 DB 저장값이 아니라 `dayOfWeek` 숫자를 한글로 변환한 표시용 값입니다.
- 현재 과제 범위는 평일 데이터만 사용합니다. 주말까지 확장할 경우 `5=토`, `6=일`을 추가할 수 있습니다.
- 현재 과제 범위에서는 로그인, 회원, 강의 신청 내역과 연결하지 않습니다.
- 추후 백엔드에서 강사 가능시간을 조회해 프론트 수강신청 화면의 선택 가능/불가능 시간 표시와 연결할 수 있습니다.

## INDEX

| 인덱스명 | 컬럼 | 설명 |
| --- | --- | --- |
| PRIMARY | availabilitySeq | 기본키 |
| UX_TBL_TUTOR_AVAILABLE_TIME_SLOT | tutorId, dayOfWeek, slotStartTime | 강사별 요일/시간 중복 방지 |
| IX_TBL_TUTOR_AVAILABLE_TIME_TUTOR | tutorId, display | 강사 아이디 기준 조회 |
| IX_TBL_TUTOR_AVAILABLE_TIME_DAY_TIME | dayOfWeek, slotStartTime | 요일/시간 기준 조회 |
