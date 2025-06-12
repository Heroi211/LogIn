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
    
def calcular_diferenca_horas(dt_inicio: datetime, dt_fim: datetime,dt_pause:datetime,dt_replay:datetime) -> float:
    """
    Calcula a diferença em horas entre duas datas, descontando o tempo de pausa se fornecido.
    :param dt_inicio: Data e hora de início.
    :param dt_fim: Data e hora de fim.
    :param dt_pause: Data e hora em que a task foi pausada (opcional).
    :param dt_replay: Data e hora em que a task foi retomada (opcional).
    :return: Diferença em horas, descontando o tempo de pausa.
    """
    if dt_inicio is None or dt_fim is None:
        return 0.0

    total_seconds = (dt_fim - dt_inicio).total_seconds()

    if dt_pause is not None and dt_replay is not None:
        # Só desconta se dt_pause < dt_replay e ambos dentro do intervalo
        pause_start = max(dt_pause, dt_inicio)
        pause_end = min(dt_replay, dt_fim)
        if pause_end > pause_start:
            pause_seconds = (pause_end - pause_start).total_seconds()
            total_seconds -= pause_seconds

    return total_seconds / 3600.0

