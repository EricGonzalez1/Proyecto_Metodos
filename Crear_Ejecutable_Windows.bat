@echo off
title Generador de Ejecutable (.EXE) para Windows - Proyecto Metodos Numericos
cd /d "%~dp0"

echo ============================================================================
echo   GENERANDO ARCHIVO EJECUTABLE (.EXE) PARA WINDOWS CON PYINSTALLER
echo ============================================================================
echo.

python -m pip install --upgrade pyinstaller
if %errorlevel% neq 0 (
    py -3 -m pip install --upgrade pyinstaller
)

echo.
echo Compilando Proyecto_Metodos.exe (un solo archivo sin consola)...
python -m PyInstaller --noconsole --onefile --clean --name "Proyecto_Metodos" main.py
if %errorlevel% neq 0 (
    py -3 -m PyInstaller --noconsole --onefile --clean --name "Proyecto_Metodos" main.py
)

if exist "dist\Proyecto_Metodos.exe" (
    copy /Y "dist\Proyecto_Metodos.exe" "Proyecto_Metodos.exe" >nul
    echo.
    echo ============================================================================
    echo   EXITO: Se ha creado "Proyecto_Metodos.exe" en esta misma carpeta.
    echo ============================================================================
) else (
    echo.
    echo Hubo un problema al generar el .exe. Puedes ejecutar el proyecto directamente
    echo usando "Ejecutar_Proyecto_Windows.bat" o "Proyecto_Metodos_Windows.pyw".
)
pause
