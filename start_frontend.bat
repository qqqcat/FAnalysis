@echo off
echo Installing and running the Financial Analysis Platform frontend...

cd %~dp0web

:: Try to get npm path
for /f "tokens=*" %%i in ('where npm') do set NPM_PATH=%%i

:: If npm is found, use it
if defined NPM_PATH (
    echo Using npm from: %NPM_PATH%
    
    echo Installing dependencies...
    call "%NPM_PATH%" install
    
    echo Starting React development server...
    call "%NPM_PATH%" start
) else (
    echo ERROR: npm command not found in PATH.
    echo Please run 'python setup_frontend.py' first to set up Node.js.
    exit /b 1
)