@echo off
echo This script will create a specified number of folders.
echo Press Ctrl + C to stop the script at any time.
set /p FOLDERS_NUM=Enter the number of folders to create:
pause

setlocal enabledelayedexpansion
set i=1
:loop
if !i! gtr %FOLDERS_NUM% goto endloop
mkdir !i!
set /a i+=1
goto loop

:endloop
echo Folder creation complete.
pause
