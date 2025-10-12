#!/usr/bin/env python
"""
Script para verificar que todos los endpoints principales estén funcionando
"""
import os
import sys
import django
import requests
import json
from datetime import datetime

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

from django.test import Client
from django.urls import reverse

def probar_endpoints_api():
    """Prueba los endpoints principales de la API usando Django test client"""

    print("🔍 Probando endpoints principales de la API...\n")

    client = Client()

    # Lista de endpoints a probar
    endpoints_a_probar = [
        # Endpoints de autenticación
        ('api/auth/csrf/', 'GET', 'CSRF Token'),
        ('api/auth/status/', 'GET', 'Estado de sesión'),

        # Endpoints de roles
        ('api/roles/', 'GET', 'Lista de roles'),

        # Endpoints de usuarios
        ('api/usuarios/', 'GET', 'Lista de usuarios'),

        # Endpoints de comunidades
        ('api/comunidades/', 'GET', 'Lista de comunidades'),

        # Endpoints de socios
        ('api/socios/', 'GET', 'Lista de socios'),

        # Endpoints de parcelas
        ('api/parcelas/', 'GET', 'Lista de parcelas'),

        # Endpoints de cultivos
        ('api/cultivos/', 'GET', 'Lista de cultivos'),

        # CU4: Gestión avanzada
        ('api/ciclo-cultivos/', 'GET', 'Ciclos de cultivo'),
        ('api/cosechas/', 'GET', 'Cosechas'),
        ('api/tratamientos/', 'GET', 'Tratamientos'),
        ('api/analisis-suelo/', 'GET', 'Análisis de suelo'),
        ('api/transferencias-parcela/', 'GET', 'Transferencias de parcela'),

        # CU7: Semillas
        ('api/semillas/', 'GET', 'Semillas'),

        # CU8: Insumos
        ('api/pesticidas/', 'GET', 'Pesticidas'),
        ('api/fertilizantes/', 'GET', 'Fertilizantes'),

        # Bitácora
        ('api/bitacora/', 'GET', 'Bitácora de auditoría'),
    ]

    resultados = []

    for endpoint, method, descripcion in endpoints_a_probar:
        try:
            if method == 'GET':
                response = client.get(f'/{endpoint}')
            elif method == 'POST':
                response = client.post(f'/{endpoint}')
            else:
                response = client.get(f'/{endpoint}')

            status_ok = 200 <= response.status_code < 300
            resultados.append({
                'endpoint': endpoint,
                'descripcion': descripcion,
                'status_code': response.status_code,
                'status_ok': status_ok,
                'error': None if status_ok else f"Status {response.status_code}"
            })

            print(f"{'✅' if status_ok else '❌'} {endpoint} - {descripcion}: {response.status_code}")

        except Exception as e:
            resultados.append({
                'endpoint': endpoint,
                'descripcion': descripcion,
                'status_code': None,
                'status_ok': False,
                'error': str(e)
            })
            print(f"❌ {endpoint} - {descripcion}: ERROR - {str(e)}")

    return resultados

def probar_endpoints_chatbot():
    """Prueba los endpoints del chatbot"""

    print("\n🤖 Probando endpoints del chatbot...\n")

    client = Client()

    # Endpoints del chatbot
    chatbot_endpoints = [
        ('chatbot/api/', 'POST', 'API del chatbot'),
        ('chatbot/historial/test_user/', 'GET', 'Historial del chatbot'),
    ]

    resultados = []

    for endpoint, method, descripcion in chatbot_endpoints:
        try:
            if method == 'GET':
                response = client.get(f'/{endpoint}')
            elif method == 'POST':
                # Para el endpoint de chatbot, enviamos un mensaje de prueba
                data = {
                    'message': 'Hola, soy un usuario de prueba',
                    'cliente_id': 'test_user'
                }
                response = client.post(f'/{endpoint}', data=json.dumps(data),
                                     content_type='application/json')
            else:
                response = client.get(f'/{endpoint}')

            status_ok = 200 <= response.status_code < 300
            resultados.append({
                'endpoint': endpoint,
                'descripcion': descripcion,
                'status_code': response.status_code,
                'status_ok': status_ok,
                'error': None if status_ok else f"Status {response.status_code}"
            })

            print(f"{'✅' if status_ok else '❌'} {endpoint} - {descripcion}: {response.status_code}")

            # Para el chatbot, verificar que la respuesta tenga contenido
            if endpoint == 'chatbot/api/' and status_ok:
                try:
                    response_data = response.json()
                    if 'response' in response_data and response_data['response']:
                        print(f"   📝 Respuesta del chatbot: {response_data['response'][:100]}...")
                    else:
                        print("   ⚠️  Respuesta del chatbot incompleta")
                except:
                    print("   ⚠️  No se pudo parsear respuesta JSON")

        except Exception as e:
            resultados.append({
                'endpoint': endpoint,
                'descripcion': descripcion,
                'status_code': None,
                'status_ok': False,
                'error': str(e)
            })
            print(f"❌ {endpoint} - {descripcion}: ERROR - {str(e)}")

    return resultados

