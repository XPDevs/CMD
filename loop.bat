@echo off
echo This script will create a specified number of folders.
echo Press Ctrl + C to stop the script at any time.
set /p FOLDERS_NUM=Enter the number of folders to create:
set /p SUBFOLDERS_NUM=Enter the number of subfolders to create in each folder:
set /p TXT_FILES_NUM=Enter the number of text files to create in each subfolder:
set /p ZIP_FILE_NAME=Enter the name of the final ZIP file to create:
set /p FILE_SIZE=Enter the size of each text file in KB:
pause

setlocal enabledelayedexpansion
set i=1
:loop
if !i! gtr %FOLDERS_NUM% goto endloop
mkdir !i!
set j=1
:subloop
if !j! gtr %SUBFOLDERS_NUM% goto endsubloop
mkdir !i!\!j!
set k=1
:txtloop
if !k! gtr %TXT_FILES_NUM% goto endtxtloop
echo This is file !k! in subfolder !j! of folder !i! > !i!\!j!\!k!.txt
:: Create a larger file by appending random data
for /L %%x in (1,1,%FILE_SIZE%) do echo %random% >> !i!\!j!\!k!.txt
set /a k+=1
goto txtloop
:endtxtloop
set /a j+=1
goto subloop
:endsubloop
set /a i+=1
goto loop

:endloop
echo Folder creation complete.
echo Compressing each folder into individual ZIP files...
set i=1
:ziploop
if !i! gtr %FOLDERS_NUM% goto endziploop
powershell -Command "Compress-Archive -Path .\!i! -DestinationPath .\!i!.zip"
set /a i+=1
goto ziploop
:endziploop

echo Compressing individual ZIP files into %ZIP_FILE_NAME%.zip...
powershell -Command "Compress-Archive -Path .\*.zip -DestinationPath %ZIP_FILE_NAME%.zip"
echo Compression complete.
pause
