# Evidências reais — Google ADK + Trello

Capturas de tela feitas durante a execução **real**, em **12/11/2026**, do agente `agente_tarefas` com Google ADK + Gemini + Trello (quadro **DIO**).

| Arquivo | O que comprova |
|---|---|
| [01-listagem-vazia-adk.png](01-listagem-vazia-adk.png) | `listar_tarefas("todas")` executado; quadro inicialmente vazio. |
| [02-criacao-adk.png](02-criacao-adk.png) | Comando em português para criar cartão e retorno de `criar_tarefa`. |
| [03-cartao-a-fazer-trello.png](03-cartao-a-fazer-trello.png) | Cartão `Estudar Python` criado na lista **A fazer** com vencimento. |
| [04-movimentacao-adk.png](04-movimentacao-adk.png) | `mudar_status_tarefa` executado para **Em andamento**. |
| [05-cartao-em-andamento-trello.png](05-cartao-em-andamento-trello.png) | Cartão exibido na lista **Em andamento**. |
| [06-conclusao-e-listagem-adk.png](06-conclusao-e-listagem-adk.png) | Agente move a tarefa para **Concluído** e lista o status confirmado. |
| [07-cartao-concluido-trello.png](07-cartao-concluido-trello.png) | Cartão visível na lista **Concluído** no quadro DIO. |

Não há chaves ou tokens de API incluídos nessas capturas. O `.env` é local e **não deve ser publicado**.
