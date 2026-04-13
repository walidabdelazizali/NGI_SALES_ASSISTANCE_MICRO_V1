@echo off
title NGI Telegram Bot

cd /d C:\micro-insurance-kb-v1\NGI_SALES_ASSISTANCE_MICRO_V1

call .\NGI-ROBOT\.venv\Scripts\activate.bat

set "TELEGRAM_BOT_TOKEN=8298828573:AAFa_CH2KaBxEWj82YxtNJef9LBPDMEBJZE"

.\NGI-ROBOT\.venv\Scripts\python.exe scripts\telegram_bot.py

pause