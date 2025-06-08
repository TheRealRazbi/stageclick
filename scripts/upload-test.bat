@echo off
cd /d %~dp0..
echo Uploading to TestPyPI...
python -m twine upload --repository testpypi dist\*
pause