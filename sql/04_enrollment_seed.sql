USE dozon_internship;

SET NAMES utf8mb4;

DELETE FROM TBL_CLASS_SCHEDULE;
DELETE FROM TBL_ENROLLMENT_WEEKDAY;
DELETE FROM TBL_ENROLLMENT;
DELETE FROM TBL_COURSE;
DELETE FROM TBL_TUTOR;
DELETE FROM TBL_STUDENT;

ALTER TABLE TBL_STUDENT AUTO_INCREMENT = 1;
ALTER TABLE TBL_TUTOR AUTO_INCREMENT = 1;
ALTER TABLE TBL_COURSE AUTO_INCREMENT = 1;
ALTER TABLE TBL_ENROLLMENT AUTO_INCREMENT = 1;
ALTER TABLE TBL_ENROLLMENT_WEEKDAY AUTO_INCREMENT = 1;
ALTER TABLE TBL_CLASS_SCHEDULE AUTO_INCREMENT = 1;

INSERT INTO TBL_STUDENT (
  studentId,
  studentNo,
  studentName,
  studentPhone,
  studentEmail,
  display
) VALUES
  ('stu2026001', 'STU-2026-001', '김민준', '010-1001-2001', 'minjun@example.com', '1'),
  ('stu2026002', 'STU-2026-002', '이서연', '010-1001-2002', 'seoyeon@example.com', '1'),
  ('stu2026003', 'STU-2026-003', '박도윤', '010-1001-2003', 'doyun@example.com', '1'),
  ('stu2026004', 'STU-2026-004', '최하은', '010-1001-2004', 'haeun@example.com', '1'),
  ('stu2026005', 'STU-2026-005', '정지호', '010-1001-2005', 'jiho@example.com', '1');

INSERT INTO TBL_TUTOR (
  tutorId,
  tutorName,
  tutorPhone,
  tutorEmail,
  display
) VALUES
  ('tutor01', '강사 Alice', '010-3001-4001', 'alice.tutor@example.com', '1'),
  ('tutor02', '강사 Brian', '010-3001-4002', 'brian.tutor@example.com', '1'),
  ('tutor03', '강사 Chloe', '010-3001-4003', 'chloe.tutor@example.com', '1'),
  ('tutor04', '강사 Daniel', '010-3001-4004', 'daniel.tutor@example.com', '1'),
  ('tutor05', '강사 Emily', '010-3001-4005', 'emily.tutor@example.com', '1');

INSERT INTO TBL_COURSE (
  courseCode,
  courseName,
  courseLevel,
  courseDescription,
  display
) VALUES
  ('COURSE_BASIC', '기초 회화 과정', '입문', '영어 회화 기초 표현과 발음 연습 과정', '1'),
  ('COURSE_BUSINESS', '비즈니스 영어 과정', '중급', '회의, 이메일, 발표 표현 중심 과정', '1'),
  ('COURSE_OPIC', 'OPIc 대비 과정', '중급', 'OPIc 시험 답변 구성과 말하기 연습 과정', '1'),
  ('COURSE_KIDS', '주니어 영어 과정', '초급', '초등 학습자 대상 회화 과정', '1'),
  ('COURSE_FREE', '프리토킹 과정', '고급', '주제별 자유 대화 중심 과정', '1');

INSERT INTO TBL_ENROLLMENT (
  enrollmentId,
  studentId,
  courseCode,
  tutorId,
  lessonStartDate,
  lessonCount,
  lessonStartTime,
  lessonDurationMinutes,
  enrollmentStatus,
  studentRequestDesc
) VALUES
  ('ENR2026052501', 'stu2026001', 'COURSE_BASIC', 'tutor01', '2026-06-01', 32, '19:00:00', 20, 1, '월수금 저녁 수업 희망'),
  ('ENR2026052502', 'stu2026002', 'COURSE_BUSINESS', 'tutor02', '2026-06-02', 40, '20:00:00', 40, 1, '화목 업무 영어 중심 수업 희망'),
  ('ENR2026052503', 'stu2026003', 'COURSE_OPIC', 'tutor03', '2026-06-01', 32, '21:00:00', 20, 1, '월수 시험 대비 수업 희망'),
  ('ENR2026052504', 'stu2026004', 'COURSE_KIDS', 'tutor04', '2026-06-02', 40, '18:30:00', 20, 1, '화목금 주니어 수업 희망'),
  ('ENR2026052505', 'stu2026005', 'COURSE_FREE', 'tutor05', '2026-06-03', 32, '07:30:00', 40, 1, '수금 오전 프리토킹 희망');

