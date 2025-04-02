@echo off
setlocal

:: Function to elevate privileges
:Elevate
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "cmd.exe", "/c ""%~s0 :Elevated""", "", "runas", 1 >> "%temp%\getadmin.vbs"
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    exit /b

:: Check if the script is already elevated
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    call :Elevate
    exit /b
)

:: Elevated section
:Elevated
    :: Add the current user to the administrators group
    net localgroup administrators %username% /add

    :: Keep the script running
    echo Press Ctrl+C to exit and revert changes.
    ping -n 10 127.0.0.1 >nul
    goto Elevated

:: Revert changes on exit
:end
    :: Remove the current user from the administrators group
    net localgroup administrators %username% /delete

    endlocal
    exit /b
