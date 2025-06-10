@echo off
set "ORIGINAL_DIR=%CD%"
cd /d %~dp0..
set PYTHONPATH=.
pytest
cd /d "%ORIGINAL_DIR%"
