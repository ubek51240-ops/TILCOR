@echo off
chcp 65001 >nul
echo =================================================================
echo   TILCOR v2.0 - GitHub Repozitoriyiga Yuklash (Push)
echo   Manzil: https://github.com/ubek51240-ops/TILCOR
echo =================================================================
echo.

set GIT_EXE="C:\Users\user\AppData\Local\Microsoft\WinGet\Packages\Git.MinGit_Microsoft.Winget.Source_8wekyb3d8bbwe\cmd\git.exe"

echo 1. Git holati tekshirilmoqda...
%GIT_EXE% status

echo.
echo 2. Agar GitHub Personal Access Token (PAT) mavjud bo'lsa,
echo    quyidagicha kiriting yoki Enter bosing:
set /p GITHUB_TOKEN="GitHub Token (bo'sh qoldirish mumkin): "

if "%GITHUB_TOKEN%"=="" (
    echo.
    echo Standart git push bajarilmoqda...
    %GIT_EXE% push -u origin main
) else (
    echo.
    echo Token orqali push qilinmoqda...
    %GIT_EXE% push https://ubek51240-ops:%GITHUB_TOKEN%@github.com/ubek51240-ops/TILCOR.git main
)

echo.
echo Amal yakunlandi.
pause
