@echo off
echo Uploading to PyPI...
python -m twine upload --repository pypi dist\*
pause
