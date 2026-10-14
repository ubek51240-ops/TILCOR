@echo off
title TILCOR STAGING (Port 5055)
chcp 65001 >nul
echo ===================================================================
echo   TILCOR STAGING MUHITI (Port 5055)
echo   Rivojlantirish va sinov uchun ishchi nusxa
echo ===================================================================
echo.
echo Python server staging rejimida ishga tushirilmoqda...
echo Admin paroli: secrets\admin.password faylida yoki TILCOR_ADMIN_PASSWORD muhit o'zgaruvchisida.
echo.
cd staging
python server.py --port 5055 --env staging
pause
