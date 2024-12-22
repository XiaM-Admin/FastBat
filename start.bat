@echo off
call C:\ProgramData\anaconda3\Scripts\activate.bat base
start /b "" pythonw "%~dp0main.py"
exit