def verificar_modelos_con_datos():
    """Verifica que los modelos principales tengan datos"""

    print("\n📊 Verificando datos en modelos principales...\n")

    from cooperativa.models import (
        Rol, Usuario, Comunidad, Socio, Parcela, Cultivo,
        Semilla, Pesticida, Fertilizante, CicloCultivo
    )

    modelos_a_verificar = [
        (Rol, 'Roles'),
        (Usuario, 'Usuarios'),
        (Comunidad, 'Comunidades'),
        (Socio, 'Socios'),
        (Parcela, 'Parcelas'),
        (Cultivo, 'Cultivos'),
        (Semilla, 'Semillas'),
        (Pesticida, 'Pesticidas'),
        (Fertilizante, 'Fertilizantes'),
        (CicloCultivo, 'Ciclos de Cultivo'),
    ]

    resultados = []

    for modelo, nombre in modelos_a_verificar:
        try:
            count = modelo.objects.count()
            tiene_datos = count > 0
            resultados.append({
                'modelo': nombre,
                'count': count,
                'tiene_datos': tiene_datos
            })

            print(f"{'✅' if tiene_datos else '⚠️'} {nombre}: {count} registros")

        except Exception as e:
            resultados.append({
                'modelo': nombre,
                'count': 0,
                'tiene_datos': False,
                'error': str(e)
            })
            print(f"❌ {nombre}: ERROR - {str(e)}")

    return resultados

def generar_reporte_final(api_results, chatbot_results, modelos_results):
    """Genera un reporte final del estado de los endpoints"""

    print("\n" + "="*80)
    print("📋 REPORTE FINAL - ESTADO DE ENDPOINTS")
    print("="*80)

    # Estadísticas generales
    total_api = len(api_results)
    api_ok = sum(1 for r in api_results if r['status_ok'])
    total_chatbot = len(chatbot_results)
    chatbot_ok = sum(1 for r in chatbot_results if r['status_ok'])
    total_modelos = len(modelos_results)
    modelos_con_datos = sum(1 for r in modelos_results if r['tiene_datos'])

    print(f"\n📊 ESTADÍSTICAS GENERALES:")
    print(f"   API Endpoints: {api_ok}/{total_api} funcionando")
    print(f"   Chatbot Endpoints: {chatbot_ok}/{total_chatbot} funcionando")
    print(f"   Modelos con datos: {modelos_con_datos}/{total_modelos}")

    # Estado general
    todos_ok = (api_ok == total_api and chatbot_ok == total_chatbot and modelos_con_datos > 0)

    print(f"\n🎯 ESTADO GENERAL: {'✅ TODOS LOS ENDPOINTS LISTOS' if todos_ok else '⚠️ ALGUNOS ENDPOINTS CON PROBLEMAS'}")

    if not todos_ok:
        print(f"\n❌ ENDPOINTS CON PROBLEMAS:")

        # API endpoints con problemas
        api_problems = [r for r in api_results if not r['status_ok']]
        if api_problems:
            print(f"   API ({len(api_problems)} problemas):")
            for r in api_problems:
                print(f"     - {r['endpoint']}: {r['error']}")

        # Chatbot endpoints con problemas
        chatbot_problems = [r for r in chatbot_results if not r['status_ok']]
        if chatbot_problems:
            print(f"   Chatbot ({len(chatbot_problems)} problemas):")
            for r in chatbot_problems:
                print(f"     - {r['endpoint']}: {r['error']}")

        # Modelos sin datos
        modelos_sin_datos = [r for r in modelos_results if not r['tiene_datos']]
        if modelos_sin_datos:
            print(f"   Modelos sin datos ({len(modelos_sin_datos)}):")
            for r in modelos_sin_datos:
                print(f"     - {r['modelo']}: {r['count']} registros")

    print(f"\n📅 Fecha de verificación: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)

    return todos_ok

def main():
    """Función principal"""

    print("🚀 VERIFICACIÓN COMPLETA DE ENDPOINTS")
    print("Proyecto: Cooperativa Agrícola - Backend Django")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)

    # Probar endpoints de API
    api_results = probar_endpoints_api()

    # Probar endpoints de chatbot
    chatbot_results = probar_endpoints_chatbot()

    # Verificar modelos con datos
    modelos_results = verificar_modelos_con_datos()

    # Generar reporte final
    todos_listos = generar_reporte_final(api_results, chatbot_results, modelos_results)

    if todos_listos:
        print("\n🎉 ¡FELICITACIONES! Todos los endpoints están listos para consumo.")
        print("El backend está completamente funcional y puede recibir requests.")
    else:
        print("\n⚠️  Algunos endpoints necesitan atención antes del despliegue.")
        print("Revisa los errores arriba y corrige los problemas identificados.")

    return todos_listos

if __name__ == '__main__':
    main()