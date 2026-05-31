import re
import secrets
from datetime import date, datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.db import get_connection

DAY_NAMES = {
    0: '월',
    1: '화',
    2: '수',
    3: '목',
    4: '금',
    5: '토',
    6: '일',
}

CLASS_DAY_PATTERNS = {
    'MWF': {'label': '월수금', 'days': [0, 2, 4]},
    'TT': {'label': '화목', 'days': [1, 3]},
}

FIXED_STUDENT_ID = 'stu2026001'
FIXED_LESSON_COUNT = 32
FIXED_LESSON_DURATION_MINUTES = 20

app = FastAPI(
    title='Tutor Available Time API',
    description='2026 더존ICT그룹 인턴쉽 백엔드 강사 가능시간 및 수강신청 API',
    version='2.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost:5173',
        'http://127.0.0.1:5173',
        'http://localhost:5174',
        'http://127.0.0.1:5174',
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class TimeSlot(BaseModel):
    startTime: str
    endTime: str


class DayAvailableTime(BaseModel):
    dayOfWeek: int
    dayName: str
    slots: list[TimeSlot]


class TutorAvailableTimeResponse(BaseModel):
    tutorId: str
    tutorName: str
    availableTimes: list[DayAvailableTime]


class AvailableTutorSearchRequest(BaseModel):
    days: list[int]
    startTime: str
    durationMinutes: int


class AvailableDay(BaseModel):
    dayOfWeek: int
    dayName: str


class AvailableTutor(BaseModel):
    tutorId: str
    tutorName: str
    availableDays: list[AvailableDay]


class AvailableTutorSearchResponse(BaseModel):
    days: list[int]
    startTime: str
    requestedEndTime: str
    durationMinutes: int
    availableTutors: list[AvailableTutor]


class StudentOption(BaseModel):
    studentId: str
    studentNo: str
    studentName: str


class CourseOption(BaseModel):
    courseCode: str
    courseName: str
    courseLevel: str | None = None


class DayPatternOption(BaseModel):
    dayPatternCode: str
    dayPatternName: str
    days: list[int]
    dayNames: list[str]


class EnrollmentOptionsResponse(BaseModel):
    fixedStudent: StudentOption
    courses: list[CourseOption]
    dayPatterns: list[DayPatternOption]
    lessonCount: int
    lessonDurationMinutes: int
    startDateMin: date
    startDateMax: date


class EnrollmentAvailabilityRequest(BaseModel):
    courseCode: str
    startDate: date
    dayPatternCode: str


class EnrollmentSlotTutor(BaseModel):
    tutorId: str
    tutorName: str


class EnrollmentAvailableSlot(BaseModel):
    startTime: str
    endTime: str
    availableTutorCount: int
    tutors: list[EnrollmentSlotTutor]


class EnrollmentAvailabilityResponse(BaseModel):
    courseCode: str
    startDate: date
    firstClassDate: date
    lessonEndDate: date
    lessonCount: int
    lessonDurationMinutes: int
    dayPatternCode: str
    dayPatternName: str
    slots: list[EnrollmentAvailableSlot]


class EnrollmentCreateRequest(EnrollmentAvailabilityRequest):
    startTime: str
    tutorId: str
    studentRequestDesc: str | None = None


class CreatedClassSchedule(BaseModel):
    lessonRound: int
    classDate: date
    dayName: str
    classStartTime: str
    classEndTime: str


class EnrollmentCreateResponse(BaseModel):
    enrollmentId: str
    studentId: str
    courseCode: str
    courseName: str
    tutorId: str
    tutorName: str
    dayPatternCode: str
    dayPatternName: str
    lessonStartDate: date
    lessonEndDate: date
    lessonCount: int
    lessonStartTime: str
    lessonDurationMinutes: int
    createdClassCount: int
    schedules: list[CreatedClassSchedule]


def format_time(value):
    if value is None:
        return None

    text = str(value)
    return text[:5]


def parse_hhmm(value: str, field_name: str):
    if not re.fullmatch(r'\d{2}:\d{2}', value):
        raise HTTPException(status_code=400, detail=f'{field_name}은 HH:MM 형식으로 입력해 주세요.')

    try:
        parsed_datetime = datetime.strptime(value, '%H:%M')
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=f'올바른 {field_name}을 입력해 주세요.') from exc

    if parsed_datetime.minute % 5 != 0:
        raise HTTPException(status_code=400, detail=f'{field_name}은 5분 단위로 입력해 주세요.')

    return parsed_datetime


