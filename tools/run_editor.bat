@echo off
chcp 65001 > nul
echo ======================================================================
echo    TRANSPORTE AUSTRAL - LANZADOR DEL SCS MAP EDITOR (CHILE MAP)
echo ======================================================================
echo.

set "ETS2_EXE="

:: Posibles rutas de instalación de Euro Truck Simulator 2 en Steam o discos locales
if exist "C:\Program Files (x86)\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe" (
    set "ETS2_EXE=C:\Program Files (x86)\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
) else if exist "D:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe" (
    set "ETS2_EXE=D:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
) else if exist "E:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe" (
    set "ETS2_EXE=E:\SteamLibrary\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
)

if "%ETS2_EXE%"=="" (
    echo [AVISO] No se detectó automáticamente el ejecutable eurotrucks2.exe.
    echo Por favor ingresa la ruta completa a eurotrucks2.exe o edita este archivo bat.
    echo Ejemplo: "C:\Program Files (x86)\Steam\steamapps\common\Euro Truck Simulator 2\bin\win_x64\eurotrucks2.exe"
    pause
    exit /b 1
)

echo Ejecutable detectado: %ETS2_EXE%
echo.
echo REQUISITOS PREVIOS:
echo En 'Documentos\Euro Truck Simulator 2\config.cfg' debes tener configurado:
echo   uset g_developer "1"
echo   uset g_console "1"
echo.
echo Iniciando SCS Map Editor con el mapa 'chile'...
echo Comando: "%ETS2_EXE%" -edit chile -force_mods
echo.

start "" "%ETS2_EXE%" -edit chile -force_mods

echo El editor se está abriendo. Puedes guardar con el comando 'save chile' en la consola del editor.
pause
