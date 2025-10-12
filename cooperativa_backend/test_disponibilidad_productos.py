#!/usr/bin/env python
"""
Script de prueba para verificar consultas de disponibilidad de productos
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

from cooperativa.apps.chatbot.agente_cooperativa import agente_agricola, inicializar_historial

def probar_consultas_disponibilidad():
    """Prueba diferentes consultas sobre disponibilidad de productos"""

    print("🧪 Probando consultas de disponibilidad de productos...\n")

    # Casos de prueba
    casos_prueba = [
        {
            "mensaje": "¿Tienen semillas de maíz disponibles?",
            "descripcion": "Consulta específica de semillas de maíz"
        },
        {
            "mensaje": "¿Qué pesticidas tienen en stock?",
            "descripcion": "Consulta general de pesticidas"
        },
        {
            "mensaje": "¿Hay fertilizantes orgánicos disponibles?",
            "descripcion": "Consulta de fertilizantes orgánicos"
        },
        {
            "mensaje": "¿Cuánto cuestan las semillas de papa?",
            "descripcion": "Consulta de precios de semillas"
        },
        {
            "mensaje": "¿Tienen herbicidas disponibles?",
            "descripcion": "Consulta de tipo específico de pesticida"
        },
        {
            "mensaje": "¿Qué productos agrícolas ofrecen?",
            "descripcion": "Consulta general de productos"
        }
    ]

    for i, caso in enumerate(casos_prueba, 1):
        print(f"📋 Caso {i}: {caso['descripcion']}")
        print(f"💬 Pregunta: {caso['mensaje']}")

        # Inicializar historial para cada prueba
        historial = inicializar_historial(f"test_{i}")

        # Obtener respuesta del agente
        respuesta = agente_agricola(caso['mensaje'], historial)

        print(f"🤖 Respuesta: {respuesta[:200]}..." if len(respuesta) > 200 else f"🤖 Respuesta: {respuesta}")
        print("-" * 80)

    print("\n✅ Pruebas completadas!")

if __name__ == '__main__':
    probar_consultas_disponibilidad()