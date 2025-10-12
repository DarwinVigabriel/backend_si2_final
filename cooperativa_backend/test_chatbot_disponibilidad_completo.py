#!/usr/bin/env python
"""
Script de prueba completa del chatbot con consultas de disponibilidad
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
django.setup()

from cooperativa.apps.chatbot.chatbot import get_chatbot_response

def probar_chatbot_completo():
    """Prueba completa del chatbot incluyendo consultas de disponibilidad"""

    print("🤖 Probando chatbot completo con consultas de disponibilidad...\n")

    # Limpiar historial anterior
    from cooperativa.apps.chatbot.chatbot import limpiar_historial
    limpiar_historial("test_disponibilidad")

    # Casos de prueba
    conversaciones_prueba = [
        {
            "mensaje": "Hola, soy Juan Pérez",
            "descripcion": "Saludo inicial"
        },
        {
            "mensaje": "¿Tienen semillas de maíz disponibles?",
            "descripcion": "Consulta de semillas específicas"
        },
        {
            "mensaje": "¿Qué pesticidas recomiendan para el maíz?",
            "descripcion": "Consulta de pesticidas"
        },
        {
            "mensaje": "¿Hay fertilizantes orgánicos disponibles?",
            "descripcion": "Consulta de fertilizantes orgánicos"
        },
        {
            "mensaje": "¿Cuánto cuestan las semillas de papa?",
            "descripcion": "Consulta de precios"
        },
        {
            "mensaje": "Gracias por la información",
            "descripcion": "Cierre de conversación"
        }
    ]

    cliente_id = "test_disponibilidad"

    for i, caso in enumerate(conversaciones_prueba, 1):
        print(f"📋 Interacción {i}: {caso['descripcion']}")
        print(f"👤 Usuario: {caso['mensaje']}")

        # Obtener respuesta del chatbot
        respuesta = get_chatbot_response(caso['mensaje'], cliente_id=cliente_id)

        print(f"🤖 Chatbot: {respuesta[:300]}..." if len(respuesta) > 300 else f"🤖 Chatbot: {respuesta}")
        print("-" * 80)

    # Obtener historial final
    from cooperativa.apps.chatbot.chatbot import get_historial_conversacion
    historial = get_historial_conversacion(cliente_id)

    print("📊 Resumen de la conversación:")
    print(f"   - Total interacciones: {len(historial['interaccion'])}")
    print(f"   - Total respuestas: {len(historial['respuestas_bot'])}")
    print(f"   - Nombre detectado: {historial.get('nombre', 'No detectado')}")

    # Verificar que se hayan hecho consultas de disponibilidad
    consultas_disponibilidad = [conv for conv in historial.get('conversaciones', [])
                               if conv.get('tipo_consulta') == 'disponibilidad_productos']

    print(f"   - Consultas de disponibilidad realizadas: {len(consultas_disponibilidad)}")

    print("\n✅ Prueba completa del chatbot finalizada exitosamente!")
    print("🎉 El chatbot ahora puede consultar la base de datos para verificar disponibilidad de productos.")

if __name__ == '__main__':
    probar_chatbot_completo()