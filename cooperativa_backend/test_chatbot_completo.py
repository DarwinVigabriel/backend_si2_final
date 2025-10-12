#!/usr/bin/env python3
"""
Script completo para probar el chatbot agrícola inteligente
Prueba todos los endpoints disponibles
"""
import requests
import json
import time

# Configuración del servidor
BASE_URL = "http://localhost:8000"
CHATBOT_URL = f"{BASE_URL}/chatbot"

def probar_chatbot():
    """Prueba completa del chatbot agrícola inteligente"""

    print("=" * 70)
    print("🧪 PRUEBA COMPLETA DEL CHATBOT AGRÍCOLA INTELIGENTE")
    print("=" * 70)

    # ID único para esta sesión de prueba
    cliente_id = f"test_{int(time.time())}"

    print(f"📋 Cliente ID: {cliente_id}")
    print(f"🌐 URL Base: {BASE_URL}")
    print()

    # Escenarios de prueba
    conversaciones_prueba = [
        {
            "mensaje": "Hola, me llamo María González",
            "descripcion": "Presentación y nombre"
        },
        {
            "mensaje": "Tengo 38 años y soy agricultora",
            "descripcion": "Edad y profesión"
        },
        {
            "mensaje": "Tengo una parcela propia de 3 hectáreas",
            "descripcion": "Información de parcela"
        },
        {
            "mensaje": "Cultivo maíz y papa principalmente",
            "descripcion": "Tipo de cultivos"
        },
        {
            "mensaje": "Necesito información sobre créditos agrícolas",
            "descripcion": "Consulta sobre créditos"
        },
        {
            "mensaje": "¿Cuáles son los requisitos para obtener un préstamo?",
            "descripcion": "Detalles de requisitos"
        },
        {
            "mensaje": "También me interesan las semillas certificadas",
            "descripcion": "Consulta sobre semillas"
        },
        {
            "mensaje": "¿Cómo puedo afiliarme a la cooperativa?",
            "descripcion": "Proceso de afiliación"
        }
    ]

    print("💬 PRUEBA DE CONVERSACIÓN")
    print("-" * 50)

    for i, conv in enumerate(conversaciones_prueba, 1):
        print(f"\n{i}. {conv['descripcion']}")
        print(f"   Usuario: {conv['mensaje']}")

        # Enviar mensaje al chatbot
        try:
            response = requests.post(
                f"{CHATBOT_URL}/api/",
                json={
                    "message": conv['mensaje'],
                    "cliente_id": cliente_id
                },
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                respuesta = data.get('response', 'Sin respuesta')
                print(f"   🤖 Chatbot: {respuesta[:100]}{'...' if len(respuesta) > 100 else ''}")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error de conexión: {e}")

        time.sleep(0.5)  # Pequeña pausa entre mensajes

    print("\n" + "=" * 50)
    print("📚 PRUEBA DE HISTORIAL")
    print("-" * 30)

    # Obtener historial de conversación
    try:
        response = requests.get(f"{CHATBOT_URL}/historial/{cliente_id}/")

        if response.status_code == 200:
            data = response.json()
            historial = data.get('historial', {})

            print("✅ Historial obtenido exitosamente")
            print(f"   📊 Total mensajes: {len(historial.get('interaccion', []))}")
            print(f"   👤 Nombre detectado: {historial.get('nombre', 'No detectado')}")
            print(f"   🎂 Edad detectada: {historial.get('edad', 'No detectada')}")
            print(f"   🌾 Cultivo detectado: {historial.get('tipo_cultivo', 'No detectado')}")
            print(f"   🎯 Necesidad principal: {historial.get('necesidad_principal', 'No detectada')}")
            print(f"   📈 Fase actual: {historial.get('fase', 'exploracion')}")
            print(f"   😊 Tono emocional: {historial.get('tono', 'neutro')}")
            print(f"   📈 Nivel de interés: {historial.get('nivel_interes', 'bajo')}")

            if historial.get('servicio_recomendado'):
                servicio = historial['servicio_recomendado']
                print(f"   🏆 Servicio recomendado: {servicio.get('tipo', 'Ninguno')}")
        else:
            print(f"❌ Error al obtener historial: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión al obtener historial: {e}")

    print("\n" + "=" * 50)
    print("🧹 PRUEBA DE LIMPIEZA DE HISTORIAL")
    print("-" * 40)

    # Limpiar historial
    try:
        response = requests.post(f"{CHATBOT_URL}/limpiar/{cliente_id}/")

        if response.status_code == 200:
            print("✅ Historial limpiado exitosamente")
        else:
            print(f"❌ Error al limpiar historial: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión al limpiar historial: {e}")

    print("\n" + "=" * 70)
    print("🎉 PRUEBA COMPLETADA")
    print("=" * 70)
    print("\n📋 RESUMEN DE ENDPOINTS DISPONIBLES:")
    print("   • POST /chatbot/api/ - Enviar mensaje al chatbot")
    print("   • GET /chatbot/historial/<cliente_id>/ - Obtener historial")
    print("   • POST /chatbot/limpiar/<cliente_id>/ - Limpiar historial")
    print("\n🔧 FORMATO DE PETICIONES:")
    print("   POST /chatbot/api/")
    print("   {")
    print('     "message": "Tu mensaje aquí",')
    print('     "cliente_id": "id_unico_del_cliente"')
    print("   }")

def verificar_servidor():
    """Verifica si el servidor está corriendo"""
    print("🔍 Verificando conexión con el servidor...")
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        print("✅ Servidor responde correctamente")
        return True
    except requests.exceptions.RequestException:
        print("❌ No se puede conectar al servidor")
        print("💡 Asegúrate de que el servidor Django esté ejecutándose:")
        print("   cd Backend_Django/cooperativa_backend")
        print("   python manage.py runserver")
        return False

if __name__ == "__main__":
    if verificar_servidor():
        probar_chatbot()
    else:
        print("\n❌ Prueba cancelada - servidor no disponible")