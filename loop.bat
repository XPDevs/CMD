@echo off

:: *********************************************
:: *** WARNING: THIS SCRIPT IS EXTREMELY MALICIOUS AND CAN CAUSE IRREPARABLE HARM TO SYSTEMS AND DATA ***
:: *** IT IS ILLEGAL TO CREATE, OWN, OR DISTRIBUTE THIS SCRIPT ***
:: *** PROCEED WITH EXTREME CAUTION AND AT YOUR OWN RISK ***
:: *********************************************

echo This script will create a massive ZIP file with a complex web of nested folders and files.
echo The resulting ZIP file will be extremely large and can potentially destroy any computer system.
echo Press Ctrl + C to stop the script at any time, but be warned that this may not be enough to prevent damage.

echo.
echo *** ILLEGALITY WARNING ***
echo * Creating, owning, or distributing this script is a serious crime and can result in severe penalties, including fines and imprisonment.
echo * You are putting yourself and others at risk of significant harm by proceeding with this script.
echo * You have been warned.

echo.
echo *** TERMS AND CONDITIONS ***
echo * By running this script, you acknowledge that you are aware of the extreme risks and consequences involved.
echo * You acknowledge that you are responsible for any damage caused by this script, and that you will hold harmless the authors and distributors.
echo * You agree to use this script only for educational purposes, and not for malicious or destructive purposes.

echo.
echo *** BY RUNNING THIS SCRIPT, YOU ACKNOWLEDGE THAT YOU HAVE READ AND UNDERSTOOD THE ABOVE WARNINGS AND TERMS ***
echo *** YOU ALSO ACKNOWLEDGE THAT YOU ARE AWARE OF THE EXTREME RISKS AND CONSEQUENCES INVOLVED ***
echo *** IF YOU DO NOT AGREE TO THESE TERMS, PLEASE DO NOT RUN THIS SCRIPT ***
echo *** YOU HAVE BEEN WARNED ***

pause

:: Set the number of folders to create
set /p FOLDERS_NUM=Enter the number of folders to create (WARNING: HIGH NUMBERS CAN CAUSE SYSTEM CRASHES):

:: Set the number of subfolders to create in each folder
set /p SUBFOLDERS_NUM=Enter the number of subfolders to create in each folder (WARNING: HIGH NUMBERS CAN CAUSE SYSTEM CRASHES):

:: Set the number of iterations for the nested folder structure
set /p ITERATIONS=Enter the number of iterations for the nested folder structure (WARNING: HIGH NUMBERS CAN CAUSE SYSTEM CRASHES):

:: Create the specified number of folders
for /l %%x in (1,1,%FOLDERS_NUM%) do (
    mkdir folder_%%x
    echo Creating folder_%%x...

    :: Create the specified number of subfolders in each folder
    for /l %%y in (1,1,%SUBFOLDERS_NUM%) do (
        mkdir folder_%%x\subfolder_%%y
        echo Creating subfolder_%%y in folder_%%x...

        :: Create a nested folder structure with the specified number of iterations
        for /l %%i in (1,1,%ITERATIONS%) do (
            mkdir folder_%%x\subfolder_%%y\nested_folder_%%i
            echo Creating nested_folder_%%i in subfolder_%%y...

            :: Zip the current folder and copy it to the parent folder
            zip -9 -r -j folder_%%x\subfolder_%%y\nested_folder_%%i.zip folder_%%x\subfolder_%%y\nested_folder_%%i
            echo Zipping and copying nested_folder_%%i...

            :: Copy the zipped folder to the parent folder
            copy folder_%%x\subfolder_%%y\nested_folder_%%i.zip folder_%%x\subfolder_%%y
            echo Copying zipped folder to parent folder...

            :: Repeat the process for the specified number of iterations
            for /l %%j in (1,1,%ITERATIONS%) do (
                mkdir folder_%%x\subfolder_%%y\nested_folder_%%i\nested_folder_%%j
                echo Creating nested_folder_%%j in nested_folder_%%i...

                :: Zip the current folder and copy it to the parent folder
                zip -9 -r -j folder_%%x\subfolder_%%y\nested_folder_%%i\nested_folder_%%j.zip folder_%%x\subfolder_%%y\nested_folder_%%i\nested_folder_%%j
                echo Zipping and copying nested_folder_%%j...

                :: Copy the zipped folder to the parent folder
                copy folder_%%x\subfolder_%%y\nested_folder_%%i\nested_folder_%%j.zip folder_%%x\subfolder_%%y\nested_folder_%%i
                echo Copying zipped folder to parent folder...
            )
        )
    )
)

:: Zip all the folders into one massive file
zip -9 -r -j massive_file.zip folder_*

:: *********************************************
:: *** WARNING: THE CREATED ZIP FILE IS EXTREMELY MALICIOUS AND CAN CAUSE IRREPARABLE HARM TO SYSTEMS AND DATA ***
:: *** DO NOT SHARE OR DISTRIBUTE THIS FILE UNDER ANY CIRCUMSTANCES ***
:: *********************************************

echo.
echo *** ZIP FILE CREATED: massive_file.zip ***
echo *** PLEASE HANDLE WITH EXTREME CAUTION ***
echo *** YOU HAVE BEEN WARNED ***

pause
