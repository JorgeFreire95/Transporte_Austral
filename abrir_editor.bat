@echo off
title SCS Map Editor - Transporte Austral Chile
echo ======================================================================
echo    TRANSPORTE AUSTRAL - LANZADOR DEL SCS MAP EDITOR (CHILE)
echo ======================================================================
echo.

set "ETS2_EXE=D:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"

if not exist "%ETS2_EXE%" (
    if exist "C:\Program Files (x86)\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe" (
        set "ETS2_EXE=C:\Program Files (x86)\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
    )
)

if not exist "%ETS2_EXE%" (
    echo [ERROR] No se encontro el archivo eurotrucks2.exe.
    echo Por favor verifica la ruta de instalacion de Euro Truck Simulator 2.
    pause
    exit /b 1
)

echo Ejecutable encontrado en:
echo %ETS2_EXE%
echo.
echo Iniciando el SCS Map Editor con el mapa 'chile'...
echo.

start "" "%ETS2_EXE%" -edit chile -force_mods

echo ======================================================================
echo El Map Editor se esta iniciando.
echo Cuando estes dentro del editor:
echo  1. Abre la consola con la tecla ~ (o la tecla al lado del 1).
echo  2. Escribe: c_goto -39700 100 -11000  (para ir a Santiago)
echo ======================================================================
echo.
pause
