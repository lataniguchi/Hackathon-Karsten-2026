@echo off
title Testes Automatizados
echo ==========================================
echo    Executando Testes Automatizados
echo ==========================================
echo.
cd /d "%~dp0\.."
python testes\executar_testes.py
echo.
pause

