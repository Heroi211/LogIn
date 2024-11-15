import pytz
from datetime import datetime

def to_utc(dt:datetime) -> datetime:
        if dt and dt.tzinfo:
            return dt.astimezone(pytz.UTC).replace(tzinfo=None)
        return dt

def utcnow() -> datetime:
    return datetime.now(pytz.UTC).replace(tzinfo=None)