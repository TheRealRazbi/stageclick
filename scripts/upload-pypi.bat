@echo off
setlocal
set "ORIGINAL_DIR=%CD%"
cd /d %~dp0..
echo Uploading to PyPI...
python -m twine upload --repository pypi dist\*
cd /d "%ORIGINAL_DIR%"
pause
