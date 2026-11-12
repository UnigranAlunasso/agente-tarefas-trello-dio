from datetime import date, datetime, timezone

import pytest

from agente_tarefas import trello_tools as tools
from agente_tarefas.config import parse_due_date


class FakeCard:
    def __init__(self, name, desc, due, list_id, identifier):
        self.id = identifier
        self.name = name
        self.desc = desc
        self.due = due
        self.url = f"https://trello.com/c/{identifier}"
        self.list_id = list_id
        self.due_complete = False
    def set_due_complete(self):
        self.due_complete = True
    def remove_due_complete(self):
        self.due_complete = False
    def change_list(self, list_id):
        self.list_id = list_id


class FakeList:
    def __init__(self, board, name):
        self.board = board
        self.name = name
        self.id = f"list-{name}"
    def add_card(self, name, desc, due):
        card = FakeCard(name, desc, due, self.id, f"card{len(self.board.cards)+1}")
        self.board.cards.append(card)
        return card
    def list_cards(self, card_filter="open"):
        return [c for c in self.board.cards if c.list_id == self.id]


class FakeBoard:
    def __init__(self):
        self.name = "DIO"
        self.id = "board123"
        self.cards = []
        self.lists = [FakeList(self, name) for name in tools.STATUSES]
    def list_lists(self, list_filter="open"):
        return self.lists


class FakeClient:
    def __init__(self, board):
        self.board = board
    def list_boards(self, board_filter="open"):
        return [self.board]
    def get_board(self, board_id):
        assert board_id == self.board.id
        return self.board


@pytest.fixture
def board(monkeypatch):
    board = FakeBoard()
    monkeypatch.setattr(tools, "_client", lambda: FakeClient(board))
    monkeypatch.setenv("TRELLO_BOARD_NAME", "DIO")
    monkeypatch.delenv("TRELLO_BOARD_ID", raising=False)
    return board


def test_create_list_move_with_accents(board):
    result = tools.criar_tarefa("Estudar Python", "Aula 1", "2026-11-12")
    assert result["ok"] and result["status"] == "A fazer"
    assert result["data"] == "2026-11-12"
    assert tools.listar_tarefas("pendentes")["total"] == 1
    assert tools.mudar_status_tarefa("Estudar Python", "em andamento")["ok"]
    assert tools.listar_tarefas("fazendo")["total"] == 1
    assert tools.mudar_status_tarefa("Estudar Python", "concluido")["ok"]
    assert board.cards[0].due_complete is True
    assert tools.listar_tarefas("concluído")["total"] == 1
    assert tools.mudar_status_tarefa("Estudar Python", "a fazer")["ok"]
    assert board.cards[0].due_complete is False


def test_all_and_status_filter(board):
    tools.criar_tarefa("T1", "", "2026-11-12")
    tools.criar_tarefa("T2", "", "2026-11-12", "Feito")
    assert tools.listar_tarefas("todas")["total"] == 2
    assert tools.listar_tarefas("concluídas")["total"] == 1
    assert tools.listar_tarefas("finalizado")["total"] == 1


def test_duplicate_names_safe(board):
    tools.criar_tarefa("Enviar relatório", data="2026-11-12")
    tools.criar_tarefa("Enviar relatório", data="2026-11-12")
    result = tools.mudar_status_tarefa("Enviar relatório", "feito")
    assert result["ok"] is False and "ID" in result["mensagem"]
    exact = tools.mudar_status_tarefa(board.cards[0].id, "feito")
    assert exact["ok"] is True


def test_bad_date_never_creates_card(board):
    assert tools.criar_tarefa("Teste", data="12/11/2026")["ok"] is False
    assert len(board.cards) == 0


def test_unknown_board_error(board, monkeypatch):
    monkeypatch.setenv("TRELLO_BOARD_NAME", "OUTRO")
    response = tools.listar_tarefas()
    assert response["ok"] is False
    assert "não encontrado" in response["mensagem"]


def test_invalid_status(board):
    response = tools.criar_tarefa("Estudar", status="desconhecido")
    assert not response["ok"]
    assert board.cards == []


def test_due_utc_corresponds_to_local_day(monkeypatch):
    monkeypatch.setenv("APP_TIMEZONE", "America/Campo_Grande")
    day, due = parse_due_date("2026-11-12")
    assert day == date(2026, 11, 12)
    assert datetime.fromisoformat(due).astimezone(timezone.utc).hour == 16


def test_communication_error_without_secret_leaks(board, monkeypatch):
    def fail():
        raise RuntimeError("https://example?token=SENHA_SUPER_SECRETA")
    monkeypatch.setattr(tools, "_client", fail)
    result = tools.listar_tarefas()
    assert not result["ok"]
    assert "SENHA_SUPER_SECRETA" not in str(result)


def test_blank_title(board):
    assert not tools.criar_tarefa("   ")["ok"]
    assert not board.cards
