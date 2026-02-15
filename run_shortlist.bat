@echo off
REM Run from job-list-filter folder. For Windows (if OpenClaw or agent runs natively).
cd /d "%~dp0"
python yc_ai_assistant_ingest.py --remote-only --top 20
python shareable_output.py --top 10
