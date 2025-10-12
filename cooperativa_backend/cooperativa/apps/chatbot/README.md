# Cooperativa Chatbot

Este módulo integra un chatbot con IA usando el modelo DeepSeek V3.1 vía OpenRouter.

## Estructura
- `chatbot.py`: Lógica para interactuar con la API de OpenRouter.
- `views.py`: Endpoint Django para recibir mensajes y devolver respuestas.
- `urls.py`: Routing del endpoint.
- `__init__.py`: Marca el paquete.

## Uso
1. Agrega la app a `INSTALLED_APPS` en tu `settings.py`.
2. Incluye las URLs en tu archivo principal de rutas:
   ```python
   path('chatbot/', include('cooperativa.apps.chatbot.urls')),
   ```
3. Haz POST a `/chatbot/api/` con `{ "message": "tu mensaje" }` para obtener respuesta.

## Seguridad
- La API key se toma de variable de entorno `OPENROUTER_API_KEY` (o puedes ponerla directamente en `chatbot.py`).
- No expongas la API key en el frontend.
