@echo off
setlocal
title API Auto-T&M Karsten
echo ==========================================
echo    Iniciando o sistema - Hackathon Karsten
echo ==========================================
echo.
cd /d "%~dp0"
if errorlevel 1 (
   echo ERRO: nao foi possivel acessar a pasta do Backend.
   pause
   exit /b 1
)

echo [1/3] Verificando se a API ja esta ativa...
curl.exe --silent --fail http://127.0.0.1:8000/ >nul 2>&1
if errorlevel 1 (
   echo [2/3] Instalando dependencias...
   python -m pip install -r requirements.txt --only-binary=:all:
   if errorlevel 1 (
       echo.
       echo ERRO: falha ao instalar dependencias. Verifique sua conexao e instalacao do Python.
       pause
       exit /b 1
   )

   echo Iniciando o servidor FastAPI...
   start "API Auto-T&M Karsten" /D "%~dp0" python -m uvicorn main:app --reload
) else (
   echo A API ja esta ativa; sera reutilizada.
)

echo.
echo [3/3] Aguardando a API ficar pronta...
powershell -NoProfile -Command "$ok = $false; for ($i = 0; $i -lt 60; $i++) { try { Invoke-RestMethod -Uri 'http://127.0.0.1:8000/' -TimeoutSec 2 | Out-Null; $ok = $true; break } catch { Start-Sleep -Seconds 1 } }; if (-not $ok) { exit 1 }"
if errorlevel 1 (
   echo.
   echo ERRO: a API nao respondeu em http://127.0.0.1:8000/.
   echo Confira a janela do servidor para ver os detalhes.
   pause
   exit /b 1
)

echo API pronta. Abrindo o painel...
start "" "%~dp0..\Frontend\index.html"
echo.
echo Painel: abra a pagina que acabou de iniciar no navegador.
echo Documentacao da API: http://127.0.0.1:8000/docs
echo.
echo Voce pode fechar esta janela; a API continua na janela do servidor.
exit /b 0