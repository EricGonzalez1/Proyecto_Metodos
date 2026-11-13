@echo off
title Proyecto de Metodos Numericos
cd /d "%~dp0"

REM Intentar abrir sin ventana de consola usando pythonw o pyw en Windows
where pyw >nul 2>nul
if %errorlevel%==0 (
    start "" pyw "%~dp0main.py"
    exit /b 0
)

where pythonw >nul 2>nul
if %errorlevel%==0 (
    start "" pythonw "%~dp0main.py"
    exit /b 0
)

where py >nul 2>nul
if %errorlevel%==0 (
    py -3 "%~dp0main.py"
    exit /b 0
)

where python >nul 2>nul
if %errorlevel%==0 (
    python "%~dp0main.py"
    exit /b 0
)

echo No se encontro una instalacion de Python en el PATH de Windows.
echo Por favor instala Python 3 desde https://www.python.org/ marcando la casilla "Add Python to PATH".
pause
