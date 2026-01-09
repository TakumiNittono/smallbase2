#!/bin/bash
# Azure App ServiceのPORT環境変数を使用
if [ -z "$PORT" ]; then
    PORT=8000
fi
gunicorn main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120

