@echo off
title https://xpdevs.github.io/CMD/C:/WINDOWS/System32/cmd.exe
echo Microsoft Windows [Version 10.0.19045.3086]
echo (c) Microsoft Corporation. All rights reserved.
echo.

:CMD
set /p "COM=%cd%> "
if "%COM%" == "exit" goto :SEC
%COM%
goto :CMD

:SEC
echo You cannot exit the command prompt.
goto :CMD