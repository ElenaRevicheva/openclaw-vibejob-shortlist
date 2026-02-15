@echo off
cd /d "%~dp0"
echo.
echo  Job list filter - Remote or Panama only
echo  ---------------------------------------
python filter_jobs.py
echo.
pause
