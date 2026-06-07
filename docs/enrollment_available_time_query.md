# 수강신청 가능시간 조회 쿼리

## 사용 목적

수강신청 화면에서 과정, 수업시작일, 수업요일을 선택하면 해당 조건으로 32회 수업을 생성했을 때 배정 가능한 강사와 시간을 조회한다.

## 2차 3주차 피드백 반영

- 가능시간 쿼리 실행 전에 서버 언어인 파이썬에서 실제 수업일 32개를 먼저 계산한다.
- 파이썬에서 계산한 첫 수업일과 종료일을 쿼리 파라미터로 전달한다.
- 기존 쿼리의 `WITH RECURSIVE day_numbers`, `target_classes`, `ROW_NUMBER()`를 제거했다.
- 기존 수업 충돌 검사는 `TBL_CLASS_SCHEDULE.classDate BETWEEN :firstClassDate AND :lessonEndDate` 범위 조건으로 처리한다.
- 선택 요일은 `cs.dayOfWeek IN (:days)`로 함께 제한해 수업 기간 안의 실제 대상 요일만 검사한다.

## 서버 종료일 계산 소스

```python
class_dates = build_class_dates(request.startDate, pattern['days'], FIXED_LESSON_COUNT)

rows = fetch_available_enrollment_rows(
    cursor,
    class_dates[0],
    class_dates[-1],
    pattern['days'],
)
```

```python
def build_class_dates(start_date: date, days: list[int], lesson_count: int):
    class_dates = []
    current_date = start_date

    while len(class_dates) < lesson_count:
        if current_date.weekday() in days:
            class_dates.append(current_date)
        current_date += timedelta(days=1)

    return class_dates
```

## 조회 기준

- 학생은 `stu2026001`로 고정한다.
- 수업횟수는 32회로 고정한다.
- 수업시간은 20분으로 고정한다.
- 수업요일은 `월수금` 또는 `화목`만 사용한다.
- 강사의 주간 가능시간은 `TBL_TUTOR_AVAILABLE_TIME`에서 확인한다.
- 이미 배정된 실제 수업은 `TBL_CLASS_SCHEDULE`에서 확인한다.
- 같은 강사가 같은 날짜와 시간에 겹치는 수업이 있으면 조회 결과에서 제외한다.

## 핵심 쿼리

```sql
WITH candidate_day_times AS (
    SELECT
        seed.tutorId,
        tutor.tutorName,
        seed.dayOfWeek,
        seed.slotStartTime AS candidateStartTime,
        ADDTIME(seed.slotStartTime, SEC_TO_TIME(:lessonDurationMinutes * 60)) AS candidateEndTime,
        SUM(
            TIME_TO_SEC(
                TIMEDIFF(
                    LEAST(
                        slot.slotEndTime,
                        ADDTIME(seed.slotStartTime, SEC_TO_TIME(:lessonDurationMinutes * 60))
                    ),
                    GREATEST(slot.slotStartTime, seed.slotStartTime)
                )
            ) / 60
        ) AS matchedMinutes
    FROM TBL_TUTOR_AVAILABLE_TIME seed
    JOIN TBL_TUTOR tutor
        ON tutor.tutorId = seed.tutorId
        AND tutor.display = '1'
    JOIN TBL_TUTOR_AVAILABLE_TIME slot
        ON slot.tutorId = seed.tutorId
        AND slot.dayOfWeek = seed.dayOfWeek
        AND slot.display = '1'
        AND slot.slotStartTime < ADDTIME(seed.slotStartTime, SEC_TO_TIME(:lessonDurationMinutes * 60))
        AND slot.slotEndTime > seed.slotStartTime
    WHERE seed.display = '1'
        AND seed.dayOfWeek IN (:days)
        AND ADDTIME(seed.slotStartTime, SEC_TO_TIME(:lessonDurationMinutes * 60)) <= TIME('23:59:59')
    GROUP BY seed.tutorId, tutor.tutorName, seed.dayOfWeek, seed.slotStartTime
    HAVING matchedMinutes >= :lessonDurationMinutes
),
candidate_times AS (
    SELECT
        tutorId,
        tutorName,
        candidateStartTime,
        candidateEndTime,
        COUNT(DISTINCT dayOfWeek) AS availableDayCount
    FROM candidate_day_times
    GROUP BY tutorId, tutorName, candidateStartTime, candidateEndTime
    HAVING availableDayCount = :dayCount
)
SELECT
    ct.tutorId,
    ct.tutorName,
    ct.candidateStartTime,
    ct.candidateEndTime
FROM candidate_times ct
WHERE NOT EXISTS (
    SELECT 1
    FROM TBL_CLASS_SCHEDULE cs
    WHERE cs.tutorId = ct.tutorId
        AND cs.classStatus <> 9
        AND cs.classDate BETWEEN :firstClassDate AND :lessonEndDate
        AND cs.dayOfWeek IN (:days)
        AND cs.classStartTime < ct.candidateEndTime
        AND cs.classEndTime > ct.candidateStartTime
)
ORDER BY ct.candidateStartTime ASC, ct.tutorId ASC;
```

## 작성 사유

- 수업 종료일은 파이썬에서 `build_class_dates()`로 계산한 32번째 수업일을 사용한다.
- DB는 32개 수업일을 재귀 CTE로 다시 생성하지 않고, 이미 계산된 기간 안의 기존 수업만 조회한다.
- `TBL_CLASS_SCHEDULE`는 실제 배정 수업 단위 테이블이므로, 강사/기간/요일/시간 겹침 조건만으로 충돌 여부를 판단할 수 있다.
- 데이터가 많아질수록 재귀 CTE와 임시 대상 수업일 생성 비용을 줄이고, 일정 테이블의 인덱스를 활용하기 쉬운 조건으로 바뀐다.
