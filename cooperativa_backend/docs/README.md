# 📚 Documentación del Sistema de Gestión Cooperativa Agrícola

## 📋 Índice General

Esta documentación está organizada por **Casos de Uso (CU)** implementados en el sistema. Cada CU contiene documentación detallada de sus tareas específicas, implementación técnica, endpoints API, validaciones y ejemplos de uso.

## 🗂️ Estructura de Documentación

```
docs/
├── README.md                           # Este archivo (índice general)
├── API_Documentation.md               # Documentación completa de API
├── IMPLEMENTATION_SUMMARY.md          # Resumen ejecutivo del proyecto
│
├── CU1_Autenticacion/
│   ├── README.md                      # Documentación completa CU1
│   ├── T011_Autenticacion_Sesiones.md # Gestión de autenticación
│   ├── T013_Bitacora_Basica.md        # Bitácora básica
│   ├── T020_Interfaces_Login.md       # Diseño de interfaces
│   ├── T023_Cierre_Sesion.md          # Implementación logout
│   └── T026_Vistas_Moviles.md         # Vistas móviles
│
├── CU2_Logout_Sesion/
│   ├── README.md                      # Documentación completa CU2
│   ├── T011_Autenticacion_Sesiones.md # Gestión de sesiones
│   ├── T023_Cierre_Sesion.md          # Logout web/móvil
│   └── T030_Bitacora_Extendida.md     # Bitácora extendida
│
├── CU3_Gestion_Socios/
│   ├── README.md                      # Documentación completa CU3
│   ├── T012_Gestion_Usuarios_Roles.md # Gestión usuarios/roles
│   ├── T014_CRUD_Socios.md            # CRUD de socios
│   ├── T016_Busquedas_Filtros.md      # Búsquedas y filtros
│   ├── T021_Validacion_Formularios.md # Validaciones
│   ├── T024_Vistas_Usuarios_Roles.md  # Interfaces web
│   ├── T025_Vistas_Socios_Parcelas.md # Interfaces web
│   ├── T027_Validacion_Duplicados.md  # Validación duplicados
│   ├── T029_Busqueda_Avanzada.md      # Búsqueda avanzada
│   └── T031_Reportes_Usuarios.md      # Reportes usuarios
│
├── CU4_Gestion_Parcelas/
│   ├── README.md                      # Documentación completa CU4
│   ├── T015_Registro_Parcelas.md      # Registro de parcelas
│   ├── T021_Validacion_Datos.md       # Validaciones
│   ├── T025_Vistas_Parcelas.md        # Interfaces web
│   └── T034_Documentacion_Tecnica.md  # Documentación técnica
│
├── CU5_Consultas_Filtros/
│   ├── README.md                      # Documentación completa CU5
│   ├── T016_Busquedas_Filtros.md      # Búsquedas y filtros
│   ├── T026_Vistas_Moviles.md         # Vistas móviles
│   ├── T029_Busqueda_Avanzada.md      # Búsqueda avanzada
│   └── T031_Reportes_Basicos.md       # Reportes básicos
│
├── CU6_Roles_Permisos/
│   ├── README.md                      # Documentación completa CU6
│   ├── T012_Gestion_Usuarios_Roles.md # Gestión usuarios/roles
│   ├── T022_Configuracion_Roles.md    # Configuración inicial
│   ├── T024_Vistas_Gestion.md         # Interfaces web
│   └── T034_Documentacion_API.md      # Documentación API
│
└── Sistema_Pagos/                     # 💰 NUEVO: Sistema de Pagos
    ├── SISTEMA_PAGOS_README.md        # Resumen ejecutivo completo
    ├── SISTEMA_PAGOS_API.md           # Documentación API detallada
    ├── SISTEMA_PAGOS_FRONTEND_EJEMPLOS.md  # Código React/Vue
    ├── SISTEMA_PAGOS_GUIA_RAPIDA.md   # Guía rápida de uso
    └── SISTEMA_PAGOS_PRUEBAS_API.md   # Colección Postman/cURL
```

## 🎯 Casos de Uso Implementados

### **CU1: Iniciar Sesión (Web/Móvil)**
**Ubicación:** `CU1_Autenticacion/`  
**Estado:** ✅ Completado  
**Descripción:** Sistema completo de autenticación con validaciones, bloqueo por intentos fallidos y auditoría básica.

### **CU2: Cerrar Sesión (Web/Móvil)**
**Ubicación:** `CU2_Logout_Sesion/`  
**Estado:** ✅ Completado  
**Descripción:** Gestión avanzada de sesiones con logout seguro, invalidación de sesiones y bitácora extendida.

### **CU3: Gestionar Socios (Alta, Edición, Inhabilitar/Reactivar)**
**Ubicación:** `CU3_Gestion_Socios/`  
**Estado:** ✅ Completado  
**Descripción:** CRUD completo de socios con validaciones robustas, búsquedas avanzadas y reportes.

### **CU4: Gestionar Parcelas por Socio**
**Ubicación:** `CU4_Gestion_Parcelas/`  
**Estado:** ✅ Completado  
**Descripción:** Gestión completa de parcelas con validaciones de superficie, coordenadas y documentación técnica.

### **CU5: Consultar Socios y Parcelas con Filtros (Web/Móvil)**
**Ubicación:** `CU5_Consultas_Filtros/`  
**Estado:** ✅ Completado  
**Descripción:** Sistema avanzado de consultas con filtros múltiples, vistas móviles y reportes básicos.

