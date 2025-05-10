import pytz
from datetime import datetime
from typing import Optional


def to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None

    if dt.tzinfo is None:
        sp = pytz.timezone("America/Sao_Paulo")
        dt = sp.localize(dt)
    dt_utc = dt.astimezone(pytz.UTC).replace(tzinfo=None)
    return dt_utc

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

