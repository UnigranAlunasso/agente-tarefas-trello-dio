"""Configuração do ambiente e datas locais do agente."""

import os
from datetime import date, datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from dotenv import load_dotenv

# A configuração real é local. Nunca versionar .env.
load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)


def get_timezone() -> ZoneInfo:
    name = os.getenv("APP_TIMEZONE", "America/Campo_Grande")
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError as exc:
        raise ValueError(f"Fuso horário inválido: {name}. Verifique APP_TIMEZONE.") from exc


def today_local() -> date:
    return datetime.now(get_timezone()).date()


def parse_due_date(due_date: str) -> tuple[date, str]:
    """Converte AAAA-MM-DD em instante UTC equivalente ao meio-dia local.

    Meio-dia local evita o efeito comum de mostrar a véspera ao usar
    meia-noite UTC. O Trello armazena instantes, não datas puras.
    """
    if not due_date:
        day = today_local()
    else:
        try:
            day = date.fromisoformat(due_date.strip())
        except (ValueError, AttributeError) as exc:
            raise ValueError("Data inválida. Use AAAA-MM-DD, por exemplo 2026-11-12.") from exc
    midday_local = datetime.combine(day, time(12, 0), tzinfo=get_timezone())
    return day, midday_local.astimezone(timezone.utc).isoformat()
