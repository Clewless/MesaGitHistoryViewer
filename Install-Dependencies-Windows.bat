@echo off
REM Windows dependency installer for Mesa Git History Viewer
echo Installing dependencies...
python -m pip install --upgrade pip
if %errorlevel% neq 0 goto error
python -m pip install -r requirements-dev.txt
if %errorlevel% neq 0 goto error

echo.
echo Installation complete!
pause
exit /b 0

:error
echo.
echo An error occurred during installation.
pause
exit /b 1