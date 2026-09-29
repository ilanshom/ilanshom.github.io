#!/bin/sh
cd "$(dirname "$0")" || exit 1
python3 bin/update_news.py
printf '\nPress Enter to close.\n'
read -r answer
