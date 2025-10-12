#!/usr/bin/env python3
"""
Script de prueba para el agente agrícola inteligente
"""
import sys
import os
import json

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

# Importar el agente agrícola
from cooperativa.apps.chatbot.agente_cooperativa import agente_agricola, inicializar_historial

def probar_agente():
    """Probar el agente agrícola con diferentes escenarios"""

    print("=" * 60)
    print("PRUEBA DEL AGENTE AGRÍCOLA INTELIGENTE")
    print("=" * 60)

    # Inicializar historial
    cliente_id = "test_productor_001"
    historial = inicializar_historial(cliente_id)

    # Escenarios de prueba
    escenarios = [
        "Hola, me llamo Juan Pérez",
        "Tengo 45 años y soy agricultor",
        "Necesito información sobre créditos agrícolas",
        "Tengo una parcela de 5 hectáreas",
        "Cultivo maíz y soja",
        "¿Qué servicios ofrecen para semillas?",
        "Estoy interesado en afiliarme a la cooperativa",
        "¿Cuáles son los requisitos para obtener un préstamo?",
        "Necesito asesoría técnica para fertilizantes",
        "¿Cómo puedo vender mi producción?"
    ]

    print(f"\nCliente ID: {cliente_id}")
    print("-" * 40)

    for i, mensaje in enumerate(escenarios, 1):
        print(f"\nMensaje {i}: {mensaje}")

        # Obtener respuesta del agente
        respuesta = agente_agricola(mensaje, historial)

        print(f"Respuesta: {respuesta}")

        # Mostrar estado del historial
        print(f"Estado - Nombre: {historial.get('nombre', 'No detectado')}, "
              f"Edad: {historial.get('edad', 'No detectada')}, "
              f"Necesidad: {historial.get('necesidad_principal', 'No detectada')}, "
              f"Fase: {historial.get('fase', 'exploracion')}")

        print("-" * 40)

    # Mostrar resumen final
    print("\n" + "=" * 60)
    print("RESUMEN FINAL DE LA CONVERSACIÓN")
    print("=" * 60)
    print(json.dumps({
        "cliente_id": cliente_id,
        "nombre": historial.get("nombre"),
        "edad": historial.get("edad"),
        "tipo_parcela": historial.get("tipo_parcela"),
        "tipo_cultivo": historial.get("tipo_cultivo"),
        "necesidad_principal": historial.get("necesidad_principal"),
        "servicio_recomendado": historial.get("servicio_recomendado"),
        "fase": historial.get("fase"),
        "tono": historial.get("tono"),
        "nivel_interes": historial.get("nivel_interes"),
        "total_mensajes": len(historial.get("interaccion", [])),
        "total_respuestas": len(historial.get("respuestas_bot", []))
    }, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("HISTORIAL COMPLETO DE CONVERSACIONES")
    print("=" * 60)
    for i, conv in enumerate(historial.get("conversaciones", []), 1):
        print(f"{i}. {conv['pregunta']} -> {conv['respuesta'][:100]}...")

if __name__ == "__main__":
    probar_agente()