# 수강신청 DB 테이블 정의서

## 1. 설계 개요

- 목적: 학생이 수강신청을 했을 때 필요한 학생, 과정, 강사, 수업요일, 수업시간, 일자별 수업정보를 저장한다.
- DBMS 기준: MySQL 8.0
- 데이터베이스명: `dozon_internship`
- 문자셋: `utf8mb4`
- 요일 기준: `0=월, 1=화, 2=수, 3=목, 4=금, 5=토, 6=일`
- 상태값은 `TINYINT`로 저장하고, 화면에 표시할 때 한글명으로 변환하는 방식으로 설계했다.

## 2. 전체 테이블 구성

| 테이블명 | 한글명 | 설명 |
| --- | --- | --- |
| `TBL_STUDENT` | 학생 기본정보 | 학생 아이디, 고유번호, 이름, 연락처, 이메일 저장 |
| `TBL_TUTOR` | 강사 기본정보 | 강사 아이디, 이름, 연락처, 이메일 저장 |
| `TBL_COURSE` | 수업과정 정보 | 과정 코드, 과정명, 레벨, 설명 저장 |
| `TBL_ENROLLMENT` | 수강신청 정보 | 학생, 과정, 강사, 시작일, 종료일, 횟수, 시작시간, 수업시간 저장 |
| `TBL_ENROLLMENT_WEEKDAY` | 수강신청별 수업요일 | 한 신청에 여러 요일을 연결해서 저장 |
| `TBL_CLASS_SCHEDULE` | 일자별 수업정보 | 수강신청 기준으로 실제 수업일과 회차를 생성해 저장 |

## 3. `TBL_STUDENT` 학생 기본정보

### 테이블 목적

수강신청을 하는 학생의 기본 정보를 저장한다. 과제의 학생정보 항목인 `아이디`와 `고유번호`를 분리해서 중복되지 않게 관리한다.

### 컬럼 정의

| 컬럼명 | 데이터 형식 | Null | Key | 설명 |
| --- | --- | --- | --- | --- |
| `studentSeq` | `INT` | N | PK | 학생 고유 순번, Auto Increment |
| `studentId` | `VARCHAR(30)` | N | UNIQUE | 학생 로그인/식별 아이디 |
| `studentNo` | `VARCHAR(20)` | N | UNIQUE | 학생 고유번호 |
| `studentName` | `VARCHAR(50)` | N |  | 학생명 |
| `studentPhone` | `VARCHAR(20)` | Y |  | 학생 연락처 |
| `studentEmail` | `VARCHAR(100)` | Y |  | 학생 이메일 |
| `display` | `CHAR(1)` | N |  | 사용 여부. `1=사용`, `0=미사용` |
| `regDate` | `DATETIME` | N |  | 등록일 |
| `modDate` | `DATETIME` | Y |  | 수정일 |

### 인덱스

| 인덱스명 | 컬럼 | 설명 |
| --- | --- | --- |
| `PRIMARY` | `studentSeq` | 기본키 |
| `UX_TBL_STUDENT_ID` | `studentId` | 학생 아이디 중복 방지 |
| `UX_TBL_STUDENT_NO` | `studentNo` | 학생 고유번호 중복 방지 |

## 4. `TBL_TUTOR` 강사 기본정보

### 테이블 목적

수업을 담당하는 강사 정보를 저장한다. 수강신청과 일자별 수업정보에서 강사를 참조한다.

### 컬럼 정의

| 컬럼명 | 데이터 형식 | Null | Key | 설명 |
| --- | --- | --- | --- | --- |
| `tutorSeq` | `INT` | N | PK | 강사 고유 순번, Auto Increment |
| `tutorId` | `VARCHAR(30)` | N | UNIQUE | 강사 아이디 |
| `tutorName` | `VARCHAR(50)` | N |  | 강사명 |
| `tutorPhone` | `VARCHAR(20)` | Y |  | 강사 연락처 |
| `tutorEmail` | `VARCHAR(100)` | Y |  | 강사 이메일 |
| `display` | `CHAR(1)` | N |  | 사용 여부. `1=사용`, `0=미사용` |
| `regDate` | `DATETIME` | N |  | 등록일 |
| `modDate` | `DATETIME` | Y |  | 수정일 |

### 인덱스

| 인덱스명 | 컬럼 | 설명 |
| --- | --- | --- |
| `PRIMARY` | `tutorSeq` | 기본키 |
| `UX_TBL_TUTOR_ID` | `tutorId` | 강사 아이디 중복 방지 |

## 5. `TBL_COURSE` 수업과정 정보

### 테이블 목적

