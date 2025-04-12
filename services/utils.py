import pytz
from datetime import datetime

def to_utc(dt: datetime) -> str:
    if dt and dt.tzinfo:
        dt = dt.astimezone(pytz.UTC).replace(tzinfo=None)
    return dt.strftime("%d:%m:%Y %H:%M") if dt else None

def utcnow() -> datetime:
    return datetime.now(pytz.UTC).replace(tzinfo=None)

def processar_origem(origem: int):
    try:
        if origem not in [1, 2]:
            raise Exception("Origem inválida")
        if origem == 1:
            return 1 #Client ID
        elif origem == 2:
            return 2 #User ID
    except Exception as e:
        return None

