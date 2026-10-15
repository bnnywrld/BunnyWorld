@echo off
setlocal
cd /d "%~dp0"
if "%~1"=="" goto instructions
if not exist "%~1" goto instructions
echo Launching BunnyWorld and recording Debug_Log.txt.
echo Close the game after reproducing the issue, then send that file.
"%~1" --path "%~dp0." --debug --verbose --log-file "%~dp0Debug_Log.txt"
echo.
echo Log saved beside project.godot as Debug_Log.txt.
pause
exit /b
:instructions
echo Drag your Godot 4.5.1 executable onto Capture_Debug_Log.bat.
echo This runs the game and records the full engine log in Debug_Log.txt.
pause
exit /b 1