수강신청에서 선택하는 수업과정 정보를 저장한다. 과정명, 레벨, 설명을 별도 테이블로 분리해서 같은 과정 정보를 반복 저장하지 않는다.

### 컬럼 정의

| 컬럼명 | 데이터 형식 | Null | Key | 설명 |
| --- | --- | --- | --- | --- |
| `courseSeq` | `INT` | N | PK | 수업과정 고유 순번, Auto Increment |
| `courseCode` | `VARCHAR(20)` | N | UNIQUE | 수업과정 코드 |
| `courseName` | `VARCHAR(100)` | N |  | 수업과정명 |
| `courseLevel` | `VARCHAR(20)` | Y |  | 과정 레벨 |
| `courseDescription` | `VARCHAR(500)` | Y |  | 과정 설명 |
| `display` | `CHAR(1)` | N |  | 사용 여부. `1=사용`, `0=미사용` |
| `regDate` | `DATETIME` | N |  | 등록일 |
| `modDate` | `DATETIME` | Y |  | 수정일 |

### 인덱스

| 인덱스명 | 컬럼 | 설명 |
| --- | --- | --- |
| `PRIMARY` | `courseSeq` | 기본키 |
| `UX_TBL_COURSE_CODE` | `courseCode` | 수업과정 코드 중복 방지 |

## 6. `TBL_ENROLLMENT` 수강신청 정보

### 테이블 목적

학생이 수강신청한 기본 정보를 저장하는 핵심 테이블이다. 필수 항목인 학생정보, 수업 시작일, 수업횟수, 수업과정정보, 수업시작시간, 수업시간, 강사정보를 이 테이블과 참조 테이블을 통해 조회할 수 있다.

### 컬럼 정의

| 컬럼명 | 데이터 형식 | Null | Key | 설명 |
| --- | --- | --- | --- | --- |
| `enrollmentSeq` | `INT` | N | PK | 수강신청 고유 순번, Auto Increment |
| `enrollmentId` | `VARCHAR(20)` | N | UNIQUE | 수강신청번호 |
| `studentId` | `VARCHAR(30)` | N | FK | 학생 아이디. `TBL_STUDENT.studentId` 참조 |
| `courseCode` | `VARCHAR(20)` | N | FK | 과정 코드. `TBL_COURSE.courseCode` 참조 |
| `tutorId` | `VARCHAR(30)` | N | FK | 강사 아이디. `TBL_TUTOR.tutorId` 참조 |
| `lessonStartDate` | `DATE` | N |  | 수업 시작일 |
| `lessonEndDate` | `DATE` | N |  | 수업 종료일. 마지막 회차의 실제 수업일 |
| `lessonCount` | `SMALLINT` | N |  | 수업횟수. 2주차 실습 기준 32회 고정 |
| `lessonStartTime` | `TIME` | N |  | 수업 시작시간 |
| `lessonDurationMinutes` | `SMALLINT` | N |  | 수업시간(분). 예: 20분, 40분 |
| `enrollmentStatus` | `TINYINT` | N |  | 신청상태. `1=신청`, `2=진행중`, `3=종료`, `9=취소` |
| `studentRequestDesc` | `VARCHAR(500)` | Y |  | 학생 요청사항 |
| `regDate` | `DATETIME` | N |  | 등록일 |
| `modDate` | `DATETIME` | Y |  | 수정일 |

### 인덱스

| 인덱스명 | 컬럼 | 설명 |
| --- | --- | --- |
| `PRIMARY` | `enrollmentSeq` | 기본키 |
| `UX_TBL_ENROLLMENT_ID` | `enrollmentId` | 수강신청번호 중복 방지 |
| `IX_TBL_ENROLLMENT_STUDENT` | `studentId`, `enrollmentStatus` | 학생별 신청 내역 조회 |
| `IX_TBL_ENROLLMENT_TUTOR_TIME` | `tutorId`, `lessonStartDate`, `lessonEndDate`, `lessonStartTime` | 강사별 수업 기간/시간 조회 |
| `IX_TBL_ENROLLMENT_COURSE` | `courseCode` | 과정별 신청 내역 조회 |

## 7. `TBL_ENROLLMENT_WEEKDAY` 수강신청별 수업요일

### 테이블 목적

한 수강신청에 여러 요일이 들어갈 수 있으므로 요일을 별도 테이블로 분리했다. 예를 들어 월수금 수업은 한 신청번호에 `0`, `2`, `4` 세 건으로 저장한다.

### 컬럼 정의