def validate_search_request(request: AvailableTutorSearchRequest):
    days = list(dict.fromkeys(request.days))
    if not days:
        raise HTTPException(status_code=400, detail='요일을 1개 이상 입력해 주세요.')

    invalid_days = [day for day in days if day not in DAY_NAMES]
    if invalid_days:
        raise HTTPException(
            status_code=400,
            detail='요일은 0=월, 1=화, 2=수, 3=목, 4=금, 5=토, 6=일 범위로 입력해 주세요.',
        )

    start_datetime = parse_hhmm(request.startTime, '시작시간')

    if request.durationMinutes < 1:
        raise HTTPException(status_code=400, detail='학습시간은 1분 이상으로 입력해 주세요.')

    requested_end_datetime = start_datetime + timedelta(minutes=request.durationMinutes)

    if requested_end_datetime.date() != start_datetime.date():
        raise HTTPException(status_code=400, detail='검색 종료 시간이 하루를 넘을 수 없습니다.')

    return days, start_datetime, requested_end_datetime


def get_day_pattern(day_pattern_code: str):
    pattern = CLASS_DAY_PATTERNS.get(day_pattern_code)
    if not pattern:
        raise HTTPException(status_code=400, detail='수업요일은 월수금 또는 화목 중에서 선택해 주세요.')

    return pattern


def validate_application_start_date(start_date: date):
    today = date.today()
    max_start_date = today + timedelta(days=365)

    if start_date < today or start_date > max_start_date:
        raise HTTPException(
            status_code=400,
            detail=f'수업시작일은 {today.isoformat()}부터 {max_start_date.isoformat()}까지 선택할 수 있습니다.',
        )


def build_class_dates(start_date: date, days: list[int], lesson_count: int):
    class_dates = []
    current_date = start_date

    while len(class_dates) < lesson_count:
        if current_date.weekday() in days:
            class_dates.append(current_date)
        current_date += timedelta(days=1)

    return class_dates


def build_enrollment_id():
    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    suffix = secrets.token_hex(2).upper()
    return f'ENR{timestamp}{suffix}'


