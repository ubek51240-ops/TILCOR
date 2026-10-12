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
echo Kirish ma'lumotlari:
echo   - Tadqiqotchi (Admin):   admin    / tilcor_phd_admin_2026
echo   - Ilmiy rahbar (Reviewer): reviewer / tilcor_supervisor_2026
echo.
python server.py --port 5050 --env production
pause