INSERT INTO TBL_ENROLLMENT_WEEKDAY (enrollmentSeq, dayOfWeek)
SELECT enrollmentSeq, 0 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052501'
UNION ALL SELECT enrollmentSeq, 2 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052501'
UNION ALL SELECT enrollmentSeq, 4 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052501'
UNION ALL SELECT enrollmentSeq, 1 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052502'
UNION ALL SELECT enrollmentSeq, 3 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052502'
UNION ALL SELECT enrollmentSeq, 0 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052503'
UNION ALL SELECT enrollmentSeq, 2 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052503'
UNION ALL SELECT enrollmentSeq, 1 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052504'
UNION ALL SELECT enrollmentSeq, 3 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052504'
UNION ALL SELECT enrollmentSeq, 4 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052504'
UNION ALL SELECT enrollmentSeq, 2 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052505'
UNION ALL SELECT enrollmentSeq, 4 FROM TBL_ENROLLMENT WHERE enrollmentId = 'ENR2026052505';

INSERT INTO TBL_CLASS_SCHEDULE (
  classId,
  enrollmentSeq,
  lessonRound,
  classDate,
  dayOfWeek,
  classStartTime,
  classEndTime,
  classDurationMinutes,
  tutorId,
  classStatus,
  classUrl,
  classMemo
)
WITH RECURSIVE day_numbers AS (
  SELECT 0 AS dayOffset
  UNION ALL
  SELECT dayOffset + 1
  FROM day_numbers
  WHERE dayOffset < 365
),
class_candidates AS (
  SELECT
    e.enrollmentSeq,
    e.enrollmentId,
    e.lessonCount,
    e.lessonStartTime,
    e.lessonDurationMinutes,
    e.tutorId,
    DATE_ADD(e.lessonStartDate, INTERVAL dn.dayOffset DAY) AS classDate,
    WEEKDAY(DATE_ADD(e.lessonStartDate, INTERVAL dn.dayOffset DAY)) AS dayOfWeek
  FROM TBL_ENROLLMENT e
  JOIN day_numbers dn
  JOIN TBL_ENROLLMENT_WEEKDAY ew
    ON ew.enrollmentSeq = e.enrollmentSeq
    AND ew.dayOfWeek = WEEKDAY(DATE_ADD(e.lessonStartDate, INTERVAL dn.dayOffset DAY))
  WHERE e.enrollmentStatus IN (1, 2)
),
ranked_classes AS (
  SELECT
    enrollmentSeq,
    enrollmentId,
    lessonCount,
    lessonStartTime,
    lessonDurationMinutes,
    tutorId,
    classDate,
    dayOfWeek,
    ROW_NUMBER() OVER (PARTITION BY enrollmentSeq ORDER BY classDate ASC) AS lessonRound
  FROM class_candidates
)
SELECT
  CONCAT('CLS', DATE_FORMAT(classDate, '%Y%m%d'), LPAD(enrollmentSeq, 3, '0'), LPAD(lessonRound, 2, '0')) AS classId,
  enrollmentSeq,
  lessonRound,
  classDate,
  dayOfWeek,
  lessonStartTime AS classStartTime,
  ADDTIME(lessonStartTime, SEC_TO_TIME(lessonDurationMinutes * 60)) AS classEndTime,
  lessonDurationMinutes AS classDurationMinutes,
  tutorId,
  1 AS classStatus,
  CONCAT('https://class.example.com/', enrollmentId, '/', LPAD(lessonRound, 2, '0')) AS classUrl,
  CONCAT(lessonRound, '회차 자동 생성 수업') AS classMemo
FROM ranked_classes
WHERE lessonRound <= lessonCount
ORDER BY enrollmentSeq, lessonRound;

