@echo off
echo ========================================
echo Building dyag v0.2.0-rc.1 package
echo ========================================
echo.

call conda activate conda_ai

echo [1/3] Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist src\dyag.egg-info rmdir /s /q src\dyag.egg-info

echo [2/3] Building package with Poetry...
poetry build

echo.
echo [3/3] Package build complete!
echo.
echo Generated files:
dir /b dist\*

echo.
echo ========================================
echo Build complete! Package ready for distribution.
echo ========================================
pause
