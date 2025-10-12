#!/bin/bash

echo "=========================================="
echo "  CONFIGURACIÓN SISTEMA COOPERATIVA AGRÍCOLA"
echo "=========================================="
echo

echo "1. Verificando Python..."
python3 --version
if [ $? -ne 0 ]; then
    echo "ERROR: Python no está instalado"
    exit 1
fi

echo "2. Creando entorno virtual..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudo crear entorno virtual"
    exit 1
fi

echo "3. Activando entorno virtual..."
source venv/bin/activate

echo "4. Actualizando pip..."
python -m pip install --upgrade pip

echo "5. Instalando dependencias..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "ERROR: No se pudieron instalar las dependencias"
    exit 1
fi

echo "6. Verificando instalación..."
pip check

echo "7. Copiando archivo de configuración..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "IMPORTANTE: Edita el archivo .env con tus credenciales"
fi

echo "8. Verificando configuración Django..."
python manage.py check --deploy
if [ $? -ne 0 ]; then
    echo "ADVERTENCIA: Hay problemas de configuración, revisar settings.py"
fi

echo
echo "=========================================="
echo "  INSTALACIÓN COMPLETADA"
echo "=========================================="
echo
echo "Siguientes pasos:"
echo "1. Editar .env con tus credenciales de base de datos"
echo "2. Ejecutar: python manage.py migrate"
echo "3. Ejecutar: python manage.py createsuperuser"
echo "4. Ejecutar: python manage.py runserver"
echo

read -p "Presiona Enter para continuar..."