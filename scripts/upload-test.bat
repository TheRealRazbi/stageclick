@echo off
setlocal
cd /d %~dp0..
set "ORIGINAL_DIR=%CD%"
echo Uploading to TestPyPI...
python -m twine upload %* --repository testpypi dist\*
cd /d "%ORIGINAL_DIR%"
pause
