"""
Tests para el chatbot con IA
"""

import os
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock


class ChatbotAPITests(APITestCase):
    """Tests para el endpoint del chatbot"""

    def setUp(self):
        """Configurar datos de prueba"""
        # No necesitamos autenticación para el chatbot según el código actual
        pass

    @patch('cooperativa.apps.chatbot.chatbot.client.chat.completions.create')
    def test_chatbot_api_success(self, mock_create):
        """Test que el endpoint del chatbot responde correctamente"""
        # Mock de la respuesta de OpenRouter
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Hola, soy tu asistente de la cooperativa."
        mock_create.return_value = mock_response

        # Datos de prueba
        data = {'message': 'Hola, ¿cómo estás?'}

        # Hacer la petición
        response = self.client.post('/chatbot/api/', data, format='json')

        # Verificar respuesta
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_data = response.json()
        self.assertIn('response', response_data)
        self.assertEqual(response_data['response'], "Hola, soy tu asistente de la cooperativa.")

        # Verificar que se llamó a la API
        mock_create.assert_called_once()

    def test_chatbot_api_invalid_method(self):
        """Test que el endpoint rechaza métodos no POST"""
        response = self.client.get('/chatbot/api/')
        self.assertEqual(response.status_code, 405)
        # Para vistas no-API, verificar el contenido de la respuesta
        self.assertIn('Only POST allowed', response.content.decode())

    def test_chatbot_api_missing_message(self):
        """Test que el endpoint maneja mensajes vacíos"""
        data = {}
        response = self.client.post('/chatbot/api/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # El código actual maneja mensajes vacíos como strings vacías

    @patch('cooperativa.apps.chatbot.chatbot.client.chat.completions.create')
    def test_chatbot_api_with_referer(self, mock_create):
        """Test que el endpoint incluye el referer en la petición a OpenRouter"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta de prueba"
        mock_create.return_value = mock_response

        data = {'message': 'Mensaje de prueba'}

        # Simular un referer
        response = self.client.post(
            '/chatbot/api/',
            data,
            format='json',
            HTTP_REFERER='http://localhost:3000'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se pasó el referer a la API
        call_args = mock_create.call_args
        extra_headers = call_args[1]['extra_headers']
        self.assertEqual(extra_headers['HTTP-Referer'], 'http://localhost:3000')
        self.assertEqual(extra_headers['X-Title'], 'Cooperativa Chatbot')

    @patch('cooperativa.apps.chatbot.chatbot.client.chat.completions.create')
    @patch.dict(os.environ, {'OPENROUTER_API_KEY': 'test_key'})
    def test_chatbot_api_uses_env_variable(self, mock_create):
        """Test que el endpoint usa la variable de entorno OPENROUTER_API_KEY"""
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Respuesta de prueba"
        mock_create.return_value = mock_response

        data = {'message': 'Mensaje de prueba'}
        response = self.client.post('/chatbot/api/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se usó la API key del entorno
        call_kwargs = mock_create.call_args[1]
        self.assertEqual(call_kwargs['api_key'], 'test_key')

    @patch('cooperativa.apps.chatbot.chatbot.client.chat.completions.create')
    def test_chatbot_api_handles_api_error(self, mock_create):
        """Test que el endpoint maneja errores de la API de OpenRouter"""
        # Simular error de la API
        mock_create.side_effect = Exception("API Error")

        data = {'message': 'Mensaje de prueba'}
        response = self.client.post('/chatbot/api/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        response_data = response.json()
        self.assertIn('error', response_data)