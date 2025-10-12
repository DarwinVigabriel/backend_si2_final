import json
import os
import re
from datetime import datetime

# Importaciones para consultas a base de datos
import django
from django.conf import settings

# Configurar Django si no está configurado
if not settings.configured:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cooperativa_backend.settings')
    django.setup()

from cooperativa.models import Semilla, Pesticida, Fertilizante

# -------------------- Configuración del modelo IA --------------------
# Usaremos el mismo modelo que ya está configurado en chatbot.py

# -------------------- Cargar base de conocimientos --------------------
with open("cooperativa/apps/chatbot/base_conocimiento_cooperativa.json", "r", encoding="utf-8") as f:
    BASE_CONOCIMIENTOS = json.load(f)

# -------------------- Funciones Auxiliares --------------------

def extraer_edad(mensaje):
    """Extrae edad del mensaje del usuario"""
    match = re.search(r'\b(\d{1,2})\s*(años|años de edad|anios|anios de edad)\b', mensaje, re.IGNORECASE)
    if match:
        return int(match.group(1))
    return None

def extraer_tipo_parcela(mensaje):
    """Extrae tipo de parcela mencionada"""
    tipos = ["propia", "arrendada", "familiar", "comunitaria"]
    mensaje_lower = mensaje.lower()
    for tipo in tipos:
        if tipo in mensaje_lower:
            return tipo
    return None

def extraer_tipo_cultivo(mensaje):
    """Extrae tipo de cultivo mencionado"""
    cultivos = ["maiz", "maíz", "soya", "soja", "trigo", "arroz", "quinoa", "papa", "tomate", "cebolla", "zanahoria"]
    mensaje_lower = mensaje.lower()
    for cultivo in cultivos:
        if cultivo in mensaje_lower:
            return cultivo.replace("maíz", "maiz").replace("soja", "soya")
    return None

def extraer_necesidad_servicio(mensaje):
    """Extrae necesidad de servicio del mensaje"""
    necesidades = {
        "credito": ["credito", "préstamo", "prestamo", "financiamiento", "dinero"],
        "semillas": ["semillas", "siembra", "sembrar"],
        "insumos": ["insumos", "fertilizantes", "pesticidas", "agroquimicos"],
        "asesoria": ["asesoria", "asesoría", "tecnica", "técnica", "ayuda", "recomendacion"],
        "comercializacion": ["vender", "venta", "comercializar", "mercado", "precio"]
    }

    mensaje_lower = mensaje.lower()
    for servicio, palabras_clave in necesidades.items():
        for palabra in palabras_clave:
            if palabra in mensaje_lower:
                return servicio
    return None

def limpiar_respuesta(texto):
    """Limpia y formatea la respuesta"""
    if not texto or not isinstance(texto, str):
        return ""

    # Remover caracteres de escape problemáticos
    texto = texto.replace("\\n", " ")
    texto = re.sub(r"\s+", " ", texto)
    texto = re.sub(r"\\+", "", texto)

    # Limpiar respuesta de tokens especiales de IA
    if '<｜' in texto or '<|' in texto:
        texto = texto.split('<｜')[0].split('<|')[0].strip()

    # Detectar y eliminar respuestas repetitivas o inválidas
    texto_lower = texto.lower().strip()

    # Si la respuesta se repite muchas veces (como "The user is...")
    if texto_lower.count("the user is") > 3:  # Reducido de 5 a 3
        return ""

    # Si contiene frases repetitivas - hacer menos restrictivo
    palabras = texto_lower.split()
    if len(palabras) > 100:  # Aumentado de 50 a 100
        # Tomar solo las primeras 150 palabras en lugar de 100
        texto = " ".join(texto.split()[:150])

    # Si la respuesta es mayormente la misma frase repetida - hacer menos restrictivo
    if len(palabras) > 10 and len(set(palabras)) < len(palabras) * 0.5:  # Cambiado de 0.3 a 0.5
        return ""

    return texto.strip()

def detectar_tono_emocional(texto):
    """Detecta el tono emocional del mensaje"""
    texto = texto.lower()
    if any(p in texto for p in ["gracias", "excelente", "me encanta", "fantástico", "genial", "perfecto", "conforme"]):
        return "positivo"
    if any(p in texto for p in ["no entiendo", "caro", "molesto", "decepcionado", "frustrado", "complicado", "difícil"]):
        return "negativo"
    return "neutro"

def evaluar_interes_agricola(contexto):
    """Evalúa el nivel de interés en servicios agrícolas"""
    contexto = contexto.lower()
    if any(p in contexto for p in ["quiero afiliarme", "me interesa", "afiliarme", "unirme", "socio", "inscribirme"]):
        return "alto"
    if any(p in contexto for p in ["cuánto cuesta", "qué ofrecen", "información", "detalles", "requisitos"]):
        return "medio"
    return "bajo"

