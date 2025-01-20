@echo off
setlocal enabledelayedexpansion

:: Try to find Python in PATH
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python install_standalone.py
    goto :end
)

:: Try to find Anaconda Python in common locations
set "ANACONDA_PATHS=%USERPROFILE%\anaconda3\python.exe %USERPROFILE%\Anaconda3\python.exe C:\ProgramData\Anaconda3\python.exe %LOCALAPPDATA%\Continuum\anaconda3\python.exe"

for %%p in (%ANACONDA_PATHS%) do (
    if exist "%%p" (
        echo Found Anaconda Python: %%p
        "%%p" install_standalone.py
        goto :end
    )
)

:: Try to find Maya's Python in common locations
set "MAYA_PATHS=C:\Program Files\Autodesk\Maya2024\bin\mayapy.exe C:\Program Files\Autodesk\Maya2023\bin\mayapy.exe C:\Program Files\Autodesk\Maya2022\bin\mayapy.exe"

for %%p in (%MAYA_PATHS%) do (
    if exist "%%p" (
        echo Found Maya Python: %%p
        "%%p" install_standalone.py
        goto :end
    )
)

:: If we get here, no Python was found
echo ERROR: No Python installation found.
echo Please ensure one of the following:
echo 1. Python is installed and added to your PATH
echo    - Download Python from https://www.python.org/downloads/
echo    - During installation, check "Add Python to PATH"
echo.
echo 2. Anaconda is installed in a standard location
echo    - The script will use Anaconda's Python if found
echo.
echo 3. Maya is installed in the default location
echo    - The script will use Maya's Python if found
echo.
echo Press any key to exit...
pause >nul

:end
pause