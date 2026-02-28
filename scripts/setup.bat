@echo off
setlocal
cd /d %~dp0\..

where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\bootstrap.py %*
  exit /b %errorlevel%
)

where python >nul 2>nul
if %errorlevel%==0 (
  python scripts\bootstrap.py %*
  exit /b %errorlevel%
)

echo Python not found. Install Python 3.9+ and re-run.
exit /b 1
