import pytz
from datetime import datetime, time
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
    
def calcular_diferenca_horas(dt_inicio: datetime, dt_fim: datetime,dt_pause:datetime,dt_replay:datetime) -> float:
    """
    Calcula a diferença em horas entre duas datas, descontando o tempo de pausa se fornecido.
    :param dt_inicio: Data e hora de início.
    :param dt_fim: Data e hora de fim.
    :param dt_pause: Data e hora em que a task foi pausada (opcional).
    :param dt_replay: Data e hora em que a task foi retomada (opcional).
    :return: Diferença em horas, descontando o tempo de pausa.
    """
    
    if not dt_inicio or not dt_fim:
        return 0.0

    # Se vier somente time, combine com a data de início
    if isinstance(dt_pause, time):
        dt_pause = datetime.combine(dt_inicio.date(), dt_pause, tzinfo=dt_inicio.tzinfo)
    if isinstance(dt_replay, time):
        dt_replay = datetime.combine(dt_inicio.date(), dt_replay, tzinfo=dt_inicio.tzinfo)

    total_seconds = (dt_fim - dt_inicio).total_seconds()

    if dt_pause and dt_replay:
        pause_start = max(dt_pause, dt_inicio)
        pause_end   = min(dt_replay, dt_fim)
        if pause_end > pause_start:
            total_seconds -= (pause_end - pause_start).total_seconds()

    return total_seconds / 3600.0

