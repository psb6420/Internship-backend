import math
import re
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.db import get_connection

DAY_NAMES = {
    0: '월',
    1: '화',
    2: '수',
    3: '목',
    4: '금',
}

app = FastAPI(
    title='Tutor Available Time API',
    description='2026 더존ICT그룹 인턴쉽 백엔드 강사 가능시간 조회 API',
    version='1.0.0',
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
    searchEndTime: str
    durationMinutes: int
    availableTutors: list[AvailableTutor]


def format_time(value):
    if value is None:
        return None

    text = str(value)
    return text[:5]


def validate_search_request(request: AvailableTutorSearchRequest):
    days = list(dict.fromkeys(request.days))
    if not days:
        raise HTTPException(status_code=400, detail='요일을 1개 이상 입력해 주세요.')

    invalid_days = [day for day in days if day not in DAY_NAMES]
    if invalid_days:
        raise HTTPException(
            status_code=400,
            detail='요일은 0=월, 1=화, 2=수, 3=목, 4=금 범위로 입력해 주세요.',
        )

    if not re.fullmatch(r'\d{2}:\d{2}', request.startTime):
        raise HTTPException(status_code=400, detail='시작시간은 HH:MM 형식으로 입력해 주세요.')

    try:
        start_datetime = datetime.strptime(request.startTime, '%H:%M')
    except ValueError as exc:
        raise HTTPException(status_code=400, detail='올바른 시작시간을 입력해 주세요.') from exc

    if start_datetime.minute % 5 != 0:
        raise HTTPException(status_code=400, detail='시작시간은 5분 단위로 입력해 주세요.')

    if request.durationMinutes < 1:
        raise HTTPException(status_code=400, detail='학습시간은 1분 이상으로 입력해 주세요.')

    requested_end_datetime = start_datetime + timedelta(minutes=request.durationMinutes)
    required_slots = math.ceil(request.durationMinutes / 5)
    search_end_datetime = start_datetime + timedelta(minutes=required_slots * 5)

    if search_end_datetime.date() != start_datetime.date():
        raise HTTPException(status_code=400, detail='검색 종료 시간이 하루를 넘을 수 없습니다.')

    return days, start_datetime, requested_end_datetime, search_end_datetime, required_slots


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
    days, start_datetime, requested_end_datetime, search_end_datetime, required_slots = (
        validate_search_request(request)
    )
    placeholders = ', '.join(['%s'] * len(days))
    query = f"""
        SELECT
            tutorId,
            tutorName,
            dayOfWeek,
            COUNT(*) AS matchedSlotCount
        FROM TBL_TUTOR_AVAILABLE_TIME
        WHERE display = '1'
            AND dayOfWeek IN ({placeholders})
            AND slotStartTime >= %s
            AND slotEndTime <= %s
        GROUP BY tutorId, tutorName, dayOfWeek
        HAVING matchedSlotCount >= %s
        ORDER BY tutorId ASC, dayOfWeek ASC
    """
    params = [
        *days,
        start_datetime.strftime('%H:%M:%S'),
        search_end_datetime.strftime('%H:%M:%S'),
        required_slots,
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
        'searchEndTime': search_end_datetime.strftime('%H:%M'),
        'durationMinutes': request.durationMinutes,
        'availableTutors': available_tutors,
    }
