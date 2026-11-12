"""Ferramentas públicas para o Google ADK, implementadas com py-trello.

Cada função retorna um dicionário serializável com `ok`, `mensagem` e dados.
Erros operacionais são tratados sem divulgar tokens ou segredos.
"""

import os
import re
import unicodedata
from typing import Any

from .config import parse_due_date, today_local


STATUSES = ("A fazer", "Em andamento", "Concluído")


class TaskError(Exception):
    """Falha recuperável que pode ser apresentada ao usuário."""


def _norm(value: str) -> str:
    plain = unicodedata.normalize("NFKD", value or "")
    no_accents = "".join(c for c in plain if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", no_accents.strip().lower().replace("-", " ").replace("_", " "))


def _status(value: str, allow_all: bool = False) -> str:
    cleaned = _norm(value)
    synonyms = {
        "a fazer": "A fazer", "afazer": "A fazer", "pendente": "A fazer",
        "pendentes": "A fazer", "nao iniciado": "A fazer", "nao iniciada": "A fazer", "nao iniciadas": "A fazer", "por fazer": "A fazer",
        "em andamento": "Em andamento", "andamento": "Em andamento",
        "fazendo": "Em andamento", "em progresso": "Em andamento", "iniciado": "Em andamento",
        "concluido": "Concluído", "concluida": "Concluído", "concluidos": "Concluído", "concluidas": "Concluído",
        "feito": "Concluído", "feita": "Concluído", "feitos": "Concluído", "feitas": "Concluído", "finalizado": "Concluído",
        "finalizada": "Concluído", "finalizados": "Concluído", "finalizadas": "Concluído", "terminado": "Concluído", "terminada": "Concluído", "terminados": "Concluído", "terminadas": "Concluído",
    }
    if allow_all and cleaned in ("", "todos", "todas", "tudo", "all"):
        return "Todas"
    if cleaned not in synonyms:
        choices = "A fazer, Em andamento ou Concluído"
        raise TaskError(f"Status '{value}' não reconhecido. Use {choices}.")
    return synonyms[cleaned]


def _client():
    key = os.getenv("TRELLO_API_KEY", "").strip()
    token = os.getenv("TRELLO_API_TOKEN", "").strip()
    if not key or not token:
        raise TaskError("Configure TRELLO_API_KEY e TRELLO_API_TOKEN no arquivo .env local.")
    from trello import TrelloClient
    return TrelloClient(api_key=key, token=token)


def _board(client):
    configured_id = os.getenv("TRELLO_BOARD_ID", "").strip()
    if configured_id:
        return client.get_board(configured_id)
    name = os.getenv("TRELLO_BOARD_NAME", "DIO").strip()
    found = [b for b in client.list_boards(board_filter="open") if b.name.strip().casefold() == name.casefold()]
    if not found:
        raise TaskError(f"Quadro '{name}' não encontrado. Verifique TRELLO_BOARD_NAME ou defina TRELLO_BOARD_ID.")
    if len(found) > 1:
        raise TaskError("Há mais de um quadro com esse nome. Defina TRELLO_BOARD_ID no .env.")
    return found[0]


def _lists(board):
    listed = {item.name.strip(): item for item in board.list_lists(list_filter="open")}
    missing = [name for name in STATUSES if name not in listed]
    if missing:
        raise TaskError("O quadro precisa ter estas listas: " + ", ".join(STATUSES) + ".")
    return listed


def _safe_call(operation):
    try:
        return operation()
    except (TaskError, ValueError) as exc:
        return {"ok": False, "mensagem": str(exc)}
    except Exception:
        # Evitar repassar exceções HTTP, que podem conter dados sensíveis.
        return {"ok": False, "mensagem": "Falha na comunicação com o Trello. Verifique suas credenciais, conexão e permissões."}


def obter_data_atual() -> dict[str, Any]:
    """Retorna a data de hoje no fuso configurado para organizar tarefas."""
    def action():
        day = today_local()
        return {"ok": True, "data": day.isoformat(), "mensagem": f"Hoje é {day.strftime('%d/%m/%Y')} no fuso configurado."}
    return _safe_call(action)


def criar_tarefa(nome: str, descricao: str = "", data: str = "", status: str = "A fazer") -> dict[str, Any]:
    """Cria um cartão do Trello.

    Args:
        nome: Nome curto da tarefa.
        descricao: Detalhes opcionais do que precisa ser realizado.
        data: Data de vencimento AAAA-MM-DD; se vazia, usa hoje no fuso configurado.
        status: A fazer, Em andamento ou Concluído (aceita variações).
    """
    def action():
        task_name = nome.strip()
        if not task_name:
            raise TaskError("Informe o nome da tarefa.")
        desired = _status(status)
        day, due_utc = parse_due_date(data)
        target = _lists(_board(_client()))[desired]
        card = target.add_card(name=task_name, desc=descricao.strip(), due=due_utc)
        if desired == "Concluído":
            card.set_due_complete()
        return {"ok": True, "mensagem": "Tarefa criada.", "nome": task_name,
                "descricao": descricao.strip(), "data": day.isoformat(), "status": desired,
                "card_id": card.id, "url": getattr(card, "url", "")}
    return _safe_call(action)


def listar_tarefas(status: str = "todas") -> dict[str, Any]:
    """Lista todas as tarefas ou apenas as de um status (ex.: 'pendentes', 'concluido').

    Args:
        status: todas, A fazer, Em andamento ou Concluído; aceita variações.
    """
    def action():
        desired = _status(status, allow_all=True)
        lists = _lists(_board(_client()))
        names = STATUSES if desired == "Todas" else (desired,)
        tasks = []
        for name in names:
            for card in lists[name].list_cards(card_filter="open"):
                tasks.append({"nome": card.name, "descricao": getattr(card, "desc", "") or "",
                              "status": name, "data": getattr(card, "due", None),
                              "card_id": card.id, "url": getattr(card, "url", "")})
        return {"ok": True, "mensagem": f"{len(tasks)} tarefa(s) encontrada(s).",
                "total": len(tasks), "tarefas": tasks}
    return _safe_call(action)


def mudar_status_tarefa(nome: str, novo_status: str) -> dict[str, Any]:
    """Move uma tarefa para um novo status no mesmo quadro.

    Args:
        nome: Nome exato de um cartão ou ID do cartão. Se nomes duplicados, use o ID.
        novo_status: A fazer, Em andamento ou Concluído; aceita variações com/sem acento.
    """
    def action():
        desired = _status(novo_status)
        lists = _lists(_board(_client()))
        target = _norm(nome)
        if not target:
            raise TaskError("Informe o nome ou ID da tarefa.")
        candidates = []
        for current in STATUSES:
            for card in lists[current].list_cards(card_filter="open"):
                if _norm(card.name) == target or card.id.lower() == nome.strip().lower():
                    candidates.append((card, current))
        if not candidates:
            raise TaskError(f"Tarefa '{nome}' não encontrada no quadro.")
        if len(candidates) > 1:
            raise TaskError("Há cartões com o mesmo nome. Informe o ID de um deles (consulte listar_tarefas).")
        card, previous = candidates[0]
        if previous != desired:
            card.change_list(lists[desired].id)
            if desired == "Concluído":
                card.set_due_complete()
            elif previous == "Concluído":
                card.remove_due_complete()
        return {"ok": True, "mensagem": "Status atualizado." if previous != desired else "A tarefa já estava nesse status.",
                "nome": card.name, "status_anterior": previous, "status_atual": desired,
                "card_id": card.id, "url": getattr(card, "url", "")}
    return _safe_call(action)
