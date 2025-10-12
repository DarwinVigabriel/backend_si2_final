from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .chatbot import get_chatbot_response, get_historial_conversacion, limpiar_historial
import json

@csrf_exempt
def chatbot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            cliente_id = data.get('cliente_id', 'default')  # ID único para la conversación
            referer = request.META.get('HTTP_REFERER')
            title = 'Cooperativa Chatbot'

            # Obtener respuesta del agente agrícola inteligente
            response = get_chatbot_response(user_message, referer, title, cliente_id)

            return JsonResponse({
                'response': response,
                'cliente_id': cliente_id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST allowed'}, status=405)

@csrf_exempt
def chatbot_historial(request, cliente_id):
    """
    Obtener el historial de conversación de un cliente
    """
    if request.method == 'GET':
        try:
            historial = get_historial_conversacion(cliente_id)
            return JsonResponse({
                'cliente_id': cliente_id,
                'historial': historial
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only GET allowed'}, status=405)

@csrf_exempt
def chatbot_limpiar(request, cliente_id):
    """
    Limpiar el historial de conversación de un cliente
    """
    if request.method == 'POST':
        try:
            limpiar_historial(cliente_id)
            return JsonResponse({
                'mensaje': f'Historial limpiado para cliente {cliente_id}',
                'cliente_id': cliente_id
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Only POST allowed'}, status=405)
