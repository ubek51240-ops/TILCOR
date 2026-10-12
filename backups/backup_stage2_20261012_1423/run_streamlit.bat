@echo off
chcp 65001 > nul
echo ===================================================================
echo   UZ-EN COLLOCATION CORPUS (ParallelColloc) - Streamlit MVP
echo   PhD Tadqiqoti uchun Python + Streamlit + SQLite Platformasi
echo ===================================================================
echo.

python -c "import streamlit" 2>nul
if %errorlevel% neq 0 (
    echo Streamlit yoki Pandas kutubxonalari topilmadi. O'rnatilmoqda...
    pip install streamlit pandas
)

echo.
echo SQLite ma'lumotlar bazasi tekshirilmoqda...
if not exist "data\corpus.db" (
    echo data\corpus.db yaratilmoqda...
    python -c "import export_to_sqlite"
)

echo.
echo Streamlit ilovasi ishga tushirilmoqda...
streamlit run app_streamlit.py

pause