| 컬럼명 | 데이터 형식 | Null | Key | 설명 |
| --- | --- | --- | --- | --- |
| `enrollmentWeekdaySeq` | `INT` | N | PK | 수강신청 요일 고유 순번, Auto Increment |
| `enrollmentSeq` | `INT` | N | FK | 수강신청 고유 순번. `TBL_ENROLLMENT.enrollmentSeq` 참조 |
| `dayOfWeek` | `TINYINT` | N |  | 수업요일. `0=월`, `1=화`, `2=수`, `3=목`, `4=금`, `5=토`, `6=일` |
| `regDate` | `DATETIME` | N |  | 등록일 |

### 인덱스

| 인덱스명 | 컬럼 | 설명 |
| --- | --- | --- |
| `PRIMARY` | `enrollmentWeekdaySeq` | 기본키 |
| `UX_TBL_ENROLLMENT_WEEKDAY` | `enrollmentSeq`, `dayOfWeek` | 한 신청에 같은 요일 중복 저장 방지 |
| `IX_TBL_ENROLLMENT_WEEKDAY_DAY` | `dayOfWeek` | 요일 기준 조회 |

## 8. `TBL_CLASS_SCHEDULE` 일자별 수업정보

### 테이블 목적

수강신청 정보를 기준으로 실제 수업일과 회차를 생성해 저장한다. 필수 제출 범위는 아니지만, 수업별 출결/수업 URL/상태 관리까지 확장하기 위해 설계했다.

### 컬럼 정의

| 컬럼명 | 데이터 형식 | Null | Key | 설명 |
| --- | --- | --- | --- | --- |
| `classSeq` | `INT` | N | PK | 일자별 수업 고유 순번, Auto Increment |
| `classId` | `VARCHAR(30)` | N | UNIQUE | 일자별 수업번호 |
| `enrollmentSeq` | `INT` | N | FK | 수강신청 고유 순번. `TBL_ENROLLMENT.enrollmentSeq` 참조 |
| `lessonRound` | `SMALLINT` | N |  | 수업 회차 |
| `classDate` | `DATE` | N |  | 수업일 |
| `dayOfWeek` | `TINYINT` | N |  | 수업요일 |
| `classStartTime` | `TIME` | N |  | 수업 시작시간 |
| `classEndTime` | `TIME` | N |  | 수업 종료시간 |
| `classDurationMinutes` | `SMALLINT` | N |  | 수업시간(분) |
| `tutorId` | `VARCHAR(30)` | N | FK | 강사 아이디. `TBL_TUTOR.tutorId` 참조 |
| `classStatus` | `TINYINT` | N |  | 수업상태. `1=예정`, `2=완료`, `9=취소` |
| `classUrl` | `VARCHAR(200)` | Y |  | 화상수업 URL |
| `classMemo` | `VARCHAR(500)` | Y |  | 수업 메모 |
| `regDate` | `DATETIME` | N |  | 등록일 |
| `modDate` | `DATETIME` | Y |  | 수정일 |

### 인덱스

| 인덱스명 | 컬럼 | 설명 |
| --- | --- | --- |
| `PRIMARY` | `classSeq` | 기본키 |
| `UX_TBL_CLASS_SCHEDULE_ID` | `classId` | 일자별 수업번호 중복 방지 |
| `UX_TBL_CLASS_SCHEDULE_ROUND` | `enrollmentSeq`, `lessonRound` | 한 신청 내 회차 중복 방지 |
| `UX_TBL_CLASS_SCHEDULE_TUTOR_START` | `tutorId`, `classDate`, `classStartTime` | 강사의 같은 날짜/시작시간 중복 배정 방지 |
| `IX_TBL_CLASS_SCHEDULE_DATE` | `classDate`, `classStartTime` | 날짜/시간 기준 조회 |
| `IX_TBL_CLASS_SCHEDULE_ENROLLMENT` | `enrollmentSeq`, `classDate` | 신청별 수업일 조회 |

## 9. 설계 기준

