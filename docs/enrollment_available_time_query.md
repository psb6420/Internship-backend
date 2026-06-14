# 수강신청 가능시간 조회 쿼리

## 사용 목적

수강신청 화면에서 과정, 수업시작일, 수업요일을 선택하면 해당 조건으로 32회 수업을 생성했을 때 배정 가능한 강사와 시간을 조회한다.

## 2차 4주차 피드백 반영

- 가능시간 쿼리 전에 서버 언어인 파이썬에서 시간 계산을 먼저 처리한다.
- 후보 수업 시작시간, 후보 수업 종료시간, 수업에 필요한 5분 단위 슬롯 시작시간을 파이썬에서 생성한다.
- 쿼리에서는 `ADDTIME`, `SEC_TO_TIME`, `TIMEDIFF`, `TIME_TO_SEC`, `LEAST`, `GREATEST` 같은 시간 계산 함수를 사용하지 않는다.
- 쿼리는 파이썬에서 만든 후보 시간 값을 `candidate_segments` CTE로 받아 단순 비교와 집계만 수행한다.
- 3주차에 반영한 수업 종료일 계산 방식도 유지해 `firstClassDate`, `lessonEndDate`를 쿼리에 함께 전달한다.

## 서버 시간 계산 소스

```python
def build_required_segment_starts(start_time: str, duration_minutes: int):
    start_minutes = time_text_to_minutes(start_time)
    end_minutes = start_minutes + duration_minutes

    if end_minutes >= 24 * 60:
        raise HTTPException(status_code=400, detail='수업 종료 시간이 하루를 넘을 수 없습니다.')

    return [
        minutes_to_time_text(start_minutes + offset)
        for offset in range(0, duration_minutes, 5)
    ]
```

```python
def build_candidate_time_windows(candidate_start_times: list[str], duration_minutes: int):
    windows = []
    seen = set()

    for candidate_start_time in candidate_start_times:
        start_time = format_time(candidate_start_time)
        if not start_time or start_time in seen:
            continue

        seen.add(start_time)
        start_minutes = time_text_to_minutes(start_time)
        end_minutes = start_minutes + duration_minutes

        if end_minutes >= 24 * 60:
            continue

        windows.append(
            {
                'startTime': f'{start_time}:00',
                'endTime': minutes_to_time_text(end_minutes),
                'segmentStartTimes': build_required_segment_starts(start_time, duration_minutes),
            },
        )

    return windows
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
WITH candidate_segments AS (
    SELECT
        TIME(:candidateStartTime) AS candidateStartTime,
        TIME(:candidateEndTime) AS candidateEndTime,
        TIME(:segmentStartTime) AS segmentStartTime
    UNION ALL
    ...
),
candidate_segment_counts AS (
    SELECT
        candidateStartTime,
        candidateEndTime,
        COUNT(DISTINCT segmentStartTime) AS requiredSegmentCount
    FROM candidate_segments
    GROUP BY candidateStartTime, candidateEndTime
),
candidate_day_times AS (
    SELECT
        slot.tutorId,
        tutor.tutorName,
        slot.dayOfWeek,
        cs.candidateStartTime,
        cs.candidateEndTime,
        csc.requiredSegmentCount,
        COUNT(DISTINCT slot.slotStartTime) AS matchedSegmentCount
    FROM candidate_segments cs
    JOIN candidate_segment_counts csc
        ON csc.candidateStartTime = cs.candidateStartTime
        AND csc.candidateEndTime = cs.candidateEndTime
    JOIN TBL_TUTOR_AVAILABLE_TIME slot
        ON slot.slotStartTime = cs.segmentStartTime
        AND slot.display = '1'
        AND slot.dayOfWeek IN (:days)
    JOIN TBL_TUTOR tutor
        ON tutor.tutorId = slot.tutorId
        AND tutor.display = '1'
    GROUP BY
        slot.tutorId,
        tutor.tutorName,
        slot.dayOfWeek,
        cs.candidateStartTime,
        cs.candidateEndTime,
        csc.requiredSegmentCount
    HAVING matchedSegmentCount = requiredSegmentCount
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
- 수업 종료시간과 필요한 5분 단위 슬롯은 파이썬에서 미리 계산한다.
- DB는 시간 더하기와 시간 차이 계산을 수행하지 않고, 전달받은 시간 값이 가능시간 테이블에 존재하는지만 확인한다.
- 데이터가 많아질수록 행마다 시간 함수를 계산하는 비용을 줄이고, `slotStartTime`, `dayOfWeek`, `classDate` 같은 저장된 컬럼 비교 중심으로 조회할 수 있다.
