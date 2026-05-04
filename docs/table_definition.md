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
| tutorName | nvarchar(50) | N | 강사명 |
| dayOfWeek | tinyint | N | 요일. 1=월, 2=화, 3=수, 4=목, 5=금 |
| slotStartTime | time | N | 가능 시작 시간. 5분 단위 저장 |
| slotEndTime | time | N | 가능 종료 시간. 시작 시간 + 5분 |
| display | char(1) | N | 사용 여부. 1=사용, 0=미사용 |
| regDate | datetime | N | 등록일 |
| modDate | datetime | Y | 수정일 |

## 특이사항

- 샘플 화면의 체크박스 구조를 기준으로 시간 슬롯을 5분 단위로 저장합니다.
- 한 강사가 같은 요일, 같은 시작 시간에 중복 저장되지 않도록 unique index를 적용합니다.
- 현재 과제 범위에서는 로그인, 회원, 강의 신청 내역과 연결하지 않습니다.
- 추후 백엔드에서 강사 가능시간을 조회해 프론트 수강신청 화면의 선택 가능/불가능 시간 표시와 연결할 수 있습니다.

## INDEX

| 인덱스명 | 컬럼 | 설명 |
| --- | --- | --- |
| PRIMARY | availabilitySeq | 기본키 |
| UX_TBL_TUTOR_AVAILABLE_TIME_SLOT | tutorId, dayOfWeek, slotStartTime | 강사별 요일/시간 중복 방지 |
| IX_TBL_TUTOR_AVAILABLE_TIME_TUTOR | tutorId, display | 강사 아이디 기준 조회 |
| IX_TBL_TUTOR_AVAILABLE_TIME_DAY_TIME | dayOfWeek, slotStartTime | 요일/시간 기준 조회 |