def build_available_time_query(days: list[int], exact_start_time=False, exact_tutor=False):
    day_placeholders = ', '.join(['%s'] * len(days))
    exact_conditions = []

    if exact_start_time:
        exact_conditions.append('ct.candidateStartTime = %s')
    if exact_tutor:
        exact_conditions.append('ct.tutorId = %s')

    exact_clause = ''
    if exact_conditions:
        exact_clause = ' AND ' + ' AND '.join(exact_conditions)

    return f"""
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
                    DATE_ADD(%s, INTERVAL dayOffset DAY) AS classDate,
                    WEEKDAY(DATE_ADD(%s, INTERVAL dayOffset DAY)) AS dayOfWeek,
                    ROW_NUMBER() OVER (
                        ORDER BY DATE_ADD(%s, INTERVAL dayOffset DAY)
                    ) AS lessonRound
                FROM day_numbers
                WHERE WEEKDAY(DATE_ADD(%s, INTERVAL dayOffset DAY)) IN ({day_placeholders})
            ) class_days
            WHERE lessonRound <= %s
        ),
        candidate_day_times AS (
            SELECT
                seed.tutorId,
                tutor.tutorName,
                seed.dayOfWeek,
                seed.slotStartTime AS candidateStartTime,
                ADDTIME(seed.slotStartTime, SEC_TO_TIME(%s * 60)) AS candidateEndTime,
                SUM(
                    TIME_TO_SEC(
                        TIMEDIFF(
                            LEAST(
                                slot.slotEndTime,
                                ADDTIME(seed.slotStartTime, SEC_TO_TIME(%s * 60))
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
                AND slot.slotStartTime < ADDTIME(seed.slotStartTime, SEC_TO_TIME(%s * 60))
                AND slot.slotEndTime > seed.slotStartTime
            WHERE seed.display = '1'
                AND seed.dayOfWeek IN ({day_placeholders})
                AND ADDTIME(seed.slotStartTime, SEC_TO_TIME(%s * 60)) <= TIME('23:59:59')
            GROUP BY seed.tutorId, tutor.tutorName, seed.dayOfWeek, seed.slotStartTime
            HAVING matchedMinutes >= %s
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
            HAVING availableDayCount = %s
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
        ){exact_clause}
        ORDER BY ct.candidateStartTime ASC, ct.tutorId ASC
    """


def build_available_time_params(
    start_date: date,
    days: list[int],
    exact_start_time: str | None = None,
    exact_tutor: str | None = None,
):
    params = [
        start_date,
        start_date,
        start_date,
        start_date,
        *days,
        FIXED_LESSON_COUNT,
        FIXED_LESSON_DURATION_MINUTES,
        FIXED_LESSON_DURATION_MINUTES,
        FIXED_LESSON_DURATION_MINUTES,
        *days,
        FIXED_LESSON_DURATION_MINUTES,
        FIXED_LESSON_DURATION_MINUTES,
        len(days),
    ]

    if exact_start_time:
        params.append(f'{exact_start_time}:00')
    if exact_tutor:
        params.append(exact_tutor)

    return params


def fetch_available_enrollment_rows(
    cursor,
    start_date: date,
    days: list[int],
    exact_start_time: str | None = None,
    exact_tutor: str | None = None,
):
    query = build_available_time_query(
        days,
        exact_start_time=bool(exact_start_time),
        exact_tutor=bool(exact_tutor),
    )
    params = build_available_time_params(start_date, days, exact_start_time, exact_tutor)
    cursor.execute(query, params)
    return cursor.fetchall()


def group_available_slots(rows):
    slot_map = {}

    for row in rows:
        start_time = format_time(row['candidateStartTime'])
        if start_time not in slot_map:
            slot_map[start_time] = {
                'startTime': start_time,
                'endTime': format_time(row['candidateEndTime']),
                'availableTutorCount': 0,
                'tutors': [],
            }

        slot_map[start_time]['tutors'].append(
            {
                'tutorId': row['tutorId'],
                'tutorName': row['tutorName'],
            },
        )
        slot_map[start_time]['availableTutorCount'] = len(slot_map[start_time]['tutors'])

    return list(slot_map.values())


