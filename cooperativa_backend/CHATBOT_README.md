# 🤖 Chatbot Agrícola Inteligente

Sistema de chatbot avanzado para la Cooperativa Agrícola Integral, capaz de mantener conversaciones contextuales, extraer información de productores y recomendar servicios apropiados.

## 🚀 Inicio Rápido

### 1. Iniciar el Servidor

```bash
cd Backend_Django/cooperativa_backend
python manage.py runserver
```

El servidor estará disponible en: `http://localhost:8000`

### 2. Probar el Chatbot

Ejecuta el script de prueba completo:

```bash
python test_chatbot_completo.py
```

## 📡 Endpoints Disponibles

### 1. Enviar Mensaje al Chatbot
**POST** `/chatbot/api/`

Envía un mensaje al chatbot y recibe una respuesta inteligente.

**Request:**
```json
{
  "message": "Hola, necesito información sobre créditos agrícolas",
  "cliente_id": "usuario_123"
}
```

**Response:**
```json
{
  "response": "¡Buenas tardes! Soy tu asistente de la Cooperativa Agrícola Integral...",
  "cliente_id": "usuario_123"
}
```

### 2. Obtener Historial de Conversación
**GET** `/chatbot/historial/<cliente_id>/`

Obtiene el historial completo de conversación de un cliente.

**Response:**
```json
{
  "cliente_id": "usuario_123",
  "historial": {
    "nombre": "Juan Pérez",
    "edad": 45,
    "tipo_cultivo": "maiz",
    "necesidad_principal": "credito",
    "fase": "recomendacion",
    "interaccion": ["Hola...", "Necesito..."],
    "respuestas_bot": ["¡Hola!...", "Te recomiendo..."]
  }
}
```

### 3. Limpiar Historial
**POST** `/chatbot/limpiar/<cliente_id>/`

Limpia todo el historial de conversación de un cliente.

**Response:**
```json
{
  "mensaje": "Historial limpiado para cliente usuario_123",
  "cliente_id": "usuario_123"
}
```

## 🧠 Funcionalidades Inteligentes

### Extracción Automática de Datos
- **Nombre**: Detecta automáticamente el nombre del productor
- **Edad**: Extrae información de edad de los mensajes
- **Tipo de Parcela**: Identifica si es propia, arrendada, etc.
- **Cultivos**: Detecta tipos de cultivos mencionados
- **Necesidades**: Identifica requerimientos específicos

### Recomendación Inteligente de Servicios
Basado en el perfil del productor, recomienda:
- 🏦 **Créditos Agrícolas**: Préstamos con tasas preferenciales
- 🌱 **Semillas Certificadas**: Maíz, soja, trigo, etc.
- 🧪 **Insumos Agrícolas**: Fertilizantes, pesticidas
- 👨‍🌾 **Asesoría Técnica**: Soporte especializado
- 📦 **Comercialización**: Ayuda para vender producción

### Gestión de Conversación
- **Fases**: Exploración → Recomendación
- **Contexto**: Mantiene historial de conversación
- **Tono Emocional**: Detecta sentimientos del usuario
- **Etiquetas**: Clasifica automáticamente las consultas

## 🧪 Ejemplos de Uso

### Ejemplo 1: Nuevo Productor
```javascript
// Primer mensaje
POST /chatbot/api/
{
  "message": "Hola, me llamo Ana López",
  "cliente_id": "ana_lopez_001"
}
// Respuesta: Saludo personalizado y pregunta por necesidades

// Segundo mensaje
POST /chatbot/api/
{
  "message": "Tengo 35 años y cultivo soja",
  "cliente_id": "ana_lopez_001"
}
// Respuesta: Información específica sobre servicios para cultivo de soja
```

### Ejemplo 2: Consulta Específica
```javascript
POST /chatbot/api/
{
  "message": "Necesito semillas de maíz certificadas",
  "cliente_id": "pedro_garcia_002"
}
// Respuesta: Detalles sobre semillas disponibles, precios y beneficios
```

### Ejemplo 3: Ver Historial
```javascript
GET /chatbot/historial/ana_lopez_001/
// Respuesta: Historial completo con datos extraídos y recomendaciones
```

## 📊 Base de Conocimientos

El chatbot utiliza una base de conocimientos completa que incluye:

- **Servicios Cooperativa**: Créditos, semillas, insumos, asesoría, comercialización
- **Productos Disponibles**: Catálogo completo de semillas e insumos
- **Precios Referenciales**: Información actualizada de costos
- **Requisitos**: Documentación necesaria para cada servicio
- **Beneficios**: Ventajas de ser socio de la cooperativa

## 🔧 Configuración

### Variables de Entorno
Asegúrate de tener configurada la variable:
```
OPENROUTER_API_KEY=tu_clave_api_aqui
```

### Dependencias
```bash
pip install -r requirements.txt
```

## 🐛 Solución de Problemas

### Error de Conexión
- Verifica que el servidor Django esté ejecutándose
- Confirma que la URL base sea correcta

### Respuestas Genéricas
- El chatbot está en fase de aprendizaje
- Proporciona más contexto en tus mensajes

### Historial Vacío
- Cada cliente tiene su propio historial identificado por `cliente_id`
- Usa el mismo `cliente_id` para mantener la conversación

## 📈 Próximas Mejoras

- [ ] Integración con WhatsApp Business API
- [ ] Soporte multiidioma (quechua, guaraní)
- [ ] Base de datos persistente para historiales
- [ ] Análisis de sentimientos avanzado
- [ ] Recomendaciones basadas en ubicación geográfica
- [ ] Integración con sistema de gestión de socios

## 🤝 Contribuir

Para mejorar el chatbot:

1. Agrega nuevos servicios a `base_conocimiento_cooperativa.json`
2. Mejora la lógica de extracción en `agente_cooperativa.py`
3. Añade nuevos endpoints según necesidades
4. Actualiza este README con nuevas funcionalidades

---

**Cooperativa Agrícola Integral** - Sistema de Información 2
📧 Contacto: admin@cooperativaagricola.com