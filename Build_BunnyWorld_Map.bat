@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" (
 py -3 tools\build_map.py
) else (
 py -3 tools\build_map.py --godot "%~1"
)
set "bunny_build_result=%errorlevel%"
if not "%bunny_build_result%"=="0" echo Map build failed. Read the error above. For changed geography, supply the Godot executable path as the first argument.
pause
exit /b %bunny_build_result%
