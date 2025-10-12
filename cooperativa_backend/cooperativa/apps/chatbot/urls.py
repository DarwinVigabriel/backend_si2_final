from django.urls import path
from .views import chatbot_api, chatbot_historial, chatbot_limpiar

urlpatterns = [
    path('api/', chatbot_api, name='chatbot_api'),
    path('historial/<str:cliente_id>/', chatbot_historial, name='chatbot_historial'),
    path('limpiar/<str:cliente_id>/', chatbot_limpiar, name='chatbot_limpiar'),
]
