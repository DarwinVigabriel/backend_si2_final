@echo off
echo ==========================================
echo  CONFIGURACION SISTEMA COOPERATIVA AGRICOLA
echo ==========================================
echo.

echo 1. Verificando Python...
python --version
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado
    pause
    exit /b 1
)

echo 2. Creando entorno virtual...
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: No se pudo crear entorno virtual
    pause
    exit /b 1
)

echo 3. Activando entorno virtual...
call venv\Scripts\activate

echo 4. Actualizando pip...
python -m pip install --upgrade pip

echo 5. Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo 6. Verificando instalacion...
pip check

echo 7. Copiando archivo de configuracion...
if not exist .env (
    copy .env.example .env
    echo IMPORTANTE: Edita el archivo .env con tus credenciales
)

echo 8. Verificando configuracion Django...
python manage.py check --deploy
if %errorlevel% neq 0 (
    echo ADVERTENCIA: Hay problemas de configuracion, revisar settings.py
)

echo.
echo ==========================================
echo  INSTALACION COMPLETADA
echo ==========================================
echo.
echo Siguiente pasos:
echo 1. Editar .env con tus credenciales de base de datos
echo 2. Ejecutar: python manage.py migrate
echo 3. Ejecutar: python manage.py createsuperuser
echo 4. Ejecutar: python manage.py runserver
echo.
pause