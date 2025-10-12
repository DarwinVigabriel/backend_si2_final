#!/usr/bin/env python3
"""
Script de prueba para verificar que el chatbot use IA en lugar de respuestas predefinidas
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
    django.setup()

from cooperativa.apps.chatbot.agente_cooperativa import agente_agricola

def test_chatbot_ia():
    """Prueba que el chatbot use IA para respuestas"""
    print("🧪 Probando integración de IA en el chatbot agrícola")
    print("=" * 60)

    # Crear historial de prueba
    historial = {
        "interaccion": [],
        "respuestas_bot": [],
        "contexto_cliente": "",
        "fase": "exploracion",
        "saludo_enviado": False,
        "etiquetas": [],
        "conversaciones": []
    }

    # Mensajes de prueba
    test_messages = [
        "Hola, quiero saber sobre sus productos",
        "¿Qué semillas tienen disponibles?",
        "¿Cuánto cuesta el fertilizante?",
        "Necesito ayuda con plagas en mi cultivo de maíz"
    ]

    for i, mensaje in enumerate(test_messages, 1):
        print(f"\n📝 Prueba {i}: '{mensaje}'")
        print("-" * 40)

        try:
            respuesta = agente_agricola(mensaje, historial, "http://localhost:3000", "Cooperativa Chatbot Test")

            print(f"🤖 Respuesta: {respuesta[:200]}{'...' if len(respuesta) > 200 else ''}")

            # Verificar que no sea una respuesta predefinida muy corta
            if len(respuesta.strip()) < 20:
                print("⚠️  ADVERTENCIA: Respuesta muy corta, posible respuesta predefinida")
            elif "procesando tu consulta" in respuesta.lower():
                print("⚠️  ADVERTENCIA: Respuesta genérica de procesamiento")
            elif "¿En qué puedo ayudarte" in respuesta.lower():
                print("⚠️  ADVERTENCIA: Respuesta predefinida detectada")
            else:
                print("✅ Respuesta parece generada por IA")

        except Exception as e:
            print(f"❌ ERROR: {e}")

    print("\n" + "=" * 60)
    print("🏁 Prueba completada")
    print("\n💡 Si ves muchas advertencias, el chatbot podría no estar usando IA correctamente.")

if __name__ == "__main__":
    test_chatbot_ia()