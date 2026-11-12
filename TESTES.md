# Relatório de testes — Agente DIO

## Testes automatizados

- **Data:** 12/11/2026.
- **Comando:** `python -m pytest -q` no diretório do projeto.
- **Resultado:** `9 passed` (confirmado no ambiente local do autor e novamente no ambiente de preparação do pacote).
- **Escopo:** testes com simulações das APIs; validam a lógica isolada, **não** substituem os testes reais.

## Testes de integração reais

Foram executados no computador do autor, usando **Google ADK Web 2.14.0**, Gemini e a API Trello com o quadro **DIO**, em 12/11/2026. Os prints reais estão em [`evidencias/`](evidencias/README.md).

1. `listar_tarefas("todas")`: confirmou quadro inicialmente vazio.
2. `criar_tarefa`: criou **Estudar Python** em **A fazer**, com descrição e vencimento 12/11/2026.
3. `mudar_status_tarefa`: moveu o cartão de **A fazer** para **Em andamento**.
4. `mudar_status_tarefa`: moveu o cartão de **Em andamento** para **Concluído**.
5. `listar_tarefas("todas")`: confirmou **Estudar Python** em **Concluído**.

O resultado de cada operação foi verificado tanto pelo retorno da ferramenta no ADK quanto pela interface do Trello.

## Segurança

- O pacote contém **somente** `.env.exemplo`, com valores fictícios; `.env` real não foi incluído.
- `.gitignore` exclui `.env`, ambientes virtuais, bancos locais e outros arquivos sensíveis.
- As capturas não exibem chaves ou tokens de API.
