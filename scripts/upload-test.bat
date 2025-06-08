@echo off
echo Uploading to TestPyPI...
python -m twine upload --repository testpypi dist\*
pause