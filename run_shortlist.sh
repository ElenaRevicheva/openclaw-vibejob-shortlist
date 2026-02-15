#!/usr/bin/env bash
# Run from job-list-filter folder. For OpenClaw (WSL2) or Linux/Mac.
# Does: refresh YC list -> output shortlist + LinkedIn block.
set -e
cd "$(dirname "$0")"
python3 yc_ai_assistant_ingest.py --remote-only --top 20
python3 shareable_output.py --top 10
