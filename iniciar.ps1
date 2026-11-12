# Inicia a interface de testes do Google ADK somente na maquina local.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path '.env')) { throw 'Crie o .env com .\configurar.ps1 antes de iniciar.' }
if (-not (Test-Path '.venv\Scripts\adk.exe')) { throw 'Instale as dependencias com .\configurar.ps1 antes de iniciar.' }
Write-Host 'Acesse http://localhost:8000 e selecione agente_tarefas.'
& .\.venv\Scripts\adk.exe web --port 8000
