USE dozon_internship;

DELETE FROM TBL_TUTOR_AVAILABLE_TIME;

INSERT INTO TBL_TUTOR_AVAILABLE_TIME (
  tutorId,
  tutorName,
  dayOfWeek,
  slotStartTime,
  slotEndTime,
  display
)
WITH RECURSIVE
tutors AS (
  SELECT 1 AS tutorNo, 'tutor1' AS tutorId, '강사1' AS tutorName UNION ALL
  SELECT 2, 'tutor2', '강사2' UNION ALL
  SELECT 3, 'tutor3', '강사3' UNION ALL
  SELECT 4, 'tutor4', '강사4' UNION ALL
  SELECT 5, 'tutor5', '강사5' UNION ALL
  SELECT 6, 'tutor6', '강사6' UNION ALL
  SELECT 7, 'tutor7', '강사7' UNION ALL
  SELECT 8, 'tutor8', '강사8' UNION ALL
  SELECT 9, 'tutor9', '강사9' UNION ALL
  SELECT 10, 'tutor10', '강사10'
),
days AS (
  SELECT 1 AS dayOfWeek UNION ALL
  SELECT 2 UNION ALL
  SELECT 3 UNION ALL
  SELECT 4 UNION ALL
  SELECT 5
),
slots AS (
  SELECT TIME('13:00:00') AS slotStartTime
  UNION ALL
  SELECT ADDTIME(slotStartTime, '00:05:00')
  FROM slots
  WHERE slotStartTime < TIME('22:55:00')
)
SELECT
  t.tutorId,
  t.tutorName,
  d.dayOfWeek,
  s.slotStartTime,
  ADDTIME(s.slotStartTime, '00:05:00') AS slotEndTime,
  '1' AS display
FROM tutors t
CROSS JOIN days d
CROSS JOIN slots s
WHERE
  (
    t.tutorNo IN (1, 2)
    AND d.dayOfWeek IN (1, 3, 5)
    AND s.slotStartTime BETWEEN TIME('13:00:00') AND TIME('16:55:00')
  )
  OR (
    t.tutorNo IN (3, 4)
    AND d.dayOfWeek IN (2, 4)
    AND s.slotStartTime BETWEEN TIME('14:00:00') AND TIME('18:55:00')
  )
  OR (
    t.tutorNo IN (5, 6)
    AND d.dayOfWeek BETWEEN 1 AND 5
    AND s.slotStartTime BETWEEN TIME('18:00:00') AND TIME('21:55:00')
  )
  OR (
    t.tutorNo IN (7, 8)
    AND d.dayOfWeek IN (1, 2, 3, 4)
    AND s.slotStartTime BETWEEN TIME('19:00:00') AND TIME('22:55:00')
  )
  OR (
    t.tutorNo IN (9, 10)
    AND d.dayOfWeek BETWEEN 1 AND 5
    AND s.slotStartTime BETWEEN TIME('15:00:00') AND TIME('17:55:00')
  )
ORDER BY t.tutorNo, d.dayOfWeek, s.slotStartTime;

SELECT tutorId, tutorName, COUNT(*) AS availableSlotCount
FROM TBL_TUTOR_AVAILABLE_TIME
GROUP BY tutorId, tutorName
ORDER BY tutorId;
