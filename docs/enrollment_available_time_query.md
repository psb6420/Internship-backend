# 수강신청 가능시간 조회 쿼리

## 사용 목적

수강신청 화면에서 과정, 수업시작일, 수업요일을 선택하면 해당 조건으로 32회 수업을 생성했을 때 배정 가능한 강사와 시간을 조회한다.

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
WITH RECURSIVE day_numbers AS (
    SELECT 0 AS dayOffset
    UNION ALL
    SELECT dayOffset + 1
    FROM day_numbers
    WHERE dayOffset < 370
),
target_classes AS (
    SELECT classDate, dayOfWeek, lessonRound
    FROM (
        SELECT
            DATE_ADD(:startDate, INTERVAL dayOffset DAY) AS classDate,
            WEEKDAY(DATE_ADD(:startDate, INTERVAL dayOffset DAY)) AS dayOfWeek,
            ROW_NUMBER() OVER (
                ORDER BY DATE_ADD(:startDate, INTERVAL dayOffset DAY)
            ) AS lessonRound
        FROM day_numbers
        WHERE WEEKDAY(DATE_ADD(:startDate, INTERVAL dayOffset DAY)) IN (:days)
    ) class_days
    WHERE lessonRound <= 32
),
candidate_day_times AS (
    SELECT
        seed.tutorId,
        tutor.tutorName,
        seed.dayOfWeek,
        seed.slotStartTime AS candidateStartTime,
        ADDTIME(seed.slotStartTime, SEC_TO_TIME(20 * 60)) AS candidateEndTime,
        SUM(
            TIME_TO_SEC(
                TIMEDIFF(
                    LEAST(
                        slot.slotEndTime,
                        ADDTIME(seed.slotStartTime, SEC_TO_TIME(20 * 60))
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
        AND slot.slotStartTime < ADDTIME(seed.slotStartTime, SEC_TO_TIME(20 * 60))
        AND slot.slotEndTime > seed.slotStartTime
    WHERE seed.display = '1'
        AND seed.dayOfWeek IN (:days)
        AND ADDTIME(seed.slotStartTime, SEC_TO_TIME(20 * 60)) <= TIME('23:59:59')
    GROUP BY seed.tutorId, tutor.tutorName, seed.dayOfWeek, seed.slotStartTime
    HAVING matchedMinutes >= 20
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
    FROM target_classes tc
    JOIN TBL_CLASS_SCHEDULE cs
        ON cs.tutorId = ct.tutorId
        AND cs.classDate = tc.classDate
        AND cs.classStatus <> 9
        AND cs.classStartTime < ct.candidateEndTime
        AND cs.classEndTime > ct.candidateStartTime
)
ORDER BY ct.candidateStartTime ASC, ct.tutorId ASC;
```

## 작성 사유

- `target_classes`에서 신청 조건에 맞는 실제 수업일 32개를 먼저 만든다.
- `candidate_day_times`에서 강사별 주간 가능시간이 20분 수업을 감당할 수 있는지 계산한다.
- `candidate_times`에서 선택한 모든 요일에 같은 시작시간으로 가능한 강사만 남긴다.
- 마지막 `NOT EXISTS`에서 실제 수업일 기준으로 이미 배정된 수업과 시간이 겹치는 강사를 제외한다.
- 따라서 화면에 표시되는 시간은 강사 가능시간과 기존 배정 현황을 모두 통과한 시간이다.
