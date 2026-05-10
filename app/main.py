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


def format_time(value):
    if value is None:
        return None

    text = str(value)
    return text[:5]


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
