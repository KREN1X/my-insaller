```bat
@echo off

:: Прямая ссылка на установочный файл
SET "URL=https://raw.githubusercontent.com/KREN1X/my-insaller/main/kaspersky4win202121.21.7.384en_46728.exe"
SET "FILENAME=kaspersky4win202121.21.7.384en_46728.exe"

:: Папка для временного хранения файла
SET "TEMPDIR=%TEMP%\KasperskyInstall"
SET "FILEPATH=%TEMPDIR%\%FILENAME%"

:: Создание временной папки
mkdir "%TEMPDIR%"

:: Скачивание файла с помощью PowerShell
powershell -Command "Invoke-WebRequest -Uri '%URL%' -OutFile '%FILEPATH%'"

:: Запуск установщика в тихом режиме
start /B "" "%FILEPATH%" /silent
```