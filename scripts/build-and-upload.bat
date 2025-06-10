@echo off
setlocal
set "ORIGINAL_DIR=%CD%"
cd /d %~dp0..
echo "Building and uploading..."
call "scripts/build.bat"
call "scripts/upload-pypi.bat"
cd /d "%ORIGINAL_DIR%"
