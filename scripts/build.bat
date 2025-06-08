@echo off
cd /d %~dp0..
echo Cleaning previous builds...
rmdir /s /q dist 2>nul
rmdir /s /q build 2>nul
rmdir /s /q *.egg-info 2>nul

echo Building package...
python -m build
