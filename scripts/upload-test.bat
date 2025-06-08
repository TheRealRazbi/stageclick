@echo off
cd /d %~dp0..
echo Uploading to TestPyPI...
python -m twine upload --repository test_stageclick dist\*
pause