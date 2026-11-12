"""Ponto de entrada do Google Agent Development Kit (ADK)."""

import os
from google.adk.agents import Agent

from .config import today_local
from .trello_tools import criar_tarefa, listar_tarefas, mudar_status_tarefa, obter_data_atual


def _instruction(_context) -> str:
    day = today_local().strftime("%d/%m/%Y")
    return f"""Você é o Organizador DIO, um agente de tarefas conectado ao quadro DIO do Trello.
Hoje é {day} no fuso horário do usuário. Ao iniciar uma nova conversa, cumprimente
brevemente e pergunte: 'Quais são as tarefas do seu dia {day}?'.

Use as ferramentas fornecidas para QUALQUER afirmação sobre tarefas reais no Trello.
Quando a pessoa listar várias tarefas, crie um cartão por tarefa via criar_tarefa,
com nome, descrição se disponível e data de hoje se outra data não for indicada.
Se o usuário trouxer outra data, passe-a no formato AAAA-MM-DD.
Para consultar tarefas, use listar_tarefas (todas ou filtradas).
Para movimentar tarefas, use mudar_status_tarefa; compreenda frases como
'comecei', 'estou fazendo', 'terminei', 'concluído' ou 'deixa para depois'.
Não diga que criou, concluiu ou moveu um cartão se a ferramenta retornar ok=false.
Se encontrar nomes duplicados, solicite o ID indicado por listar_tarefas.
Não invente cartões, datas de conclusão ou IDs. Nunca peça tokens ou senhas no chat.
Responda em português brasileiro, objetivamente.
"""


root_agent = Agent(
    name="organizador_dio",
    model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite"),
    description="Cria, lista e move tarefas no Trello por conversa com Gemini.",
    instruction=_instruction,
    tools=[obter_data_atual, criar_tarefa, listar_tarefas, mudar_status_tarefa],
)
