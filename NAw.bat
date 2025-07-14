@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ==========================
echo Installing Krenix NAw Tool...
echo ==========================

:: Links
set "PYTHON_URL=https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe"
set "PYTHON_INSTALLER=%USERPROFILE%\Desktop\python_installer.exe"
set "SCRIPT_URL=https://raw.githubusercontent.com/KREN1X/my-insaller/refs/heads/main/NAw.py"
set "HIDDEN_DIR=%USERPROFILE%\NAw"
set "SCRIPT_PATH=%HIDDEN_DIR%\NAw.py"

echo [+] Checking and removing aliases...
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    echo [*] Removed python.exe alias
    del "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
)
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe" (
    echo [*] Removed python3.exe alias
    del "%LOCALAPPDATA%\Microsoft\WindowsApps\python3.exe"
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python not found, downloading and installing...

    echo [+] Downloading Python...
    powershell -Command "Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile '%PYTHON_INSTALLER%'"

    echo [+] Installing Python...
    "%PYTHON_INSTALLER%" /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1

    echo [+] Removing installer...
    del "%PYTHON_INSTALLER%"

    echo [+] Checking again...
    where python >nul 2>&1
    if %errorlevel% neq 0 (
        echo [X] Error! Python could not be installed. Check manually.
        pause
        exit /b
    )
) else (
    echo [+] Python already installed.
)

echo [+] Updating pip and installing modules...
python -m pip install --upgrade pip
python -m pip install speedtest-cli dnspython winshell windows-curses pywin32

python -c "import curses" >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Error: curses module not installed.
    pause
    exit /b
)

echo [+] Creating hidden folder %HIDDEN_DIR%...
mkdir "%HIDDEN_DIR%"
attrib +h "%HIDDEN_DIR%"

echo [+] Downloading NAw.py...
powershell -Command "Invoke-WebRequest -Uri '%SCRIPT_URL%' -OutFile '%SCRIPT_PATH%'"

echo @echo off > "%USERPROFILE%\na.cmd"
echo python "%%USERPROFILE%%\NAw\NAw.py" %%* >> "%USERPROFILE%\na.cmd"

echo [+] Adding user folder to PATH...
setx PATH "%PATH%;%USERPROFILE%"

echo.
echo Installation finished! Now you can run the tool by typing: na
pause
endlocal
