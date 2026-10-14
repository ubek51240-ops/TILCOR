@echo off
title TILCOR PRODUCTION (Port 5050)
chcp 65001 >nul
echo ===================================================================
echo   TILCOR — O‘zbek–ingliz parallel korpusi (Production: Port 5050)
echo   PhD Himoyasi Uchun Ilmiy Parallel Korpus Platformasi
echo ===================================================================
echo.
echo Server ishga tushirilmoqda...
echo Xavfsizlik: Tizim yopiq va autentifikatsiya orqali himoyalangan.
echo Admin paroli: secrets\admin.password faylida yoki TILCOR_ADMIN_PASSWORD muhit o'zgaruvchisida.
echo.
python server.py --port 5050 --env production
pause