@app.get(
    '/api/v1/tutors/{tutor_id}/available-times',
    summary='강사 가능시간 조회',
    description='강사 ID를 기준으로 요일별 가능시간을 조회합니다.',
    response_model=TutorAvailableTimeResponse,
    responses={
        404: {
            'description': '강사 가능시간 데이터 없음',
            'content': {
                'application/json': {
                    'example': {'detail': '강사 가능시간 데이터가 없습니다.'},
                },
            },
        },
    },
)
def get_tutor_available_times(tutor_id: str):
    query = """
        SELECT
            tutorId,
            tutorName,
            dayOfWeek,
            slotStartTime,
            slotEndTime
        FROM TBL_TUTOR_AVAILABLE_TIME
        WHERE tutorId = %s
            AND display = '1'
        ORDER BY dayOfWeek ASC, slotStartTime ASC
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, (tutor_id,))
            rows = cursor.fetchall()

    if not rows:
        raise HTTPException(
            status_code=404,
            detail='강사 가능시간 데이터가 없습니다.',
        )

    result = {
        'tutorId': rows[0]['tutorId'],
        'tutorName': rows[0]['tutorName'],
        'availableTimes': [],
    }

    day_map = {}
    for row in rows:
        day_of_week = row['dayOfWeek']
        if day_of_week not in day_map:
            day_map[day_of_week] = {
                'dayOfWeek': day_of_week,
                'dayName': DAY_NAMES.get(day_of_week, ''),
                'slots': [],
            }
            result['availableTimes'].append(day_map[day_of_week])

        day_map[day_of_week]['slots'].append(
            {
                'startTime': format_time(row['slotStartTime']),
                'endTime': format_time(row['slotEndTime']),
            },
        )

    return result


@app.post(
    '/api/v1/tutors/available-search',
    summary='조건 기반 가능 강사 검색',
    description='요일, 시작시간, 학습시간을 기준으로 수업 가능한 강사를 검색합니다.',
    response_model=AvailableTutorSearchResponse,
    responses={
        400: {
            'description': '잘못된 검색 조건',
            'content': {
                'application/json': {
                    'example': {'detail': '시작시간은 5분 단위로 입력해 주세요.'},
                },
            },
        },
    },
)
def search_available_tutors(request: AvailableTutorSearchRequest):
    days, start_datetime, requested_end_datetime = validate_search_request(request)
    placeholders = ', '.join(['%s'] * len(days))
    query = f"""
        SELECT
            tutorId,
            tutorName,
            dayOfWeek,
            SUM(
                TIME_TO_SEC(
                    TIMEDIFF(
                        LEAST(slotEndTime, %s),
                        GREATEST(slotStartTime, %s)
                    )
                ) / 60
            ) AS matchedMinutes
        FROM TBL_TUTOR_AVAILABLE_TIME
        WHERE display = '1'
            AND dayOfWeek IN ({placeholders})
            AND slotStartTime < %s
            AND slotEndTime > %s
        GROUP BY tutorId, tutorName, dayOfWeek
        HAVING matchedMinutes >= %s
        ORDER BY tutorId ASC, dayOfWeek ASC
    """
    params = [
        requested_end_datetime.strftime('%H:%M:%S'),
        start_datetime.strftime('%H:%M:%S'),
        *days,
        requested_end_datetime.strftime('%H:%M:%S'),
        start_datetime.strftime('%H:%M:%S'),
        request.durationMinutes,
    ]

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

    tutor_map = {}
    for row in rows:
        tutor_id = row['tutorId']
        if tutor_id not in tutor_map:
            tutor_map[tutor_id] = {
                'tutorId': tutor_id,
                'tutorName': row['tutorName'],
                'availableDays': [],
            }

        day_of_week = row['dayOfWeek']
        tutor_map[tutor_id]['availableDays'].append(
            {
                'dayOfWeek': day_of_week,
                'dayName': DAY_NAMES.get(day_of_week, ''),
            },
        )

    available_tutors = [
        tutor
        for tutor in tutor_map.values()
        if len(tutor['availableDays']) == len(days)
    ]

    return {
        'days': days,
        'startTime': start_datetime.strftime('%H:%M'),
        'requestedEndTime': requested_end_datetime.strftime('%H:%M'),
        'durationMinutes': request.durationMinutes,
        'availableTutors': available_tutors,
    }


@app.get(
    '/api/v1/enrollments/options',
    summary='수강신청 선택 옵션 조회',
    description='고정 학생, 과정 목록, 수업요일, 신청 가능 시작일 범위를 조회합니다.',
    response_model=EnrollmentOptionsResponse,
)
def get_enrollment_options():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT studentId, studentNo, studentName
                FROM TBL_STUDENT
                WHERE studentId = %s
                    AND display = '1'
                """,
                (FIXED_STUDENT_ID,),
            )
            student = cursor.fetchone()

            cursor.execute(
                """
                SELECT courseCode, courseName, courseLevel
                FROM TBL_COURSE
                WHERE display = '1'
                ORDER BY courseSeq ASC
                """,
            )
            courses = cursor.fetchall()

    if not student:
        raise HTTPException(status_code=404, detail='고정 학생 데이터가 없습니다.')
    if not courses:
        raise HTTPException(status_code=404, detail='수업과정 데이터가 없습니다.')

    today = date.today()
    return {
        'fixedStudent': student,
        'courses': courses,
        'dayPatterns': [
            {
                'dayPatternCode': pattern_code,
                'dayPatternName': pattern['label'],
                'days': pattern['days'],
                'dayNames': [DAY_NAMES[day] for day in pattern['days']],
            }
            for pattern_code, pattern in CLASS_DAY_PATTERNS.items()
        ],
        'lessonCount': FIXED_LESSON_COUNT,
        'lessonDurationMinutes': FIXED_LESSON_DURATION_MINUTES,
        'startDateMin': today,
        'startDateMax': today + timedelta(days=365),
    }


