#!/bin/zsh
# Double-click this file in Finder to launch Photo File Copier.
cd "$(dirname "$0")"
/usr/local/bin/python3.11 photo_copier.py 2>/dev/null || \
  /opt/homebrew/bin/python3.11 photo_copier.py
