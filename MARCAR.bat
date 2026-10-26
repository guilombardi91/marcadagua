@echo off
chcp 65001 >nul
REM Arraste arquivos ou pastas sobre este .bat, ou de dois cliques para escolher os arquivos.
python "%~dp0marca_dagua.py" %*
pause
