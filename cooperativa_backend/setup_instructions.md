# Instrucciones de Configuración - Sistema Cooperativa Agrícola

## 📋 Requisitos Previos

- Python 3.12.0 o superior
- PostgreSQL 12+ (o acceso a base de datos remota)
- Git
- Node.js 16+ (para el frontend React)

## 🚀 Configuración del Backend (Django)

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd proyecto_Final/Backend_Django/cooperativa_backend
```

### 2. Crear entorno virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar archivo de ejemplo
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Editar .env con tus datos:
# - DATABASE_URL: URL de tu base de datos PostgreSQL
# - SECRET_KEY: Generar nueva clave secreta Django
# - OPENROUTER_API_KEY: Tu API key de OpenRouter
```

### 5. Configurar base de datos
```bash
# Ejecutar migraciones
python manage.py makemigrations
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Cargar datos de prueba (opcional)
python manage.py loaddata fixtures/sample_data.json
```

### 6. Ejecutar servidor
```bash
python manage.py runserver
```

## 🌐 Configuración del Frontend (React)

### 1. Navegar al directorio del frontend
```bash
cd ../../Front_React/cooperativa_front
```

### 2. Instalar dependencias
```bash
npm install
```

### 3. Configurar variables de entorno
```bash
# Crear archivo .env en la raíz del proyecto React
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

### 4. Ejecutar aplicación
```bash
npm start
```

## 🔑 APIs y Servicios Externos

### OpenRouter (IA del Chatbot)
1. Crear cuenta en https://openrouter.ai/
2. Generar API Key
3. Agregar la API Key al archivo .env como `OPENROUTER_API_KEY`

### Base de Datos PostgreSQL
**Opción 1: Local**
```bash
# Instalar PostgreSQL
# Crear base de datos
createdb cooperativa_db
```

**Opción 2: Neon (Recomendado)**
1. Crear cuenta en https://neon.tech/
2. Crear nueva base de datos
3. Copiar DATABASE_URL al archivo .env

## 🧪 Verificar Instalación

### Backend
```bash
python manage.py check
python manage.py test
```

### Chatbot
```bash
# Probar API del chatbot
curl -X POST http://localhost:8000/chatbot/api/ \
  -H "Content-Type: application/json" \
  -d '{"message": "hola"}'
```

### Frontend
- Abrir http://localhost:3000
- Verificar que se conecta al backend
- Probar funcionalidades del chatbot

## 🛠️ Comandos Útiles

### Django
```bash
# Generar nueva SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Recopilar archivos estáticos
python manage.py collectstatic

# Ejecutar tests específicos
python manage.py test cooperativa.tests.test_chatbot
```

### Base de Datos
```bash
# Backup
pg_dump cooperativa_db > backup.sql

# Restore
psql cooperativa_db < backup.sql

# Reset migraciones (si hay problemas)
python manage.py migrate --fake cooperativa zero
python manage.py migrate cooperativa
```

## 📦 Estructura del Proyecto

```
Backend_Django/cooperativa_backend/
├── manage.py
├── requirements.txt
├── .env
├── cooperativa/
│   ├── models.py          # Modelos de BD
│   ├── views.py           # APIs REST
│   ├── apps/chatbot/      # Sistema de chatbot
│   └── migrations/
└── cooperativa_backend/
    ├── settings.py        # Configuración Django
    └── urls.py           # Rutas principales

Front_React/cooperativa_front/
├── package.json
├── .env
├── src/
│   ├── components/        # Componentes React
│   ├── pages/            # Páginas principales
│   └── services/         # APIs y servicios
└── public/
```

## 🐛 Solución de Problemas

### Error: "No module named 'dj_database_url'"
```bash
pip install dj-database-url
```

### Error: "CORS policy"
- Verificar CORS_ALLOWED_ORIGINS en settings.py
- Asegurar que el frontend esté en la lista de orígenes permitidos

### Error de conexión a BD
- Verificar DATABASE_URL en .env
- Confirmar que PostgreSQL está ejecutándose
- Verificar credenciales y permisos

### Chatbot no responde
- Verificar OPENROUTER_API_KEY en .env
- Comprobar límites de API en OpenRouter
- Revisar logs del servidor Django

### Error 429 (Rate Limit)
- El sistema automáticamente rota entre modelos gratuitos
- Esperar reset diario o agregar créditos a OpenRouter

## 📞 Soporte

Para problemas adicionales:
1. Verificar logs en consola del servidor Django
2. Revisar Network tab en navegador para errores de API
3. Comprobar que todos los servicios externos estén disponibles