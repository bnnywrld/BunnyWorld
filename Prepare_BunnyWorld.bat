@echo off
setlocal
cd /d "%~dp0"
echo Close Godot before preparing an updated BunnyWorld project.
echo.
where py >nul 2>&1
if errorlevel 1 goto use_python
py -3 tools\restore_repository_assets.py
set "bunny_result=%errorlevel%"
goto finished
:use_python
python tools\restore_repository_assets.py
set "bunny_result=%errorlevel%"
:finished
echo.
if not "%bunny_result%"=="0" goto failed
echo Preparation complete. Open the project in Godot and start a fresh campaign.
goto done
:failed
echo Preparation did not finish. Copy the error above and report it.
:done
pause
exit /b %bunny_result%
