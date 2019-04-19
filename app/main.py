from datetime import date, timedelta
from fastapi import FastAPI
from pydantic import BaseModel
from numpy import busday_count, busday_offset
from starlette.middleware.cors import CORSMiddleware
import holidays

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])


@app.get("/api/analyze")
async def analyze(start_date: date, end_date: date):
    end_date = end_date + timedelta(days=1)  # include last day
    days = (end_date - start_date).days
    colombia_holidays = holidays.CO()
    holidays_range = colombia_holidays[start_date:end_date]
    public_holidays = {
        holiday: colombia_holidays.get(holiday) for holiday in holidays_range
    }
    working_days = busday_count(start_date, end_date, holidays=holidays_range)
    weekend_days = busday_count(start_date, end_date, weekmask="0000011")
    return {
        "days": days,
        "working_days": working_days.item(),
        "weekend_days": weekend_days.item(),
        "public_holidays": public_holidays,
    }


@app.get("/api/add-working-days")
async def add_working_days(start_date: date, increment: int):
    end_date_without_holidays = busday_offset(
        start_date, increment, roll="forward"
    ).item()
    co_holidays = holidays.CO()
    holidays_range = co_holidays[start_date:end_date_without_holidays]
    end_date = busday_offset(
        start_date, increment, holidays=holidays_range, roll="forward"
    )
    return end_date.item()