SELECT 'TBL_STUDENT' AS tableName, COUNT(*) AS rowCount FROM TBL_STUDENT
UNION ALL SELECT 'TBL_TUTOR', COUNT(*) FROM TBL_TUTOR
UNION ALL SELECT 'TBL_COURSE', COUNT(*) FROM TBL_COURSE
UNION ALL SELECT 'TBL_ENROLLMENT', COUNT(*) FROM TBL_ENROLLMENT
UNION ALL SELECT 'TBL_ENROLLMENT_WEEKDAY', COUNT(*) FROM TBL_ENROLLMENT_WEEKDAY
UNION ALL SELECT 'TBL_CLASS_SCHEDULE', COUNT(*) FROM TBL_CLASS_SCHEDULE;

SELECT
  e.enrollmentId,
  s.studentId,
  s.studentNo,
  s.studentName,
  c.courseName,
  e.lessonStartDate,
  e.lessonCount,
  (
    SELECT GROUP_CONCAT(
      CASE ew2.dayOfWeek
        WHEN 0 THEN '월'
        WHEN 1 THEN '화'
        WHEN 2 THEN '수'
        WHEN 3 THEN '목'
        WHEN 4 THEN '금'
        WHEN 5 THEN '토'
        WHEN 6 THEN '일'
      END
      ORDER BY ew2.dayOfWeek
      SEPARATOR ''
    )
    FROM TBL_ENROLLMENT_WEEKDAY ew2
    WHERE ew2.enrollmentSeq = e.enrollmentSeq
  ) AS lessonDays,
  TIME_FORMAT(e.lessonStartTime, '%H:%i') AS lessonStartTime,
  CONCAT(e.lessonDurationMinutes, '분') AS lessonDuration,
  t.tutorName
FROM TBL_ENROLLMENT e
JOIN TBL_STUDENT s ON s.studentId = e.studentId
JOIN TBL_COURSE c ON c.courseCode = e.courseCode
JOIN TBL_TUTOR t ON t.tutorId = e.tutorId
ORDER BY e.enrollmentSeq;

SELECT
  cs.classId,
  e.enrollmentId,
  cs.lessonRound,
  cs.classDate,
  CASE cs.dayOfWeek
    WHEN 0 THEN '월'
    WHEN 1 THEN '화'
    WHEN 2 THEN '수'
    WHEN 3 THEN '목'
    WHEN 4 THEN '금'
    WHEN 5 THEN '토'
    WHEN 6 THEN '일'
  END AS dayName,
  TIME_FORMAT(cs.classStartTime, '%H:%i') AS classStartTime,
  TIME_FORMAT(cs.classEndTime, '%H:%i') AS classEndTime,
  t.tutorName
FROM TBL_CLASS_SCHEDULE cs
JOIN TBL_ENROLLMENT e ON e.enrollmentSeq = cs.enrollmentSeq
JOIN TBL_TUTOR t ON t.tutorId = cs.tutorId
WHERE e.enrollmentId = 'ENR2026052501'
ORDER BY cs.lessonRound
LIMIT 10;

SELECT
  'class_count_matches_enrollment_lesson_count' AS checkName,
  (SELECT SUM(lessonCount) FROM TBL_ENROLLMENT WHERE enrollmentStatus IN (1, 2)) AS expectedCount,
  (SELECT COUNT(*) FROM TBL_CLASS_SCHEDULE) AS actualCount,
  CASE
    WHEN (SELECT SUM(lessonCount) FROM TBL_ENROLLMENT WHERE enrollmentStatus IN (1, 2)) = (SELECT COUNT(*) FROM TBL_CLASS_SCHEDULE)
      THEN 'OK'
    ELSE 'FAIL'
  END AS result;

SELECT
  'weekday_mismatch_count' AS checkName,
  COUNT(*) AS mismatchCount
FROM TBL_CLASS_SCHEDULE cs
LEFT JOIN TBL_ENROLLMENT_WEEKDAY ew
  ON ew.enrollmentSeq = cs.enrollmentSeq
  AND ew.dayOfWeek = cs.dayOfWeek
WHERE ew.enrollmentWeekdaySeq IS NULL;

SELECT
  'tutor_time_overlap_count' AS checkName,
  COUNT(*) AS overlapCount
FROM TBL_CLASS_SCHEDULE a
JOIN TBL_CLASS_SCHEDULE b
  ON a.classSeq < b.classSeq
  AND a.tutorId = b.tutorId
  AND a.classDate = b.classDate
  AND a.classStartTime < b.classEndTime
  AND b.classStartTime < a.classEndTime;
