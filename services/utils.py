import pytz
from datetime import datetime


def utcnow() -> datetime:
    return datetime.now(pytz.UTC).replace(tzinfo=None)
