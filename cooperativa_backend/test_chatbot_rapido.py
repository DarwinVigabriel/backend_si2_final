#!/usr/bin/env python3
"""
Script rápido para probar el chatbot agrícola
Ejecuta pruebas básicas de conectividad y funcionalidad
"""
import requests
import json
import time

def test_basico():
    """Prueba básica de conectividad"""
    print("🔍 Probando conectividad básica...")

    try:
        response = requests.post(
            "http://localhost:8000/chatbot/api/",
            json={"message": "Hola", "cliente_id": "test_001"},
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print("✅ Conexión exitosa!")
            print(f"   Respuesta: {data.get('response', '')[:50]}...")
            return True
        else:
            print(f"❌ Error HTTP {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        print("\n💡 Asegúrate de que el servidor esté ejecutándose:")
        print("   cd Backend_Django/cooperativa_backend")
        print("   python manage.py runserver")
        return False

def test_conversacion():
    """Prueba una conversación completa"""
    print("\n💬 Probando conversación inteligente...")

    cliente_id = f"test_{int(time.time())}"
    mensajes_prueba = [
        "Hola, me llamo Carlos Mendoza",
        "Tengo 42 años y cultivo soja",
        "Necesito información sobre créditos"
    ]

    for mensaje in mensajes_prueba:
        try:
            response = requests.post(
                "http://localhost:8000/chatbot/api/",
                json={"message": mensaje, "cliente_id": cliente_id},
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                print(f"   👤 Usuario: {mensaje}")
                print(f"   🤖 Chatbot: {data.get('response', '')[:60]}...")
                print()
            else:
                print(f"   ❌ Error en mensaje '{mensaje}': {response.status_code}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error en mensaje '{mensaje}': {e}")
            return False

        time.sleep(0.5)

    return True

def test_historial():
    """Prueba la obtención de historial"""
    print("📚 Probando historial de conversación...")

    cliente_id = "test_historial_001"

    # Primero enviar un mensaje
    try:
        requests.post(
            "http://localhost:8000/chatbot/api/",
            json={"message": "Hola", "cliente_id": cliente_id},
            timeout=5
        )
    except:
        pass

    # Obtener historial
    try:
        response = requests.get(f"http://localhost:8000/chatbot/historial/{cliente_id}/")

        if response.status_code == 200:
            data = response.json()
            historial = data.get('historial', {})
            print("✅ Historial obtenido exitosamente!")
            print(f"   Mensajes: {len(historial.get('interaccion', []))}")
            print(f"   Fase: {historial.get('fase', 'desconocida')}")
            return True
        else:
            print(f"❌ Error al obtener historial: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def main():
    """Función principal"""
    print("=" * 60)
    print("🧪 PRUEBA RÁPIDA DEL CHATBOT AGRÍCOLA")
    print("=" * 60)

    # Ejecutar pruebas
    pruebas = [
        ("Conectividad básica", test_basico),
        ("Conversación inteligente", test_conversacion),
        ("Historial de conversación", test_historial)
    ]

    resultados = []
    for nombre, funcion in pruebas:
        print(f"\n🔬 {nombre}:")
        print("-" * 40)
        resultado = funcion()
        resultados.append((nombre, resultado))

    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)

    exitosas = 0
    for nombre, resultado in resultados:
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"   {status} - {nombre}")
        if resultado:
            exitosas += 1

    print(f"\n🏆 Resultado: {exitosas}/{len(resultados)} pruebas exitosas")

    if exitosas == len(resultados):
        print("\n🎉 ¡Todas las pruebas pasaron! El chatbot está listo.")
        print("\n📖 Para más pruebas detalladas:")
        print("   python test_chatbot_completo.py")
        print("\n🌐 Para probar desde el navegador:")
        print("   abre chatbot_demo.html")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa la configuración.")

if __name__ == "__main__":
    main()