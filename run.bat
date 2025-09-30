@echo off
echo Instalando dependencias...
pip install -r requirements.txt

echo.
echo Creando base de datos...
python app.py

pause
