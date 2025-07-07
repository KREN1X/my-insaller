@echo off
setlocal

echo =============================
echo 🚀 Скачиваем установщик Python...
echo =============================

set PYTHON_URL=https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe
set INSTALLER=%TEMP%\python-installer.exe

powershell -Command "Invoke-WebRequest -Uri %PYTHON_URL% -OutFile '%INSTALLER%'"

echo =============================
echo ⚙️ Устанавливаем Python...
echo =============================

"%INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

echo =============================
echo ⏳ Ждем обновления PATH...
echo =============================

timeout /t 10 >nul

echo =============================
echo ✅ Проверяем версии...
echo =============================

python --version
pip --version

echo =============================
echo 🔥 Готово! Python и pip установлены!
echo Закройте и заново откройте консоль, если pip не определяется сразу.
echo =============================

pause
endlocal