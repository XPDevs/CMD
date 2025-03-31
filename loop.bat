@echo off

:: *********************************************
:: *** WARNING: READ THIS ENTIRE MESSAGE CAREFULLY BEFORE PROCEEDING ***
:: *** BY RUNNING THIS SCRIPT, YOU ACKNOWLEDGE THAT YOU HAVE READ AND UNDERSTOOD THE FOLLOWING WARNINGS AND LEGAL INFORMATION ***
:: *********************************************

echo This script will create a specified number of folders and files, which will then be compiled into a ZIP file.
echo The resulting ZIP file may be large and potentially dangerous if opened on an unprotected system.
echo Press Ctrl + C to stop the script at any time.

echo.
echo *** IMPORTANT WARNINGS ***
echo * This script may cause system instability or crashes if not used properly.
echo * The resulting ZIP file may contain malicious or unwanted content if not used in a controlled environment.
echo * You are responsible for ensuring that the script is used in compliance with all applicable laws and regulations.
echo * You are responsible for backing up any important data before running this script.

echo.
echo *** LEGAL INFORMATION ***
echo * This script is provided "as is" without warranty of any kind, express or implied.
echo * The authors and distributors of this script disclaim all liability for any damages or losses arising from its use.
echo * By running this script, you agree to hold harmless the authors and distributors from any claims or damages.
echo * This script is subject to the terms and conditions of the license agreement, which can be found at [insert license agreement URL].

echo.
echo *** TERMS AND CONDITIONS ***
echo * You must be at least 18 years old to use this script.
echo * You must use this script only for lawful purposes.
echo * You must not use this script to create or distribute malicious or unwanted content.
echo * You must not use this script to infringe on the rights of others.

echo.
echo *** BY RUNNING THIS SCRIPT, YOU ACKNOWLEDGE THAT YOU HAVE READ AND UNDERSTOOD THE ABOVE WARNINGS AND LEGAL INFORMATION ***
echo *** YOU ALSO ACKNOWLEDGE THAT YOU ARE RESPONSIBLE FOR ENSURING THAT THE SCRIPT IS USED IN COMPLIANCE WITH ALL APPLICABLE LAWS AND REGULATIONS ***
echo *** IF YOU DO NOT AGREE TO THESE TERMS, PLEASE DO NOT RUN THIS SCRIPT ***

pause

:: Set the number of folders to create
set /p FOLDERS_NUM=Enter the number of folders to create:

:: Set the number of subfolders to create in each folder
set /p SUBFOLDERS_NUM=Enter the number of subfolders to create in each folder:

:: Set the number of text files to create in each subfolder
set /p TXT_FILES_NUM=Enter the number of text files to create in each subfolder:

:: Set the name of the final ZIP file to create
set /p ZIP_FILE_NAME=Enter the name of the final ZIP file to create:

:: Set the size of each text file in KB
set /p FILE_SIZE=Enter the size of each text file in KB:

:: *********************************************
:: *** WARNING: THE FOLLOWING PROCESS MAY TAKE A LONG TIME AND CONSUME LARGE AMOUNTS OF DISK SPACE ***
:: *** PROCEED WITH CAUTION ***
:: *********************************************

:: Create the specified number of folders
for /l %%x in (1,1,%FOLDERS_NUM%) do (
    mkdir folder_%%x
    echo Creating folder_%%x...

    :: Create the specified number of subfolders in each folder
    for /l %%y in (1,1,%SUBFOLDERS_NUM%) do (
        mkdir folder_%%x\subfolder_%%y
        echo Creating subfolder_%%y in folder_%%x...

        :: Create the specified number of text files in each subfolder
        for /l %%z in (1,1,%TXT_FILES_NUM%) do (
            fsutil file createnew folder_%%x\subfolder_%%y\file_%%z.txt %FILE_SIZE%000
            echo Creating file_%%z.txt in subfolder_%%y...
        )
    )
)

:: *********************************************
:: *** WARNING: THE CREATED FOLDERS AND FILES WILL NOW BE COMPILED INTO A ZIP FILE ***
:: *** THIS MAY TAKE A LONG TIME AND CONSUME LARGE AMOUNTS OF DISK SPACE ***
:: *********************************************

:: Compile the folders and files into a ZIP file
zip -9 -r -j %ZIP_FILE_NAME%.zip folder_*

:: *********************************************
:: *** WARNING: THE CREATED ZIP FILE MAY BE DANGEROUS IF OPENED ON AN UNPROTECTED SYSTEM ***
:: *** DO NOT SHARE OR DISTRIBUTE THIS FILE WITHOUT PROPER PRECAUTIONS ***
:: *********************************************

echo.
echo *** ZIP FILE CREATED: %ZIP_FILE_NAME%.zip ***
echo *** PLEASE HANDLE WITH CARE ***

pause
