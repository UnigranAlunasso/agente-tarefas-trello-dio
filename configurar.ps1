# Configuração local (Windows PowerShell). Nenhuma credencial é enviada a este script.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    if (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv .venv
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv .venv
    } else {
        throw 'Instale o Python 3.10 ou superior antes de continuar.'
    }
}

& .\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw 'A instalacao das dependencias falhou.' }

if (-not (Test-Path '.env')) {
    Copy-Item -LiteralPath '.env.exemplo' -Destination '.env'
    Write-Host 'Arquivo .env criado. Edite as chaves SOMENTE no seu computador.' -ForegroundColor Yellow
    Start-Process -FilePath notepad.exe -ArgumentList ('"{0}"' -f (Join-Path $PSScriptRoot '.env'))
} else {
    Write-Host 'Arquivo .env ja existe; nao foi sobrescrito.' -ForegroundColor Yellow
}

& .\.venv\Scripts\python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Ha testes de unidade com falha.' }
Write-Host 'Configuracao e testes locais concluidos. Preencha o .env e execute .\iniciar.ps1.' -ForegroundColor Green
