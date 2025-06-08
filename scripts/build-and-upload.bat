@echo off
cd /d %~dp0..
echo "Building and uploading..."
call "scripts/build.bat"
call "scripts/upload-pypi.bat"