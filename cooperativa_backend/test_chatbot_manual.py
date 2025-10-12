import requests
import json

# URL del endpoint del chatbot
url = "http://127.0.0.1:8000/chatbot/api/"

# Datos a enviar
data = {
    "message": "Hola, ¿puedes ayudarme con información sobre la cooperativa?"
}

# Headers
headers = {
    "Content-Type": "application/json"
}

try:
    # Hacer la petición POST
    response = requests.post(url, json=data, headers=headers)

    # Verificar el código de estado
    print(f"Código de estado: {response.status_code}")

    if response.status_code == 200:
        # Mostrar la respuesta
        result = response.json()
        print("Respuesta del chatbot:")
        print(result.get("response", "No se encontró respuesta"))
    else:
        print(f"Error: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"Error de conexión: {e}")
    print("Asegúrate de que el servidor Django esté corriendo con: python manage.py runserver")