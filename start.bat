@echo off
if exist "C:\ProgramData\anaconda3\Scripts\activate.bat" (
    call C:\ProgramData\anaconda3\Scripts\activate.bat base
)
start /b "" pythonw "%~dp0main.py"
exit