@echo off
cd /d "%~dp0"
where py >nul 2>nul
if %errorlevel%==0 (
    echo Blackthorn Estate V7: http://localhost:8000
    py -3 -m http.server 8000 --bind 127.0.0.1
    goto end
)
where python >nul 2>nul
if %errorlevel%==0 (
    echo Blackthorn Estate V7: http://localhost:8000
    python -m http.server 8000 --bind 127.0.0.1
    goto end
)
echo Python 3 wurde nicht gefunden. Bitte Python 3 installieren.
:end
pause
