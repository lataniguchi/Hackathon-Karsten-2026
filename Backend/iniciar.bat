@echo off
title API Auto-T&M Karsten
echo ==========================================
echo    Iniciando o Backend - Hackathon Karsten
echo ==========================================
echo.
echo [1/2] Verificando e instalando dependencias...
pip install -r requirements.txt --only-binary=:all:
echo.
echo [2/2] Iniciando o servidor FastAPI...
echo Acesse no navegador para testar: http://127.0.0.1:8000/docs
echo.
python -m uvicorn main:app --reload
pause