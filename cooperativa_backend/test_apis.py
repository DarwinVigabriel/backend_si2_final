import requests
import json

def login_and_test():
    base_url = 'http://127.0.0.1:8000'
    session = requests.Session()

    print('=== LOGIN ===')
    # Hacer login
    login_data = {
        'username': 'admin',
        'password': 'clave123'
    }

    try:
        response = session.post(f'{base_url}/api/auth/login/', json=login_data)
        print(f'Login Status Code: {response.status_code}')
        if response.status_code == 200:
            login_result = response.json()
            print(f'Login exitoso: {login_result.get("mensaje")}')
            print(f'Usuario: {login_result.get("usuario", {}).get("usuario")}')

            # Ahora probar las APIs con la sesión autenticada
            test_apis_with_session(session, base_url)
        else:
            print(f'Error en login: {response.text}')
    except Exception as e:
        print(f'Error de conexión en login: {e}')

def test_apis_with_session(session, base_url):
    apis = [
        ('semillas/', 'semillas'),
        ('pesticidas/', 'pesticidas'),
        ('fertilizantes/', 'fertilizantes')
    ]

    for endpoint, name in apis:
        print(f'\n=== PRUEBA API {name.upper()} ===')
        try:
            response = session.get(f'{base_url}/api/{endpoint}')
            print(f'Status Code: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                print(f'Numero de {name}: {len(data)}')
                if data:
                    if name == 'semillas':
                        print(f'Primera semilla: {data[0]["especie"]} - {data[0]["variedad"]}')
                    else:
                        print(f'Primer {name[:-1]}: {data[0]["nombre_comercial"]}')
                print(f'API de {name} funcionando correctamente')
            else:
                print(f'Error en API: {response.text}')
        except Exception as e:
            print(f'Error de conexión: {e}')

if __name__ == '__main__':
    login_and_test()