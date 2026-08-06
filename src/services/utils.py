from datetime import datetime

import pytz


def utcnow() -> datetime:
    return datetime.now(pytz.UTC).replace(tzinfo=None)