@app.post(
    '/api/v1/enrollments/available-times',
    summary='수강신청 가능시간 조회',
    description='수업요일, 시작일, 기존 수업 배정 현황을 기준으로 신청 가능한 강사/시간을 조회합니다.',
    response_model=EnrollmentAvailabilityResponse,
)
def search_enrollment_available_times(request: EnrollmentAvailabilityRequest):
    pattern = get_day_pattern(request.dayPatternCode)
    validate_application_start_date(request.startDate)
    class_dates = build_class_dates(request.startDate, pattern['days'], FIXED_LESSON_COUNT)

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT courseCode
                FROM TBL_COURSE
                WHERE courseCode = %s
                    AND display = '1'
                """,
                (request.courseCode,),
            )
            if not cursor.fetchone():
                raise HTTPException(status_code=400, detail='사용 가능한 과정이 아닙니다.')

            rows = fetch_available_enrollment_rows(cursor, request.startDate, pattern['days'])

    return {
        'courseCode': request.courseCode,
        'startDate': request.startDate,
        'firstClassDate': class_dates[0],
        'lessonEndDate': class_dates[-1],
        'lessonCount': FIXED_LESSON_COUNT,
        'lessonDurationMinutes': FIXED_LESSON_DURATION_MINUTES,
        'dayPatternCode': request.dayPatternCode,
        'dayPatternName': pattern['label'],
        'slots': group_available_slots(rows),
    }


@app.post(
    '/api/v1/enrollments',
    summary='수강신청 등록',
    description='선택한 시간과 강사가 아직 가능한지 다시 확인한 뒤 수강신청과 일자별 수업정보를 등록합니다.',
    response_model=EnrollmentCreateResponse,
)
def create_enrollment(request: EnrollmentCreateRequest):
    pattern = get_day_pattern(request.dayPatternCode)
    validate_application_start_date(request.startDate)
    start_datetime = parse_hhmm(request.startTime, '수업 시작시간')
    end_datetime = start_datetime + timedelta(minutes=FIXED_LESSON_DURATION_MINUTES)

    if end_datetime.date() != start_datetime.date():
        raise HTTPException(status_code=400, detail='수업 종료 시간이 하루를 넘을 수 없습니다.')

    class_dates = build_class_dates(request.startDate, pattern['days'], FIXED_LESSON_COUNT)
    enrollment_id = build_enrollment_id()
    connection = get_connection()

    try:
        connection.begin()

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT courseCode, courseName
                FROM TBL_COURSE
                WHERE courseCode = %s
                    AND display = '1'
                """,
                (request.courseCode,),
            )
            course = cursor.fetchone()
            if not course:
                raise HTTPException(status_code=400, detail='사용 가능한 과정이 아닙니다.')

            cursor.execute(
                """
                SELECT studentId
                FROM TBL_STUDENT
                WHERE studentId = %s
                    AND display = '1'
                """,
                (FIXED_STUDENT_ID,),
            )
            if not cursor.fetchone():
                raise HTTPException(status_code=404, detail='고정 학생 데이터가 없습니다.')

            available_rows = fetch_available_enrollment_rows(
                cursor,
                request.startDate,
                pattern['days'],
                request.startTime,
                request.tutorId,
            )
            if not available_rows:
                raise HTTPException(status_code=409, detail='선택한 시간은 더 이상 신청할 수 없습니다.')

            tutor = available_rows[0]

            cursor.execute(
                """
                INSERT INTO TBL_ENROLLMENT (
                    enrollmentId,
                    studentId,
                    courseCode,
                    tutorId,
                    lessonStartDate,
                    lessonEndDate,
                    lessonCount,
                    lessonStartTime,
                    lessonDurationMinutes,
                    enrollmentStatus,
                    studentRequestDesc
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, %s
                )
                """,
                (
                    enrollment_id,
                    FIXED_STUDENT_ID,
                    request.courseCode,
                    request.tutorId,
                    class_dates[0],
                    class_dates[-1],
                    FIXED_LESSON_COUNT,
                    f'{request.startTime}:00',
                    FIXED_LESSON_DURATION_MINUTES,
                    request.studentRequestDesc,
                ),
            )
            enrollment_seq = cursor.lastrowid

            cursor.executemany(
                """
                INSERT INTO TBL_ENROLLMENT_WEEKDAY (enrollmentSeq, dayOfWeek)
                VALUES (%s, %s)
                """,
                [(enrollment_seq, day_of_week) for day_of_week in pattern['days']],
            )

            class_rows = []
            schedules = []
            for index, class_date in enumerate(class_dates, start=1):
                class_id = f'CLS{class_date.strftime("%Y%m%d")}{enrollment_seq:06d}{index:03d}'
                class_rows.append(
                    (
                        class_id,
                        enrollment_seq,
                        index,
                        class_date,
                        class_date.weekday(),
                        f'{request.startTime}:00',
                        end_datetime.strftime('%H:%M:%S'),
                        FIXED_LESSON_DURATION_MINUTES,
                        request.tutorId,
                        1,
                        f'https://class.example.com/{enrollment_id}/{index:02d}',
                        f'{index}회차 자동 생성 수업',
                    ),
                )
                schedules.append(
                    {
                        'lessonRound': index,
                        'classDate': class_date,
                        'dayName': DAY_NAMES[class_date.weekday()],
                        'classStartTime': request.startTime,
                        'classEndTime': end_datetime.strftime('%H:%M'),
                    },
                )

            cursor.executemany(
                """
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
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """,
                class_rows,
            )

        connection.commit()

    except HTTPException:
        connection.rollback()
        raise
    except Exception as exc:
        connection.rollback()
        raise HTTPException(status_code=500, detail='수강신청 등록 중 오류가 발생했습니다.') from exc
    finally:
        connection.close()

    return {
        'enrollmentId': enrollment_id,
        'studentId': FIXED_STUDENT_ID,
        'courseCode': request.courseCode,
        'courseName': course['courseName'],
        'tutorId': request.tutorId,
        'tutorName': tutor['tutorName'],
        'dayPatternCode': request.dayPatternCode,
        'dayPatternName': pattern['label'],
        'lessonStartDate': class_dates[0],
        'lessonEndDate': class_dates[-1],
        'lessonCount': FIXED_LESSON_COUNT,
        'lessonStartTime': request.startTime,
        'lessonDurationMinutes': FIXED_LESSON_DURATION_MINUTES,
        'createdClassCount': len(class_rows),
        'schedules': schedules,
    }
