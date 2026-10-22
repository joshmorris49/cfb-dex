#!/usr/bin/env bash
# Rebuild index.html from the CSVs in data/. Requires Python 3 with numpy and scipy.
set -euo pipefail
cd "$(dirname "$0")"
python3 build_2026.py
python3 add_colors.py dex_2026.json dex_colored.json data/colors.csv > /dev/null
python3 make_page.py