def detectar_etiquetas_agricolas(texto):
    """Detecta etiquetas relacionadas con agricultura"""
    etiquetas = []
    texto = texto.lower()

    # Servicios
    if any(k in texto for k in ["credito", "préstamo", "prestamo", "financiamiento"]):
        etiquetas.append("credito")
    if any(k in texto for k in ["semillas", "siembra", "sembrar"]):
        etiquetas.append("semillas")
    if any(k in texto for k in ["insumos", "fertilizantes", "pesticidas"]):
        etiquetas.append("insumos")
    if any(k in texto for k in ["asesoria", "asesoría", "tecnica", "técnica"]):
        etiquetas.append("asesoria")
    if any(k in texto for k in ["vender", "venta", "comercializar", "mercado"]):
        etiquetas.append("comercializacion")

    # Afiliación
    if any(k in texto for k in ["afiliar", "socio", "unirme", "inscribir"]):
        etiquetas.append("afiliacion")

    # Cultivos
    cultivos = ["maiz", "maíz", "soya", "soja", "trigo", "arroz", "quinoa", "papa"]
    for cultivo in cultivos:
        if cultivo in texto:
            etiquetas.append("cultivo")

    return etiquetas

def extraer_nombre(mensaje):
    """Extrae nombre del usuario del mensaje"""
    patrones_nombre = [
        r"(?:me llamo|soy|mi nombre es)\s+([A-Za-záéíóúÁÉÍÓÚñÑ]+(?:\s+[A-Za-záéíóúÁÉÍÓÚñÑ]+)?)",
        r"(?:puedes llamarme|dime)\s+([A-Za-záéíóúÁÉÍÓÚñÑ]+(?:\s+[A-Za-záéíóúÁÉÍÓÚñÑ]+)?)",
    ]
    for patron in patrones_nombre:
        match = re.search(patron, mensaje, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None

def determinar_etapa_conversacion(historial):
    """Determina la etapa de la conversación agrícola"""
    num_interacciones = len(historial["interaccion"])
    if not historial.get("nombre"):
        return "presentacion"
    if num_interacciones <= 1:
        return "presentacion"
    elif num_interacciones <= 3:
        return "exploracion_necesidades"
    else:
        return "recomendacion_servicios"

def obtener_objetivo_etapa(etapa):
    """Obtiene el objetivo de cada etapa de conversación"""
    objetivos = {
        "presentacion": "Presentarme y conocer el nombre del productor.",
        "exploracion_necesidades": "Descubrir qué necesita el productor agrícola.",
        "recomendacion_servicios": "Ofrecer los servicios más apropiados según sus necesidades."
    }
    return objetivos.get(etapa, "Ayudar al productor con sus necesidades agrícolas.")

def seleccionar_servicio_apropiado(historial, base_conocimientos):
    """Selecciona el servicio más apropiado basado en el historial"""
    necesidad_principal = historial.get("necesidad_principal")
    tipo_cultivo = historial.get("tipo_cultivo")

    servicios = base_conocimientos["CooperativaAgricola"]["serviciosCooperativa"]

    if necesidad_principal == "credito":
        return {
            "tipo": "credito",
            "servicio": servicios["creditoAgricola"],
            "recomendacion": "Te recomiendo nuestro servicio de crédito agrícola con tasas preferenciales."
        }
    elif necesidad_principal == "semillas":
        return {
            "tipo": "semillas",
            "servicio": servicios["suministroSemillas"],
            "recomendacion": "Nuestras semillas certificadas pueden mejorar significativamente tus rendimientos."
        }
    elif necesidad_principal == "insumos":
        return {
            "tipo": "insumos",
            "servicio": servicios["suministroInsumos"],
            "recomendacion": "Ofrecemos insumos de calidad con asesoría técnica incluida."
        }
    elif necesidad_principal == "asesoria":
        return {
            "tipo": "asesoria",
            "servicio": servicios["asesoriaTecnica"],
            "recomendacion": "Nuestra asesoría técnica puede optimizar tus prácticas agrícolas."
        }
    else:
        return {
            "tipo": "general",
            "servicio": servicios["creditoAgricola"],
            "recomendacion": "Como socio de la cooperativa, tienes acceso a múltiples beneficios."
        }

def actualizar_fase_agricola(historial):
    """Actualiza la fase de la conversación agrícola"""
    if historial["fase"] == "recomendacion":
        return

    nombre_ok = bool(historial.get("nombre"))
    necesidad_ok = bool(historial.get("necesidad_principal"))

    if nombre_ok and necesidad_ok:
        historial["fase"] = "recomendacion"
    else:
        historial["fase"] = "exploracion"

def guardar_historial_agricola(cliente_id, historial):
    """Guarda el historial de conversación agrícola"""
    os.makedirs("conversaciones_agricolas", exist_ok=True)
    with open(f"conversaciones_agricolas/{cliente_id}.json", "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)
    return cliente_id

def inicializar_historial(cliente_id):
    """Inicializa el historial de conversación para un cliente agrícola"""
    return {
        "cliente_id": cliente_id,
        "interaccion": [],
        "respuestas_bot": [],
        "contexto_cliente": "",
        "fase": "exploracion",
        "saludo_enviado": False,
        "etiquetas": [],
        "conversaciones": []
    }

# -------------------- Agente agrícola principal --------------------

def agente_agricola(mensaje, historial, referer=None, title=None):
    """
    Agente inteligente para cooperativa agrícola
    """
    # 1. Guardar mensaje y actualizar contexto
    historial["interaccion"].append(mensaje)
    historial["contexto_cliente"] += f"\nProductor: {mensaje}"
    historial["tono"] = detectar_tono_emocional(mensaje)
    historial["nivel_interes"] = evaluar_interes_agricola(historial["contexto_cliente"])

    # Agregar etiquetas
    historial.setdefault("etiquetas", [])
    nuevas_etiquetas = detectar_etiquetas_agricolas(mensaje)
    historial["etiquetas"] = list(set(historial["etiquetas"] + nuevas_etiquetas))

    # Extraer datos básicos
    if not historial.get("nombre"):
        nombre_detectado = extraer_nombre(mensaje)
        if nombre_detectado:
            historial["nombre"] = nombre_detectado

    if not historial.get("edad"):
        edad_extraida = extraer_edad(mensaje)
        if edad_extraida:
            historial["edad"] = edad_extraida

    if not historial.get("tipo_parcela"):
        tipo_detectado = extraer_tipo_parcela(mensaje)
        if tipo_detectado:
            historial["tipo_parcela"] = tipo_detectado

    if not historial.get("tipo_cultivo"):
        cultivo_detectado = extraer_tipo_cultivo(mensaje)
        if cultivo_detectado:
            historial["tipo_cultivo"] = cultivo_detectado

    if not historial.get("necesidad_principal"):
        necesidad_detectada = extraer_necesidad_servicio(mensaje)
        if necesidad_detectada:
            historial["necesidad_principal"] = necesidad_detectada

    # NO MÁS RESPUESTAS PREDEFINIDAS - TODO POR IA
    # Solo obtener información de productos para contexto de IA

    # Preparar saludo
    if not historial.get("saludo_enviado"):
        if len(historial["interaccion"]) == 1:
            hora_actual = datetime.now().hour
            if 5 <= hora_actual < 12:
                saludo = "¡Buenos días! "
            elif 12 <= hora_actual < 19:
                saludo = "¡Buenas tardes! "
            else:
                saludo = "¡Buenas noches! "

            if historial.get("nombre"):
                saludo += f"Encantado de ayudarte, {historial['nombre']}. "
            else:
                saludo += "Soy tu asistente de la Cooperativa Agrícola Integral. "
            historial["saludo_enviado"] = True
        else:
            saludo = ""
    else:
        saludo = ""

    # Actualizar fase
    actualizar_fase_agricola(historial)

    # Seleccionar servicio si estamos en fase de recomendación
    if historial["fase"] == "recomendacion" and not historial.get("servicio_recomendado"):
        servicio = seleccionar_servicio_apropiado(historial, BASE_CONOCIMIENTOS)
        if servicio:
            historial["servicio_recomendado"] = servicio

    # Limitar historial
    historial["interaccion"] = historial["interaccion"][-10:]
    historial["respuestas_bot"] = historial["respuestas_bot"][-10:]

    # Construir resumen de conversación
    texto_conversacion = []
    for i, user_msg in enumerate(historial["interaccion"]):
        texto_conversacion.append(f"Productor: {user_msg}")
        if i < len(historial["respuestas_bot"]):
            texto_conversacion.append(f"Asistente: {historial['respuestas_bot'][i]}")
    texto_conversacion_str = "\n".join(texto_conversacion)

    # Convertir base de conocimientos a string
    contexto_base = ""
    for clave, content in BASE_CONOCIMIENTOS.items():
        contexto_base += f"[{clave}]\n"
        if isinstance(content, dict):
            for subclave, valor in content.items():
                contexto_base += f"- {subclave}: {valor}\n"

    # Obtener información actualizada de productos para el contexto de la IA
    info_productos = obtener_informacion_productos()

    # Instrucciones específicas
    instrucciones_extra = ""
    if len(historial["interaccion"]) == 1:
        instrucciones_extra = "Pregunta por el nombre del productor si no lo sabes."

    # Construir prompt completo para IA
    prompt = f"""
Eres un asistente agrícola especializado en cooperativas. Ayuda a los productores con información sobre servicios, cultivos y productos disponibles.

Fase actual: {historial.get("fase", "exploracion")}
Etapa: {determinar_etapa_conversacion(historial)}
Objetivo: {obtener_objetivo_etapa(determinar_etapa_conversacion(historial))}

Datos del productor:
- Nombre: {historial.get("nombre", "No disponible")}
- Edad: {historial.get("edad", "No especificada")}
- Tipo de parcela: {historial.get("tipo_parcela", "No especificada")}
- Tipo de cultivo: {historial.get("tipo_cultivo", "No especificado")}
- Necesidad principal: {historial.get("necesidad_principal", "No identificada")}
- Servicio recomendado: {historial.get("servicio_recomendado", {})}

Tono emocional: {historial.get("tono", "neutro")}
Nivel de interés: {historial.get("nivel_interes", "bajo")}

BASE DE CONOCIMIENTOS COOPERATIVA:
{contexto_base}

INVENTARIO ACTUAL DE PRODUCTOS DISPONIBLES:
{info_productos}

CONVERSACIÓN ACTUAL:
{texto_conversacion_str}

{instrucciones_extra}

INSTRUCCIONES IMPORTANTES:
1. Sé amable, profesional y conocedor de agricultura
2. Si no sabes el nombre, pregúntalo amablemente al inicio
3. Adapta las respuestas al contexto agrícola boliviano
4. Si preguntan sobre productos disponibles, proporciona información precisa basada en el INVENTARIO ACTUAL
5. Incluye precios, cantidades y características cuando preguntan sobre productos
6. Mantén las respuestas naturales y conversacionales, no como listas robóticas
7. Si preguntan "hay más" o "más productos", continúa la conversación de manera natural mencionando productos adicionales
8. Incluye el saludo: "{saludo.strip()}" si corresponde
9. Responde de manera contextual, manteniendo la conversación fluida

Tu respuesta (única, conversacional, natural):
"""

    # Limpiar prompt de caracteres problemáticos antes de enviar a IA
    prompt = prompt.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    prompt = prompt.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
    prompt = prompt.replace('ñ', 'n').replace('Ñ', 'N').replace('ü', 'u').replace('Ü', 'U')
    # Convertir a ASCII puro para evitar problemas de codificación
    prompt = prompt.encode('ascii', 'ignore').decode('ascii')

    # Determinar si es primera interacción
    es_primera_interaccion = not historial.get("saludo_enviado") and len(historial["interaccion"]) == 1

    # SIEMPRE usar IA con información completa de la BD
    print(f"DEBUG - Generando respuesta IA para: '{mensaje}'")
    
    try:
        # Importar función de IA
        from .chatbot import get_openai_response

        # Construir prompt optimizado con información completa de BD
        prompt = f"""
Eres el asistente virtual inteligente de la Cooperativa Agrícola Integral. Responde de forma natural y conversacional.

MENSAJE DEL USUARIO: "{mensaje}"

INFORMACIÓN DEL PRODUCTOR:
- Nombre: {historial.get("nombre", "No proporcionado")}
- Fase: {historial.get("fase", "inicial")}
- Contexto: {historial.get("tono", "neutro")}

INVENTARIO COMPLETO Y ACTUALIZADO:
{info_productos}

CONVERSACIÓN PREVIA:
{texto_conversacion_str}

INSTRUCCIONES:
1. Responde ÚNICAMENTE con información del INVENTARIO mostrado arriba
2. Para productos específicos, da detalles exactos (precios, cantidades, características)  
3. Si preguntan "hola" o saludos, saluda naturalmente y ofrece ayuda con productos
4. Si preguntan por un producto que no existe, menciona productos similares disponibles
5. Mantén conversación natural, no como lista robótica
6. Incluye precios y cantidades reales cuando sea relevante
7. NO inventes productos que no estén en el inventario

Responde de forma natural y conversacional:
"""

        # Limpiar prompt
        prompt = prompt.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        prompt = prompt.replace('ñ', 'n').replace('Ñ', 'N')
        prompt = prompt.encode('ascii', 'ignore').decode('ascii')

        # Usar IA
        respuesta_ia = get_openai_response(prompt, referer or "https://cooperativa-agricola.com", title or "Asistente Agrícola")
        respuesta_ia = limpiar_respuesta(respuesta_ia)

        if respuesta_ia and len(respuesta_ia.strip()) > 10:
            respuesta = respuesta_ia
            print(f"DEBUG - Respuesta IA exitosa: '{respuesta}'")
        else:
            # Solo si IA falla completamente, usar BD como último recurso
            respuesta = generar_respuesta_sin_ia(mensaje, historial, info_productos)
            print(f"DEBUG - IA falló, usando BD: '{respuesta}'")

    except Exception as e:
        print(f"Error con IA: {e}")
        # Si IA no está disponible (rate limit, etc), usar respuesta inteligente de BD
        respuesta = generar_respuesta_sin_ia(mensaje, historial, info_productos)
        print(f"DEBUG - IA no disponible, usando BD: '{respuesta}'")

    # Marcar que ya se envió saludo después de primera respuesta
    if es_primera_interaccion:
        historial["saludo_enviado"] = True

    historial["respuestas_bot"].append(respuesta)

    # Agregar conversación estructurada
    historial.setdefault("conversaciones", [])
    historial["conversaciones"].append({
        "pregunta": mensaje,
        "respuesta": respuesta,
        "fase": historial.get("fase", "exploracion")
    })

    return respuesta

def detectar_pregunta_disponibilidad(mensaje, historial=None):
    """Detecta si el mensaje es una pregunta sobre disponibilidad de productos"""
    mensaje_lower = mensaje.lower()

    # Palabras clave que indican preguntas sobre disponibilidad
    indicadores_disponibilidad = [
        "tienen", "hay", "disponible", "tienen disponible", "hay disponible",
        "stock", "inventario", "queda", "quedan", "tienen en stock",
        "puedo conseguir", "puedo obtener", "venden", "ofrecen",
        "precio de", "cuánto cuesta", "cuanto cuesta", "costo de",
        "tengan", "vender", "saber sobre", "informacion sobre", "información sobre",
        "productos que", "qué productos", "que productos", "cuales tienen", "cuáles tienen",
        "indícame", "indicame", "muestrame", "muéstrame", "lista de", "catálogo",
        "disponibles", "para vender", "a la venta", "en venta", "qué tienen",
        "que tienen", "los productos", "productos disponibles",
        "estos productos", "hay mas", "hay más", "por ahora", "más productos",
        "otros productos", "productos adicionales", "resto de productos"
    ]

    # Productos agrícolas mencionados
    productos = [
        "semilla", "semillas", "pesticida", "pesticidas", "fertilizante", "fertilizantes",
        "insecticida", "insecticidas", "fungicida", "fungicidas", "herbicida", "herbicidas",
        "maiz", "maíz", "papa", "trigo", "soya", "soja", "quinoa", "tomate", "cebolla"
    ]

    # Verificar si contiene indicadores de disponibilidad
    tiene_indicador = any(indicador in mensaje_lower for indicador in indicadores_disponibilidad)

    # Verificar si contiene productos específicos O si es una pregunta de seguimiento
    tiene_producto = any(producto in mensaje_lower for producto in productos)

    # Si no tiene producto específico pero tiene indicadores, podría ser una pregunta de seguimiento
    es_pregunta_seguimiento = tiene_indicador and ("productos" in mensaje_lower or "mas" in mensaje_lower or "más" in mensaje_lower)

    # Si es una pregunta de seguimiento y tenemos historial, verificar contexto anterior
    if es_pregunta_seguimiento and historial:
        contexto_anterior = detectar_contexto_conversacion(historial)
        if contexto_anterior:
            return True

    return tiene_indicador and (tiene_producto or es_pregunta_seguimiento)

def consultar_disponibilidad_semillas(especie=None, variedad=None):
    """Consulta disponibilidad de semillas en la base de datos"""
    try:
        queryset = Semilla.objects.filter(estado='DISPONIBLE')

        if especie:
            queryset = queryset.filter(especie__icontains=especie)
        if variedad:
            queryset = queryset.filter(variedad__icontains=variedad)

        semillas = queryset.order_by('especie', 'variedad')

        resultados = []
        for semilla in semillas[:10]:  # Limitar a 10 resultados
            info = {
                'tipo': 'semilla',
                'especie': semilla.especie,
                'variedad': semilla.variedad or 'N/A',
                'cantidad': float(semilla.cantidad),
                'unidad': semilla.unidad_medida,
                'precio_unitario': float(semilla.precio_unitario) if semilla.precio_unitario else None,
                'lote': semilla.lote,
                'proveedor': semilla.proveedor,
                'fecha_vencimiento': semilla.fecha_vencimiento.strftime('%Y-%m-%d') if semilla.fecha_vencimiento else None,
                'germinacion': float(semilla.porcentaje_germinacion) if semilla.porcentaje_germinacion else None
            }
            resultados.append(info)

        return resultados

    except Exception as e:
        print(f"Error consultando semillas: {e}")
        return []

def consultar_disponibilidad_pesticidas(tipo=None, ingrediente=None):
    """Consulta disponibilidad de pesticidas en la base de datos"""
    try:
        queryset = Pesticida.objects.filter(estado='DISPONIBLE')

        if tipo:
            queryset = queryset.filter(tipo_pesticida__icontains=tipo)
        if ingrediente:
            queryset = queryset.filter(ingrediente_activo__icontains=ingrediente)

        pesticidas = queryset.order_by('tipo_pesticida', 'nombre_comercial')

        resultados = []
        for pesticida in pesticidas[:10]:  # Limitar a 10 resultados
            info = {
                'tipo': 'pesticida',
                'nombre_comercial': pesticida.nombre_comercial,
                'ingrediente_activo': pesticida.ingrediente_activo,
                'tipo_pesticida': pesticida.tipo_pesticida,
                'concentracion': pesticida.concentracion,
                'cantidad': float(pesticida.cantidad),
                'unidad': pesticida.unidad_medida,
                'precio_unitario': float(pesticida.precio_unitario),
                'lote': pesticida.lote,
                'proveedor': pesticida.proveedor,
                'fecha_vencimiento': pesticida.fecha_vencimiento.strftime('%Y-%m-%d') if pesticida.fecha_vencimiento else None,
                'dosis_recomendada': pesticida.dosis_recomendada
            }
            resultados.append(info)

        return resultados

    except Exception as e:
        print(f"Error consultando pesticidas: {e}")
        return []

def consultar_disponibilidad_fertilizantes(tipo=None, composicion=None):
    """Consulta disponibilidad de fertilizantes en la base de datos"""
    try:
        queryset = Fertilizante.objects.filter(estado='DISPONIBLE')

        if tipo:
            queryset = queryset.filter(tipo_fertilizante__icontains=tipo)
        if composicion:
            queryset = queryset.filter(composicion_npk__icontains=composicion)

        fertilizantes = queryset.order_by('tipo_fertilizante', 'nombre_comercial')

        resultados = []
        for fertilizante in fertilizantes[:10]:  # Limitar a 10 resultados
            info = {
                'tipo': 'fertilizante',
                'nombre_comercial': fertilizante.nombre_comercial,
                'tipo_fertilizante': fertilizante.tipo_fertilizante,
                'composicion_npk': fertilizante.composicion_npk,
                'cantidad': float(fertilizante.cantidad),
                'unidad': fertilizante.unidad_medida,
                'precio_unitario': float(fertilizante.precio_unitario),
                'lote': fertilizante.lote,
                'proveedor': fertilizante.proveedor,
                'fecha_vencimiento': fertilizante.fecha_vencimiento.strftime('%Y-%m-%d') if fertilizante.fecha_vencimiento else None,
                'dosis_recomendada': fertilizante.dosis_recomendada,
                'materia_organica': float(fertilizante.materia_orgánica) if fertilizante.materia_orgánica else None
            }
            resultados.append(info)

        return resultados

    except Exception as e:
        print(f"Error consultando fertilizantes: {e}")
        return []

def extraer_parametros_producto(mensaje):
    """Extrae parámetros de búsqueda de productos del mensaje"""
    mensaje_lower = mensaje.lower()

    # Extraer especie de cultivo
    especies = {
        'maiz': 'Maíz', 'maíz': 'Maíz', 'papa': 'Papa', 'trigo': 'Trigo',
        'soya': 'Soya', 'soja': 'Soya', 'quinoa': 'Quinoa', 'tomate': 'Tomate', 'cebolla': 'Cebolla'
    }

    especie_encontrada = None
    for clave, valor in especies.items():
        if clave in mensaje_lower:
            especie_encontrada = valor
            break

    # Extraer tipo de pesticida
    tipos_pesticida = {
        'insecticida': 'INSECTICIDA', 'fungicida': 'FUNGICIDA', 'herbicida': 'HERBICIDA',
        'nematicida': 'NEMATICIDA', 'acaricida': 'ACARICIDA', 'bactericida': 'BACTERICIDA'
    }

    tipo_pesticida_encontrado = None
    for clave, valor in tipos_pesticida.items():
        if clave in mensaje_lower:
            tipo_pesticida_encontrado = valor
            break

    # Extraer tipo de fertilizante
    tipos_fertilizante = {
        'organico': 'ORGANICO', 'quimico': 'QUIMICO', 'foliar': 'FOLIARES',
        'micronutriente': 'MICRONUTRIENTES', 'calcareo': 'CALCAREO'
    }

    tipo_fertilizante_encontrado = None
    for clave, valor in tipos_fertilizante.items():
        if clave in mensaje_lower:
            tipo_fertilizante_encontrado = valor
            break

    # Extraer composición NPK
    patron_npk = r'(\d+-\d+-\d+)'
    match_npk = re.search(patron_npk, mensaje)
    composicion_npk = match_npk.group(1) if match_npk else None

    return {
        'especie': especie_encontrada,
        'tipo_pesticida': tipo_pesticida_encontrado,
        'tipo_fertilizante': tipo_fertilizante_encontrado,
        'composicion_npk': composicion_npk
    }

def generar_respuesta_disponibilidad(parametros, resultados, tipo_especifico=None):
    """Genera una respuesta amigable sobre disponibilidad de productos"""
    if not resultados:
        return "Lo siento, actualmente no tenemos ese producto disponible en nuestro inventario. ¿Te gustaría que te informe sobre otros productos similares o cuándo podríamos tenerlo disponible?"

    # Verificar si se pidió un tipo específico o productos en general
    tipos_solicitados = set()
    for resultado in resultados:
        tipos_solicitados.add(resultado['tipo'])

    if len(tipos_solicitados) == 1 or tipo_especifico:
        # Un solo tipo específico - mostrar todos los productos disponibles
        respuesta = "¡Claro! Te informo sobre la disponibilidad de productos:\n\n"
        limite_por_tipo = 10  # Mostrar hasta 10 productos cuando es un tipo específico
    else:
        # Múltiples tipos - mostrar selección general
        respuesta = "¡Claro! Te muestro una selección de nuestros productos disponibles:\n\n"
        limite_por_tipo = 3  # Mostrar máximo 3 por tipo cuando son múltiples

    # Agrupar por tipo
    por_tipo = {}
    for resultado in resultados:
        tipo = resultado['tipo']
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append(resultado)

    for tipo, productos in por_tipo.items():
        if tipo == 'semilla':
            respuesta += f"🌱 **SEMILLAS DISPONIBLES** ({len(productos)} variedades):\n"
            for prod in productos[:limite_por_tipo]:
                precio_info = f" - Bs. {prod['precio_unitario']:.2f}/{prod['unidad']}" if prod['precio_unitario'] else ""
                germinacion_info = f" - Germinación: {prod['germinacion']}%" if prod['germinacion'] else ""
                respuesta += f"• {prod['especie']} {prod['variedad']} - {prod['cantidad']} {prod['unidad']}{precio_info}{germinacion_info}\n"
        elif tipo == 'pesticida':
            respuesta += f"🧪 **PESTICIDAS DISPONIBLES** ({len(productos)} productos):\n"
            for prod in productos[:limite_por_tipo]:
                respuesta += f"• {prod['nombre_comercial']} ({prod['tipo_pesticida']}) - {prod['cantidad']} {prod['unidad']} - Bs. {prod['precio_unitario']:.2f}/{prod['unidad']}\n"
        elif tipo == 'fertilizante':
            respuesta += f"🌿 **FERTILIZANTES DISPONIBLES** ({len(productos)} productos):\n"
            for prod in productos[:limite_por_tipo]:
                respuesta += f"• {prod['nombre_comercial']} (NPK: {prod['composicion_npk']}) - {prod['cantidad']} {prod['unidad']} - Bs. {prod['precio_unitario']:.2f}/{prod['unidad']}\n"

        if len(productos) > limite_por_tipo:
            respuesta += f"... y {len(productos) - limite_por_tipo} productos más disponibles.\n"

        respuesta += "\n"

    respuesta += "Todos los precios incluyen IVA. ¿Te gustaría más información sobre algún producto específico o saber sobre condiciones de venta?"

    return respuesta

def obtener_informacion_productos():
    """Obtiene información actual de productos disponibles para el contexto del chatbot"""
    try:
        info = []

        # Semillas disponibles - mostrar todas
        semillas = Semilla.objects.filter(estado='DISPONIBLE').order_by('especie')
        if semillas:
            info.append("SEMILLAS DISPONIBLES:")
            for semilla in semillas:
                precio = f"Bs. {semilla.precio_unitario}" if semilla.precio_unitario else "Precio no disponible"
                info.append(f"- {semilla.especie} {semilla.variedad or 'N/A'}: {semilla.cantidad} {semilla.unidad_medida} a {precio}")
            info.append("")

        # Pesticidas disponibles - mostrar todos
        pesticidas = Pesticida.objects.filter(estado='DISPONIBLE').order_by('tipo_pesticida', 'nombre_comercial')
        if pesticidas:
            info.append("PESTICIDAS DISPONIBLES:")
            for pesticida in pesticidas:
                info.append(f"- {pesticida.nombre_comercial} ({pesticida.tipo_pesticida}): {pesticida.cantidad} {pesticida.unidad_medida} a Bs. {pesticida.precio_unitario}")
            info.append("")

        # Fertilizantes disponibles - mostrar todos
        fertilizantes = Fertilizante.objects.filter(estado='DISPONIBLE').order_by('tipo_fertilizante', 'nombre_comercial')
        if fertilizantes:
            info.append("FERTILIZANTES DISPONIBLES:")
            for fertilizante in fertilizantes:
                info.append(f"- {fertilizante.nombre_comercial} (NPK: {fertilizante.composicion_npk}): {fertilizante.cantidad} {fertilizante.unidad_medida} a Bs. {fertilizante.precio_unitario}")
            info.append("")

        if not info:
            return "Actualmente tenemos semillas, pesticidas y fertilizantes disponibles. Consulta nuestro inventario para detalles especificos."

        # Unir todo y asegurar codificación ASCII segura
        resultado = "\n".join(info)
        # Reemplazar caracteres acentuados por versiones sin acento para evitar problemas de codificación
        resultado = resultado.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        resultado = resultado.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
        resultado = resultado.replace('ñ', 'n').replace('Ñ', 'N')

        return resultado

    except Exception as e:
        print(f"Error obteniendo información de productos: {e}")
        return "Informacion de productos disponible en nuestro inventario. Puedo ayudarte a consultar detalles especificos."

def detectar_contexto_conversacion(historial):
    """Detecta el contexto de la conversación anterior para preguntas de seguimiento"""
    if not historial or not historial.get("conversaciones"):
        return None

    # Revisar las últimas conversaciones para encontrar menciones de productos
    for conversacion in reversed(historial["conversaciones"][-3:]):  # Últimas 3 conversaciones
        respuesta = conversacion.get("respuesta", "").lower()

        # Buscar menciones específicas de tipos de productos en las respuestas anteriores
        if "pesticidas disponibles" in respuesta or "pesticida" in respuesta:
            return "pesticida"
        elif "semillas disponibles" in respuesta or "semilla" in respuesta:
            return "semilla"
        elif "fertilizantes disponibles" in respuesta or "fertilizante" in respuesta:
            return "fertilizante"

    return None

def generar_respuesta_sin_ia(mensaje, historial, info_productos):
    """Genera respuesta inteligente basada en BD cuando IA no está disponible"""
    mensaje_lower = mensaje.lower().strip()
    
    # Detectar tipo de consulta
    es_saludo = any(saludo in mensaje_lower for saludo in ['hola', 'buenos dias', 'buenas tardes', 'buenas noches', 'muy buenas', 'hello', 'hi', 'hey'])
    
    if es_saludo:
        # Saludo personalizado con información de productos
        try:
            num_semillas = Semilla.objects.filter(estado='DISPONIBLE').count()
            num_pesticidas = Pesticida.objects.filter(estado='DISPONIBLE').count() 
            num_fertilizantes = Fertilizante.objects.filter(estado='DISPONIBLE').count()
            
            nombre = historial.get("nombre", "")
            saludo_nombre = f"¡Hola {nombre}!" if nombre else "¡Hola!"
            
            respuesta = f"{saludo_nombre} Soy tu asistente agrícola de la Cooperativa. "
            respuesta += f"Tenemos {num_semillas} tipos de semillas, {num_pesticidas} pesticidas y {num_fertilizantes} fertilizantes disponibles. "
            respuesta += "¿En qué puedo ayudarte hoy?"
            
            return respuesta
        except:
            return "¡Hola! Soy tu asistente agrícola. ¿En qué puedo ayudarte con nuestros productos?"
    
    # Detectar preguntas sobre productos específicos
    elif any(palabra in mensaje_lower for palabra in ["pesticidas", "pesticida", "insecticidas", "fungicidas", "herbicidas"]):
        try:
            pesticidas = Pesticida.objects.filter(estado='DISPONIBLE').order_by('tipo_pesticida', 'nombre_comercial')[:5]
            if pesticidas:
                respuesta = "Te muestro nuestros pesticidas disponibles:\n\n"
                for pesticida in pesticidas:
                    respuesta += f"• {pesticida.nombre_comercial} ({pesticida.tipo_pesticida}) - {pesticida.cantidad} {pesticida.unidad_medida} - Bs. {pesticida.precio_unitario:.2f}\n"
                respuesta += f"\nTenemos más productos disponibles. ¿Te interesa algún pesticida específico?"
                return respuesta
            else:
                return "Actualmente no tenemos pesticidas disponibles en inventario."
        except:
            return "Puedo ayudarte con información sobre pesticidas. ¿Qué tipo de pesticida necesitas?"
    
    elif any(palabra in mensaje_lower for palabra in ["semillas", "semilla", "siembra"]):
        try:
            semillas = Semilla.objects.filter(estado='DISPONIBLE').order_by('especie')[:5]
            if semillas:
                respuesta = "Te muestro nuestras semillas disponibles:\n\n"
                for semilla in semillas:
                    precio = f"Bs. {semilla.precio_unitario:.2f}" if semilla.precio_unitario else "Consultar precio"
                    respuesta += f"• {semilla.especie} {semilla.variedad or ''} - {semilla.cantidad} {semilla.unidad_medida} - {precio}\n"
                respuesta += f"\nTenemos más variedades disponibles. ¿Te interesa alguna semilla específica?"
                return respuesta
            else:
                return "Actualmente no tenemos semillas disponibles en inventario."
        except:
            return "Puedo ayudarte con información sobre semillas. ¿Qué tipo de semilla necesitas?"
    
    elif any(palabra in mensaje_lower for palabra in ["fertilizantes", "fertilizante", "abonos"]):
        try:
            fertilizantes = Fertilizante.objects.filter(estado='DISPONIBLE').order_by('tipo_fertilizante', 'nombre_comercial')[:5]
            if fertilizantes:
                respuesta = "Te muestro nuestros fertilizantes disponibles:\n\n"
                for fertilizante in fertilizantes:
                    respuesta += f"• {fertilizante.nombre_comercial} (NPK: {fertilizante.composicion_npk}) - {fertilizante.cantidad} {fertilizante.unidad_medida} - Bs. {fertilizante.precio_unitario:.2f}\n"
                respuesta += f"\nTenemos más productos disponibles. ¿Te interesa algún fertilizante específico?"
                return respuesta
            else:
                return "Actualmente no tenemos fertilizantes disponibles en inventario."
        except:
            return "Puedo ayudarte con información sobre fertilizantes. ¿Qué tipo de fertilizante necesitas?"
    
    elif any(palabra in mensaje_lower for palabra in ["productos", "product", "ofrecen", "tienen", "disponible", "inventario", "catalogo", "catálogo"]):
        try:
            num_semillas = Semilla.objects.filter(estado='DISPONIBLE').count()
            num_pesticidas = Pesticida.objects.filter(estado='DISPONIBLE').count()
            num_fertilizantes = Fertilizante.objects.filter(estado='DISPONIBLE').count()
            
            respuesta = "¡Claro! Tenemos estos productos disponibles:\n\n"
            respuesta += f"🌱 SEMILLAS: {num_semillas} variedades\n"
            respuesta += f"🧪 PESTICIDAS: {num_pesticidas} productos\n" 
            respuesta += f"🌿 FERTILIZANTES: {num_fertilizantes} productos\n\n"
            respuesta += "¿Sobre qué tipo de producto te gustaría más información?"
            return respuesta
        except:
            return "Tenemos semillas, pesticidas y fertilizantes disponibles. ¿Qué tipo de producto te interesa?"
    
    # Buscar productos específicos mencionados
    else:
        try:
            # Buscar producto específico por nombre
            productos_encontrados = []
            
            # Buscar en pesticidas
            for pesticida in Pesticida.objects.filter(estado='DISPONIBLE'):
                if pesticida.nombre_comercial.lower() in mensaje_lower:
                    productos_encontrados.append({
                        'tipo': 'pesticida',
                        'nombre': pesticida.nombre_comercial,
                        'detalles': f"Tipo: {pesticida.tipo_pesticida}, Ingrediente: {pesticida.ingrediente_activo}, Precio: Bs. {pesticida.precio_unitario:.2f}/{pesticida.unidad_medida}, Disponible: {pesticida.cantidad} {pesticida.unidad_medida}"
                    })
            
            # Buscar en semillas
            for semilla in Semilla.objects.filter(estado='DISPONIBLE'):
                if semilla.especie.lower() in mensaje_lower or (semilla.variedad and semilla.variedad.lower() in mensaje_lower):
                    precio = f"Bs. {semilla.precio_unitario:.2f}" if semilla.precio_unitario else "Consultar precio"
                    productos_encontrados.append({
                        'tipo': 'semilla',
                        'nombre': f"{semilla.especie} {semilla.variedad or ''}".strip(),
                        'detalles': f"Disponible: {semilla.cantidad} {semilla.unidad_medida}, Precio: {precio}/{semilla.unidad_medida}"
                    })
            
            # Buscar en fertilizantes
            for fertilizante in Fertilizante.objects.filter(estado='DISPONIBLE'):
                if fertilizante.nombre_comercial.lower() in mensaje_lower:
                    productos_encontrados.append({
                        'tipo': 'fertilizante', 
                        'nombre': fertilizante.nombre_comercial,
                        'detalles': f"NPK: {fertilizante.composicion_npk}, Precio: Bs. {fertilizante.precio_unitario:.2f}/{fertilizante.unidad_medida}, Disponible: {fertilizante.cantidad} {fertilizante.unidad_medida}"
                    })
            
            if productos_encontrados:
                respuesta = f"Encontré información sobre estos productos:\n\n"
                for producto in productos_encontrados[:3]:  # Mostrar máximo 3
                    respuesta += f"• **{producto['nombre']}** ({producto['tipo']})\n  {producto['detalles']}\n\n"
                respuesta += "¿Te gustaría más información sobre alguno de estos productos?"
                return respuesta
            
        except:
            pass
    
    # Respuesta por defecto inteligente
    return f"Entiendo tu consulta sobre '{mensaje}'. Puedo ayudarte con información sobre nuestras semillas, pesticidas y fertilizantes disponibles. ¿Podrías ser más específico sobre qué producto te interesa?"
