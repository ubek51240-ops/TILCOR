@echo off
title TILCOR STAGING (Port 5055)
chcp 65001 >nul
echo ===================================================================
echo   TILCOR STAGING MUHITI (Port 5055)
echo   Rivojlantirish va sinov uchun ishchi nusxa
echo ===================================================================
echo.
echo Python server staging rejimida ishga tushirilmoqda...
echo Kirish ma'lumotlari:
echo   - Admin (Tadqiqotchi): admin / tilcor_phd_admin_2026
echo   - Reviewer (Ilmiy rahbar): reviewer / tilcor_supervisor_2026
echo.
cd staging
python server.py --port 5055 --env staging
pause
