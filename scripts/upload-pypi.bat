@echo off
cd /d %~dp0..
echo Uploading to PyPI...
python -m twine upload --repository pypi dist\*
pause
