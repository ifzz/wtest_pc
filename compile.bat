@echo off
rmdir /s /q .\dist\
rmdir /s /q .\build\
pyinstaller --onefile --icon=console.ico interface.py
xcopy console.ico .\dist\
xcopy README.md .\dist\
pause
@echo on