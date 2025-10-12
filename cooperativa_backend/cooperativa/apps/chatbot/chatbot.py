import os
import json
from openai import OpenAI
from .agente_cooperativa import agente_agricola

# Almacenamiento temporal de historiales de conversación
historiales_conversacion = {}

# No más cache de respuestas - todo debe pasar por IA con contexto de BD

def inicializar_historial(cliente_id):
    """Inicializa el historial de conversación para un cliente"""
    if cliente_id not in historiales_conversacion:
        historiales_conversacion[cliente_id] = {
            "interaccion": [],
            "respuestas_bot": [],
            "contexto_cliente": "",
            "fase": "exploracion",
            "saludo_enviado": False,
            "etiquetas": [],
            "conversaciones": []
        }
    return historiales_conversacion[cliente_id]

def get_chatbot_response(user_message, referer=None, title=None, cliente_id="default"):
    """
    Obtiene respuesta del chatbot usando el agente agrícola inteligente
    """
    # Inicializar o obtener historial
    historial = inicializar_historial(cliente_id)

    # No más cache - todo debe pasar por agente con IA

    # Usar el agente agrícola para procesar el mensaje
    respuesta_agente = agente_agricola(user_message, historial, referer, title)

    # Si el agente no puede manejar la consulta, usar IA como respaldo
    if not respuesta_agente or len(respuesta_agente.strip()) < 10:
        respuesta_agente = get_openai_response(user_message, referer, title)

    # Actualizar historial con la respuesta final
    historial["respuestas_bot"].append(respuesta_agente)

    return respuesta_agente

def get_openai_response(prompt, referer=None, title=None):
    """
    Obtiene respuesta de IA usando rotación de modelos gratuitos
    """
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is not set")

    # Lista de modelos gratuitos para rotar
    free_models = [
        "google/gemma-3n-e2b-it:free",
        "nvidia/nemotron-nano-9b-v2:free", 
        "alibaba/tongyi-deepresearch-30b-a3b:free",
        "deepseek/deepseek-chat-v3.1:free",
        "openai/gpt-oss-20b:free",
        "moonshotai/kimi-k2:free"
    ]

    # Asegurar que el prompt sea una cadena UTF-8 válida
    if isinstance(prompt, str):
        try:
            prompt.encode('utf-8')
        except UnicodeEncodeError:
            prompt = prompt.encode('utf-8', errors='ignore').decode('utf-8')

    # Configurar cliente
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key
    )

    # Intentar con cada modelo hasta que uno funcione
    for model in free_models:
        try:
            print(f"DEBUG - Probando modelo: {model}")
            completion = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente agrícola especializado que ayuda a productores con información precisa sobre productos y servicios agrícolas. Mantén respuestas concisas, útiles y en español."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=800
            )
            print(f"DEBUG - Modelo {model} funcionó!")
            return completion.choices[0].message.content
            
        except Exception as e:
            print(f"Error con modelo {model}: {e}")
            # Si es rate limit, probar siguiente modelo
            if "429" in str(e) or "rate limit" in str(e).lower():
                continue
            # Si es otro error, también probar siguiente
            continue
    
    # Si todos los modelos fallan, devolver error
    print("DEBUG - Todos los modelos fallaron")
    raise Exception("Todos los modelos de IA están temporalmente no disponibles")

def get_historial_conversacion(cliente_id):
    """Obtiene el historial completo de conversación de un cliente"""
    return inicializar_historial(cliente_id)

def limpiar_historial(cliente_id):
    """Limpia el historial de conversación de un cliente"""
    if cliente_id in historiales_conversacion:
        del historiales_conversacion[cliente_id]