### **CU6: Gestionar Roles y Permisos**
**Ubicación:** `CU6_Roles_Permisos/`  
**Estado:** ✅ Completado  
**Descripción:** Sistema completo de roles y permisos con configuración inicial y documentación API.

### **💰 Sistema de Pagos (NUEVO - Nov 2025)**
**Ubicación:** `docs/SISTEMA_PAGOS_*.md`  
**Estado:** ✅ Completado - Listo para migrar  
**Descripción:** Sistema completo de gestión de pagos y pedidos con integración Stripe, múltiples métodos de pago, historial de ventas con filtros avanzados y exportación CSV.

**Características principales:**
- ✅ Gestión de pedidos/órdenes de venta
- ✅ Pagos en efectivo, transferencia, Stripe, QR
- ✅ Pagos parciales y múltiples pagos por pedido
- ✅ Integración completa con Stripe (tarjetas)
- ✅ Reembolsos automáticos
- ✅ Historial de ventas con filtros
- ✅ Exportación a CSV
- ✅ Auditoría completa en bitácora

**Documentos disponibles:**
- `SISTEMA_PAGOS_README.md` - Resumen ejecutivo y checklist
- `SISTEMA_PAGOS_API.md` - Documentación API completa (endpoints, modelos, ejemplos)
- `SISTEMA_PAGOS_FRONTEND_EJEMPLOS.md` - Código React/Vue completo
- `SISTEMA_PAGOS_GUIA_RAPIDA.md` - Guía rápida de uso
- `SISTEMA_PAGOS_PRUEBAS_API.md` - Colección Postman/cURL

## 📊 Métricas del Sistema

- **✅ 6 Casos de Uso** completamente implementados
- **✅ Sistema de Pagos** completo con Stripe
- **✅ 160 Tests** automatizados pasando
- **✅ 60+ Endpoints** API funcionales (10+ nuevos del sistema de pagos)
- **✅ 18+ Modelos** de datos validados (3 nuevos: Pedido, DetallePedido, Pago)
- **✅ Documentación completa** por CU y tarea
- **✅ Integración Stripe** para pagos en línea

## 🚀 Inicio Rápido

Para comenzar a explorar la documentación:

1. **Visión General:** `IMPLEMENTATION_SUMMARY.md`
2. **API Completa:** `API_Documentation.md`
3. **Sistema de Pagos:** `SISTEMA_PAGOS_GUIA_RAPIDA.md` ⭐ NUEVO
4. **Por CU específico:** Navegar a la carpeta correspondiente

### 💰 Empezar con Sistema de Pagos

⚠️ **IMPORTANTE PARA FRONTEND:** Lee primero **`SISTEMA_PAGOS_GUIA_FRONTEND.md`** 🎯

Esta guía explica:
- ✅ **El flujo real:** Socios → Cooperativa vende → Cliente paga
- ✅ **Quién hace qué:** Admin usa Django Admin, Socio usa React
- ✅ **Componentes React completos** con Vite + Axios
- ✅ **Ejemplos de código listos** para copiar y pegar
- ✅ **Permisos y restricciones** bien explicados

```bash
# 1. Instalar Stripe
pip install stripe==11.2.0

# 2. Configurar .env (crear archivo)
STRIPE_PUBLIC_KEY=pk_test_xxxxx
STRIPE_SECRET_KEY=sk_test_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx

# 3. Crear migraciones
python manage.py makemigrations
python manage.py migrate

# 4. Ver documentación en orden (FRONTEND):
# 🎯 1️⃣ LEER PRIMERO: docs/SISTEMA_PAGOS_GUIA_FRONTEND.md ⭐⭐⭐
# 📋 2️⃣ Referencia de campos: docs/SISTEMA_PAGOS_CAMBIOS_IMPORTANTES.md
# 📖 3️⃣ API completa: docs/SISTEMA_PAGOS_API.md
# 💻 4️⃣ Ejemplos adicionales: docs/SISTEMA_PAGOS_FRONTEND_EJEMPLOS.md
```

**📌 Diferencia de Roles:**
- **ADMINISTRADOR** → Django Admin (`/admin/`) → Registra ventas y pagos
- **SOCIO** → React App (Vite + Axios) → Consulta ventas de SUS productos

**📌 Campos importantes actualizados:**
- ✅ Usar `subtotal`, `impuestos`, `descuento`, `total` (NO `monto_*`)
- ✅ Usar `producto_cosechado` (NO `producto` ni `producto_id`)
- ✅ Usar `observaciones` (NO `notas`)
- ✅ Usar `referencia_bancaria` y `comprobante_archivo`

Ver detalles completos en: **`SISTEMA_PAGOS_CAMBIOS_IMPORTANTES.md`** 🔴

## 📞 Contacto y Soporte

- **API Base:** `http://localhost:8000/api/`
- **Admin Panel:** `http://localhost:8000/admin/`
- **Tests:** `python manage.py test`
- **Documentación:** `docs/` directory

---

**📅 Última actualización:** Noviembre 2025  
**🎯 Estado del proyecto:** Completado con Sistema de Pagos ✅  
**💰 Nuevo:** Sistema de Pagos con Stripe completamente funcional</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\proyecto_Final\Backend_Django\cooperativa_backend\docs\README.md