- 학생, 강사, 과정처럼 반복 사용되는 정보는 기준 테이블로 분리했다.
- 수강신청 본문에는 신청 자체의 조건인 시작일, 횟수, 시작시간, 수업시간, 상태를 저장했다.
- 수업 종료일은 `TBL_CLASS_SCHEDULE`의 마지막 수업일로도 계산할 수 있지만, 학생별 수강 기간 조회와 종료 예정 수업 검색이 자주 필요하다고 보고 `TBL_ENROLLMENT.lessonEndDate`에도 저장했다. 대신 일정 재생성 시 마지막 수업일과 함께 갱신해야 한다.
- 요일은 `월수금` 같은 문자열 하나로 저장하지 않고 `TBL_ENROLLMENT_WEEKDAY`에 숫자 여러 건으로 저장했다. 이렇게 하면 월수금, 화목 같은 조합을 처리할 수 있고, 요일별 검색/인덱스 적용이 쉽다.
- 요일을 별도 테이블로 분리하면 신청 1건에 요일 여러 건이 생겨 JOIN이 필요하고, 요일 전체를 바꿀 때 연결 데이터를 함께 수정해야 한다. 반대로 `TBL_ENROLLMENT`에 요일 문자열이나 여러 컬럼을 직접 넣으면 조회는 단순하지만 요일 조합 검색과 정합성 관리가 어려워진다. 이번 설계는 다양한 요일 조합과 요일 기준 검색을 우선해 별도 테이블 방식을 선택했다.
- 일자별 수업정보는 수강신청 기준으로 자동 생성되도록 했다. 이후 출결, 수업 URL, 강사 변경, 수업 취소 같은 운영 데이터는 `TBL_CLASS_SCHEDULE`에서 관리할 수 있다.
- 같은 강사가 같은 날짜와 같은 시작시간에 중복 배정되지 않도록 `UX_TBL_CLASS_SCHEDULE_TUTOR_START` 인덱스를 추가했다.
- MySQL은 `utf8mb4` 문자셋을 사용하므로 한글 데이터도 `VARCHAR`에 저장한다.

## 10. 더미데이터 구성

| 구분 | 건수 | 내용 |
| --- | ---: | --- |
| 학생 | 5건 | 서로 다른 학생 아이디와 고유번호 |
| 강사 | 5건 | 서로 다른 강사 아이디 |
| 과정 | 5건 | 기초 회화, 비즈니스, OPIc, 주니어, 프리토킹 |
| 수강신청 | 5건 | 32회, 20분, 월수금/화목 패턴 |
| 수강신청 요일 | 13건 | 월수금 3건씩 3개 신청, 화목 2건씩 2개 신청 |
| 일자별 수업정보 | 160건 | 수강신청의 수업횟수 합계만큼 자동 생성 |

## 11. 예시 조회 쿼리

### 테이블별 데이터 건수

```sql
SELECT 'TBL_STUDENT' AS tableName, COUNT(*) AS rowCount FROM TBL_STUDENT
UNION ALL SELECT 'TBL_TUTOR', COUNT(*) FROM TBL_TUTOR
UNION ALL SELECT 'TBL_COURSE', COUNT(*) FROM TBL_COURSE
UNION ALL SELECT 'TBL_ENROLLMENT', COUNT(*) FROM TBL_ENROLLMENT
UNION ALL SELECT 'TBL_ENROLLMENT_WEEKDAY', COUNT(*) FROM TBL_ENROLLMENT_WEEKDAY
UNION ALL SELECT 'TBL_CLASS_SCHEDULE', COUNT(*) FROM TBL_CLASS_SCHEDULE;
```

### 수강신청 목록 조회

```sql
SELECT
  e.enrollmentId,
  s.studentId,
  s.studentNo,
  s.studentName,
  c.courseName,
  e.lessonStartDate,
  e.lessonEndDate,
  e.lessonCount,
  e.lessonStartTime,
  e.lessonDurationMinutes,
  t.tutorName
FROM TBL_ENROLLMENT e
JOIN TBL_STUDENT s ON s.studentId = e.studentId
JOIN TBL_COURSE c ON c.courseCode = e.courseCode
JOIN TBL_TUTOR t ON t.tutorId = e.tutorId
ORDER BY e.enrollmentSeq;
```

### 특정 수강신청의 일자별 수업정보 조회

```sql
SELECT
  cs.classId,
  e.enrollmentId,
  cs.lessonRound,
  cs.classDate,
  cs.dayOfWeek,
  cs.classStartTime,
  cs.classEndTime,
  t.tutorName
FROM TBL_CLASS_SCHEDULE cs
JOIN TBL_ENROLLMENT e ON e.enrollmentSeq = cs.enrollmentSeq
JOIN TBL_TUTOR t ON t.tutorId = cs.tutorId
WHERE e.enrollmentId = 'ENR2026060101'
ORDER BY cs.lessonRound;
```

## 12. 검증 기준

- `TBL_ENROLLMENT`은 5건이어야 한다.
- `TBL_CLASS_SCHEDULE` 건수는 수강신청별 `lessonCount` 합계와 같아야 한다.
- `TBL_ENROLLMENT.lessonEndDate`는 해당 신청의 마지막 `TBL_CLASS_SCHEDULE.classDate`와 같아야 한다.
- 생성된 `TBL_CLASS_SCHEDULE.dayOfWeek`는 `TBL_ENROLLMENT_WEEKDAY.dayOfWeek`에 존재해야 한다.
- 같은 강사, 같은 날짜, 같은 시작시간의 중복 수업이 없어야 한다.
