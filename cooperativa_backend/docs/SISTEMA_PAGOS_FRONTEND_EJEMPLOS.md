# Sistema de Pagos - Ejemplos Frontend

**Fecha:** Noviembre 2025  
**Versión:** 1.0  

Este documento contiene ejemplos prácticos de código para integrar el sistema de pagos en el frontend.

---

## 📋 Tabla de Contenido

1. [Configuración Inicial](#configuración-inicial)
2. [Servicio API (JavaScript Vanilla)](#servicio-api-javascript-vanilla)
3. [Componentes React](#componentes-react)
4. [Componentes Vue](#componentes-vue)
5. [Integración Stripe](#integración-stripe)

---

## ⚙️ Configuración Inicial

### Instalar Dependencias

```bash
# Stripe para pagos con tarjeta
npm install @stripe/stripe-js

# Axios para peticiones HTTP (opcional)
npm install axios

# date-fns para manejo de fechas (opcional)
npm install date-fns
```

### Variables de Entorno

Crear archivo `.env` en el frontend:

```env
# API Backend
VITE_API_URL=http://localhost:8000/api
REACT_APP_API_URL=http://localhost:8000/api

# Stripe
VITE_STRIPE_PUBLIC_KEY=pk_test_51xxxxxxxxxxxxx
REACT_APP_STRIPE_PUBLIC_KEY=pk_test_51xxxxxxxxxxxxx
```

---

## 🔧 Servicio API (JavaScript Vanilla)

### api/pagosService.js

```javascript
// Configuración base
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

// Helper para obtener token
const getAuthToken = () => {
  return localStorage.getItem('token');
};

// Helper para headers con autenticación
const getHeaders = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : ''
  };
};

// Servicio de Pedidos
export const pedidosService = {
  // Listar pedidos con filtros
  listar: async (filtros = {}) => {
    const params = new URLSearchParams();
    
    if (filtros.socio_id) params.append('socio_id', filtros.socio_id);
    if (filtros.estado) params.append('estado', filtros.estado);
    if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde);
    if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta);
    if (filtros.cliente_nombre) params.append('cliente_nombre', filtros.cliente_nombre);
    if (filtros.page) params.append('page', filtros.page);
    if (filtros.page_size) params.append('page_size', filtros.page_size);
    
    const response = await fetch(`${API_URL}/pedidos/?${params}`, {
      headers: getHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Error al obtener pedidos');
    }
    
    return response.json();
  },

  // Obtener detalle de pedido
  obtener: async (id) => {
    const response = await fetch(`${API_URL}/pedidos/${id}/`, {
      headers: getHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Error al obtener pedido');
    }
    
    return response.json();
  },

  // Crear pedido
  crear: async (datos) => {
    const response = await fetch(`${API_URL}/pedidos/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(datos)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw error;
    }
    
    return response.json();
  },

  // Actualizar pedido
  actualizar: async (id, datos) => {
    const response = await fetch(`${API_URL}/pedidos/${id}/`, {
      method: 'PATCH',
      headers: getHeaders(),
      body: JSON.stringify(datos)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw error;
    }
    
    return response.json();
  },

  // Cambiar estado de pedido
  cambiarEstado: async (id, nuevoEstado) => {
    const response = await fetch(`${API_URL}/pedidos/${id}/cambiar_estado/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ estado: nuevoEstado })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw error;
    }
    
    return response.json();
  }
};

// Servicio de Pagos
export const pagosService = {
  // Listar pagos
  listar: async (filtros = {}) => {
    const params = new URLSearchParams();
    
    if (filtros.pedido_id) params.append('pedido_id', filtros.pedido_id);
    if (filtros.estado) params.append('estado', filtros.estado);
    if (filtros.metodo_pago) params.append('metodo_pago', filtros.metodo_pago);
    if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde);
    if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta);
    if (filtros.page) params.append('page', filtros.page);
    
    const response = await fetch(`${API_URL}/pagos/?${params}`, {
      headers: getHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Error al obtener pagos');
    }
    
    return response.json();
  },

  // Registrar pago (efectivo/transferencia)
  registrar: async (datos) => {
    const response = await fetch(`${API_URL}/pagos/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(datos)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw error;
    }
    
    return response.json();
  },

  // Pagar con Stripe
  pagarConStripe: async (datos) => {
    const response = await fetch(`${API_URL}/pagos/pagar_con_stripe/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(datos)
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw error;
    }
    
    return response.json();
  },

  // Reembolsar pago
  reembolsar: async (id, motivo) => {
    const response = await fetch(`${API_URL}/pagos/${id}/reembolsar/`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ motivo })
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw error;
    }
    
    return response.json();
  }
};

// Servicio de Historial
export const historialService = {
  // Obtener historial de ventas
  obtenerHistorial: async (filtros = {}) => {
    const params = new URLSearchParams();
    
    if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde);
    if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta);
    if (filtros.cliente_nombre) params.append('cliente_nombre', filtros.cliente_nombre);
    if (filtros.socio_id) params.append('socio_id', filtros.socio_id);
    if (filtros.estado_pedido) params.append('estado_pedido', filtros.estado_pedido);
    if (filtros.metodo_pago) params.append('metodo_pago', filtros.metodo_pago);
    if (filtros.page) params.append('page', filtros.page);
    if (filtros.page_size) params.append('page_size', filtros.page_size);
    
    const response = await fetch(`${API_URL}/historial-ventas/?${params}`, {
      headers: getHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Error al obtener historial');
    }
    
    return response.json();
  },

  // Exportar a CSV
  exportarCSV: async (filtros = {}) => {
    const params = new URLSearchParams();
    
    if (filtros.fecha_desde) params.append('fecha_desde', filtros.fecha_desde);
    if (filtros.fecha_hasta) params.append('fecha_hasta', filtros.fecha_hasta);
    if (filtros.cliente_nombre) params.append('cliente_nombre', filtros.cliente_nombre);
    if (filtros.socio_id) params.append('socio_id', filtros.socio_id);
    if (filtros.estado_pedido) params.append('estado_pedido', filtros.estado_pedido);
    if (filtros.metodo_pago) params.append('metodo_pago', filtros.metodo_pago);
    
    const response = await fetch(`${API_URL}/exportar-ventas-csv/?${params}`, {
      headers: getHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Error al exportar CSV');
    }
    
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `ventas_${new Date().getTime()}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
};
```

---

## ⚛️ Componentes React

### 1. Lista de Pedidos

```jsx
// components/Pedidos/ListaPedidos.jsx
import React, { useState, useEffect } from 'react';
import { pedidosService } from '../../api/pagosService';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const ListaPedidos = () => {
  const [pedidos, setPedidos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filtros, setFiltros] = useState({
    estado: '',
    fecha_desde: '',
    fecha_hasta: '',
    cliente_nombre: '',
    page: 1
  });
  const [estadisticas, setEstadisticas] = useState({
    count: 0,
    total_pages: 0
  });

  useEffect(() => {
    cargarPedidos();
  }, [filtros]);

  const cargarPedidos = async () => {
    try {
      setLoading(true);
      const data = await pedidosService.listar(filtros);
      setPedidos(data.results);
      setEstadisticas({
        count: data.count,
        total_pages: data.total_pages || Math.ceil(data.count / 20)
      });
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFiltroChange = (e) => {
    const { name, value } = e.target;
    setFiltros(prev => ({
      ...prev,
      [name]: value,
      page: 1 // Resetear a página 1 cuando cambia filtro
    }));
  };

  const cambiarPagina = (nuevaPagina) => {
    setFiltros(prev => ({ ...prev, page: nuevaPagina }));
  };

  const getEstadoBadgeClass = (estado) => {
    const clases = {
      'PENDIENTE': 'badge-warning',
      'CONFIRMADO': 'badge-info',
      'EN_PROCESO': 'badge-primary',
      'COMPLETADO': 'badge-success',
      'CANCELADO': 'badge-danger'
    };
    return clases[estado] || 'badge-secondary';
  };

  const getEstadoPagoBadgeClass = (estadoPago) => {
    const clases = {
      'PENDIENTE': 'badge-danger',
      'PARCIAL': 'badge-warning',
      'PAGADO': 'badge-success'
    };
    return clases[estadoPago] || 'badge-secondary';
  };

  if (loading) {
    return (
      <div className="d-flex justify-content-center p-5">
        <div className="spinner-border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>Pedidos</h2>
        <button 
          className="btn btn-primary"
          onClick={() => window.location.href = '/pedidos/nuevo'}
        >
          <i className="bi bi-plus-circle"></i> Nuevo Pedido
        </button>
      </div>

      {/* Filtros */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="row g-3">
            <div className="col-md-3">
              <label className="form-label">Estado</label>
              <select 
                className="form-select"
                name="estado"
                value={filtros.estado}
                onChange={handleFiltroChange}
              >
                <option value="">Todos</option>
                <option value="PENDIENTE">Pendiente</option>
                <option value="CONFIRMADO">Confirmado</option>
                <option value="EN_PROCESO">En Proceso</option>
                <option value="COMPLETADO">Completado</option>
                <option value="CANCELADO">Cancelado</option>
              </select>
            </div>
            
            <div className="col-md-3">
              <label className="form-label">Desde</label>
              <input 
                type="date"
                className="form-control"
                name="fecha_desde"
                value={filtros.fecha_desde}
                onChange={handleFiltroChange}
              />
            </div>
            
            <div className="col-md-3">
              <label className="form-label">Hasta</label>
              <input 
                type="date"
                className="form-control"
                name="fecha_hasta"
                value={filtros.fecha_hasta}
                onChange={handleFiltroChange}
              />
            </div>
            
            <div className="col-md-3">
              <label className="form-label">Cliente</label>
              <input 
                type="text"
                className="form-control"
                name="cliente_nombre"
                placeholder="Nombre del cliente"
                value={filtros.cliente_nombre}
                onChange={handleFiltroChange}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Mensajes */}
      {error && (
        <div className="alert alert-danger" role="alert">
          {error}
        </div>
      )}

      {/* Tabla */}
      <div className="card">
        <div className="card-body">
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>N° Pedido</th>
                  <th>Fecha</th>
                  <th>Cliente</th>
                  <th>Total</th>
                  <th>Pagado</th>
                  <th>Pendiente</th>
                  <th>Estado</th>
                  <th>Pago</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {pedidos.map(pedido => (
                  <tr key={pedido.id}>
                    <td>
                      <strong>{pedido.numero_pedido}</strong>
                    </td>
                    <td>
                      {format(new Date(pedido.fecha_pedido), 'dd/MM/yyyy HH:mm', { locale: es })}
                    </td>
                    <td>{pedido.cliente_nombre}</td>
                    <td>Bs. {parseFloat(pedido.total).toFixed(2)}</td>
                    <td>Bs. {parseFloat(pedido.total_pagado).toFixed(2)}</td>
                    <td>Bs. {parseFloat(pedido.saldo_pendiente).toFixed(2)}</td>
                    <td>
                      <span className={`badge ${getEstadoBadgeClass(pedido.estado)}`}>
                        {pedido.estado}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${getEstadoPagoBadgeClass(pedido.estado_pago)}`}>
                        {pedido.estado_pago}
                      </span>
                    </td>
                    <td>
                      <button 
                        className="btn btn-sm btn-outline-primary me-1"
                        onClick={() => window.location.href = `/pedidos/${pedido.id}`}
                      >
                        <i className="bi bi-eye"></i>
                      </button>
                      {pedido.saldo_pendiente > 0 && pedido.estado !== 'CANCELADO' && (
                        <button 
                          className="btn btn-sm btn-outline-success"
                          onClick={() => window.location.href = `/pagos/nuevo?pedido_id=${pedido.id}`}
                        >
                          <i className="bi bi-cash"></i>
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Paginación */}
          {estadisticas.total_pages > 1 && (
            <nav className="mt-3">
              <ul className="pagination justify-content-center">
                <li className={`page-item ${filtros.page === 1 ? 'disabled' : ''}`}>
                  <button 
                    className="page-link"
                    onClick={() => cambiarPagina(filtros.page - 1)}
                    disabled={filtros.page === 1}
                  >
                    Anterior
                  </button>
                </li>
                
                {[...Array(estadisticas.total_pages)].map((_, i) => (
                  <li 
                    key={i + 1} 
                    className={`page-item ${filtros.page === i + 1 ? 'active' : ''}`}
                  >
                    <button 
                      className="page-link"
                      onClick={() => cambiarPagina(i + 1)}
                    >
                      {i + 1}
                    </button>
                  </li>
                ))}
                
                <li className={`page-item ${filtros.page === estadisticas.total_pages ? 'disabled' : ''}`}>
                  <button 
                    className="page-link"
                    onClick={() => cambiarPagina(filtros.page + 1)}
                    disabled={filtros.page === estadisticas.total_pages}
                  >
                    Siguiente
                  </button>
                </li>
              </ul>
            </nav>
          )}

          <div className="text-center text-muted mt-2">
            Mostrando {pedidos.length} de {estadisticas.count} pedidos
          </div>
        </div>
      </div>
    </div>
  );
};

export default ListaPedidos;
```

### 2. Formulario de Crear Pedido

```jsx
// components/Pedidos/FormularioPedido.jsx
import React, { useState } from 'react';
import { pedidosService } from '../../api/pagosService';

const FormularioPedido = () => {
  const [formData, setFormData] = useState({
    socio_id: '',
    cliente_nombre: '',
    cliente_email: '',
    cliente_telefono: '',
    impuestos: '0.00',
    descuento: '0.00',
    notas: ''
  });

  const [items, setItems] = useState([
    { producto_id: '', cantidad: '', precio_unitario: '' }
  ]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleItemChange = (index, field, value) => {
    const nuevosItems = [...items];
    nuevosItems[index][field] = value;
    setItems(nuevosItems);
  };

  const agregarItem = () => {
    setItems([...items, { producto_id: '', cantidad: '', precio_unitario: '' }]);
  };

  const eliminarItem = (index) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const calcularSubtotal = (item) => {
    const cantidad = parseFloat(item.cantidad) || 0;
    const precio = parseFloat(item.precio_unitario) || 0;
    return cantidad * precio;
  };

  const calcularTotales = () => {
    const subtotal = items.reduce((sum, item) => sum + calcularSubtotal(item), 0);
    const impuestos = parseFloat(formData.impuestos) || 0;
    const descuento = parseFloat(formData.descuento) || 0;
    const total = subtotal + impuestos - descuento;

    return { subtotal, impuestos, descuento, total };
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      setLoading(true);
      setError(null);

      const datos = {
        ...formData,
        items: items.filter(item => 
          item.producto_id && item.cantidad && item.precio_unitario
        )
      };

      if (datos.items.length === 0) {
        throw new Error('Debe agregar al menos un producto');
      }

      const resultado = await pedidosService.crear(datos);
      
      setSuccess(true);
      setTimeout(() => {
        window.location.href = `/pedidos/${resultado.id}`;
      }, 1500);
      
    } catch (err) {
      setError(err.error || err.message || 'Error al crear pedido');
    } finally {
      setLoading(false);
    }
  };

  const totales = calcularTotales();

  return (
    <div className="container py-4">
      <div className="row justify-content-center">
        <div className="col-lg-10">
          <div className="card">
            <div className="card-header bg-primary text-white">
              <h3 className="mb-0">Nuevo Pedido</h3>
            </div>
            
            <div className="card-body">
              {error && (
                <div className="alert alert-danger" role="alert">
                  {error}
                </div>
              )}

              {success && (
                <div className="alert alert-success" role="alert">
                  ¡Pedido creado exitosamente! Redirigiendo...
                </div>
              )}

              <form onSubmit={handleSubmit}>
                {/* Datos del Cliente */}
                <div className="mb-4">
                  <h5 className="border-bottom pb-2">Datos del Cliente</h5>
                  
                  <div className="row g-3">
                    <div className="col-md-6">
                      <label className="form-label">Socio ID *</label>
                      <input 
                        type="number"
                        className="form-control"
                        name="socio_id"
                        value={formData.socio_id}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                    
                    <div className="col-md-6">
                      <label className="form-label">Nombre del Cliente *</label>
                      <input 
                        type="text"
                        className="form-control"
                        name="cliente_nombre"
                        value={formData.cliente_nombre}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                    
                    <div className="col-md-6">
                      <label className="form-label">Email</label>
                      <input 
                        type="email"
                        className="form-control"
                        name="cliente_email"
                        value={formData.cliente_email}
                        onChange={handleInputChange}
                      />
                    </div>
                    
                    <div className="col-md-6">
                      <label className="form-label">Teléfono</label>
                      <input 
                        type="tel"
                        className="form-control"
                        name="cliente_telefono"
                        value={formData.cliente_telefono}
                        onChange={handleInputChange}
                      />
                    </div>
                  </div>
                </div>

                {/* Productos */}
                <div className="mb-4">
                  <div className="d-flex justify-content-between align-items-center mb-3">
                    <h5 className="mb-0">Productos</h5>
                    <button 
                      type="button"
                      className="btn btn-sm btn-outline-primary"
                      onClick={agregarItem}
                    >
                      <i className="bi bi-plus-circle"></i> Agregar Producto
                    </button>
                  </div>

                  <div className="table-responsive">
                    <table className="table">
                      <thead>
                        <tr>
                          <th style={{width: '40%'}}>Producto ID *</th>
                          <th style={{width: '20%'}}>Cantidad *</th>
                          <th style={{width: '20%'}}>Precio Unit. *</th>
                          <th style={{width: '15%'}}>Subtotal</th>
                          <th style={{width: '5%'}}></th>
                        </tr>
                      </thead>
                      <tbody>
                        {items.map((item, index) => (
                          <tr key={index}>
                            <td>
                              <input 
                                type="number"
                                className="form-control"
                                value={item.producto_id}
                                onChange={(e) => handleItemChange(index, 'producto_id', e.target.value)}
                                required
                              />
                            </td>
                            <td>
                              <input 
                                type="number"
                                step="0.01"
                                className="form-control"
                                value={item.cantidad}
                                onChange={(e) => handleItemChange(index, 'cantidad', e.target.value)}
                                required
                              />
                            </td>
                            <td>
                              <input 
                                type="number"
                                step="0.01"
                                className="form-control"
                                value={item.precio_unitario}
                                onChange={(e) => handleItemChange(index, 'precio_unitario', e.target.value)}
                                required
                              />
                            </td>
                            <td>
                              <input 
                                type="text"
                                className="form-control"
                                value={calcularSubtotal(item).toFixed(2)}
                                readOnly
                              />
                            </td>
                            <td>
                              {items.length > 1 && (
                                <button 
                                  type="button"
                                  className="btn btn-sm btn-outline-danger"
                                  onClick={() => eliminarItem(index)}
                                >
                                  <i className="bi bi-trash"></i>
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Totales */}
                <div className="row mb-4">
                  <div className="col-md-6">
                    <label className="form-label">Notas</label>
                    <textarea 
                      className="form-control"
                      name="notas"
                      rows="3"
                      value={formData.notas}
                      onChange={handleInputChange}
                    />
                  </div>
                  
                  <div className="col-md-6">
                    <div className="card">
                      <div className="card-body">
                        <div className="row mb-2">
                          <div className="col-6"><strong>Subtotal:</strong></div>
                          <div className="col-6 text-end">Bs. {totales.subtotal.toFixed(2)}</div>
                        </div>
                        
                        <div className="row mb-2">
                          <div className="col-6">
                            <label className="form-label mb-0">Impuestos:</label>
                          </div>
                          <div className="col-6">
                            <input 
                              type="number"
                              step="0.01"
                              className="form-control form-control-sm"
                              name="impuestos"
                              value={formData.impuestos}
                              onChange={handleInputChange}
                            />
                          </div>
                        </div>
                        
                        <div className="row mb-3">
                          <div className="col-6">
                            <label className="form-label mb-0">Descuento:</label>
                          </div>
                          <div className="col-6">
                            <input 
                              type="number"
                              step="0.01"
                              className="form-control form-control-sm"
                              name="descuento"
                              value={formData.descuento}
                              onChange={handleInputChange}
                            />
                          </div>
                        </div>
                        
                        <div className="row border-top pt-2">
                          <div className="col-6"><h5 className="mb-0">TOTAL:</h5></div>
                          <div className="col-6 text-end">
                            <h5 className="mb-0 text-primary">Bs. {totales.total.toFixed(2)}</h5>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Botones */}
                <div className="d-flex justify-content-end gap-2">
                  <button 
                    type="button"
                    className="btn btn-secondary"
                    onClick={() => window.history.back()}
                  >
                    Cancelar
                  </button>
                  <button 
                    type="submit"
                    className="btn btn-primary"
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                        Creando...
                      </>
                    ) : (
                      <>
                        <i className="bi bi-check-circle me-2"></i>
                        Crear Pedido
                      </>
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormularioPedido;
```

### 3. Formulario de Pago con Stripe

```jsx
// components/Pagos/FormularioPagoStripe.jsx
import React, { useState, useEffect } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { 
  CardElement, 
  Elements, 
  useStripe, 
  useElements 
} from '@stripe/react-stripe-js';
import { pagosService, pedidosService } from '../../api/pagosService';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);

const FormularioPagoStripeInner = ({ pedidoId }) => {
  const stripe = useStripe();
  const elements = useElements();
  
  const [pedido, setPedido] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [monto, setMonto] = useState('');
  const [comprobante, setComprobante] = useState('');

  useEffect(() => {
    cargarPedido();
  }, [pedidoId]);

  const cargarPedido = async () => {
    try {
      const data = await pedidosService.obtener(pedidoId);
      setPedido(data);
      setMonto(data.saldo_pendiente);
    } catch (err) {
      setError('Error al cargar pedido');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    try {
      setLoading(true);
      setError(null);

      // Crear PaymentMethod con Stripe
      const { paymentMethod, error: stripeError } = await stripe.createPaymentMethod({
        type: 'card',
        card: elements.getElement(CardElement),
        billing_details: {
          name: pedido.cliente_nombre,
          email: pedido.cliente_email
        }
      });

      if (stripeError) {
        throw new Error(stripeError.message);
      }

      // Enviar al backend
      const resultado = await pagosService.pagarConStripe({
        pedido_id: pedidoId,
        monto: monto,
        payment_method_id: paymentMethod.id,
        comprobante: comprobante
      });

      setSuccess(true);
      setTimeout(() => {
        window.location.href = `/pedidos/${pedidoId}`;
      }, 2000);

    } catch (err) {
      setError(err.error || err.message || 'Error al procesar pago');
    } finally {
      setLoading(false);
    }
  };

  if (!pedido) {
    return <div className="text-center py-5">Cargando...</div>;
  }

  return (
    <div className="card">
      <div className="card-header bg-success text-white">
        <h4 className="mb-0">Pagar con Tarjeta</h4>
      </div>
      
      <div className="card-body">
        {error && (
          <div className="alert alert-danger" role="alert">
            {error}
          </div>
        )}

        {success && (
          <div className="alert alert-success" role="alert">
            ¡Pago procesado exitosamente! Redirigiendo...
          </div>
        )}

        {/* Información del Pedido */}
        <div className="card mb-4">
          <div className="card-body">
            <h5>Pedido: {pedido.numero_pedido}</h5>
            <p className="mb-1">Cliente: {pedido.cliente_nombre}</p>
            <p className="mb-1">Total: Bs. {parseFloat(pedido.total).toFixed(2)}</p>
            <p className="mb-1">Pagado: Bs. {parseFloat(pedido.total_pagado).toFixed(2)}</p>
            <p className="mb-0">
              <strong>Saldo Pendiente: Bs. {parseFloat(pedido.saldo_pendiente).toFixed(2)}</strong>
            </p>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label className="form-label">Monto a Pagar *</label>
            <input 
              type="number"
              step="0.01"
              className="form-control"
              value={monto}
              onChange={(e) => setMonto(e.target.value)}
              max={pedido.saldo_pendiente}
              required
            />
            <small className="form-text text-muted">
              Máximo: Bs. {parseFloat(pedido.saldo_pendiente).toFixed(2)}
            </small>
          </div>

          <div className="mb-3">
            <label className="form-label">Número de Comprobante</label>
            <input 
              type="text"
              className="form-control"
              value={comprobante}
              onChange={(e) => setComprobante(e.target.value)}
              placeholder="STRIPE-REC-001"
            />
          </div>

          <div className="mb-4">
            <label className="form-label">Datos de la Tarjeta *</label>
            <div className="card">
              <div className="card-body">
                <CardElement 
                  options={{
                    style: {
                      base: {
                        fontSize: '16px',
                        color: '#424770',
                        '::placeholder': {
                          color: '#aab7c4',
                        },
                      },
                      invalid: {
                        color: '#9e2146',
                      },
                    },
                  }}
                />
              </div>
            </div>
            <small className="form-text text-muted">
              Tarjeta de prueba: 4242 4242 4242 4242 | CVV: 123 | Fecha: 12/30
            </small>
          </div>

          <div className="d-flex justify-content-between">
            <button 
              type="button"
              className="btn btn-secondary"
              onClick={() => window.history.back()}
            >
              Cancelar
            </button>
            
            <button 
              type="submit"
              className="btn btn-success"
              disabled={!stripe || loading}
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2"></span>
                  Procesando...
                </>
              ) : (
                <>
                  <i className="bi bi-credit-card me-2"></i>
                  Pagar Bs. {parseFloat(monto || 0).toFixed(2)}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

const FormularioPagoStripe = ({ pedidoId }) => {
  return (
    <Elements stripe={stripePromise}>
      <FormularioPagoStripeInner pedidoId={pedidoId} />
    </Elements>
  );
};

export default FormularioPagoStripe;
```

---

## 🖼️ Componentes Vue 3

### Lista de Pedidos (Vue)

```vue
<!-- components/Pedidos/ListaPedidos.vue -->
<template>
  <div class="container-fluid py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Pedidos</h2>
      <button class="btn btn-primary" @click="$router.push('/pedidos/nuevo')">
        <i class="bi bi-plus-circle"></i> Nuevo Pedido
      </button>
    </div>

    <!-- Filtros -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <label class="form-label">Estado</label>
            <select class="form-select" v-model="filtros.estado">
              <option value="">Todos</option>
              <option value="PENDIENTE">Pendiente</option>
              <option value="CONFIRMADO">Confirmado</option>
              <option value="EN_PROCESO">En Proceso</option>
              <option value="COMPLETADO">Completado</option>
              <option value="CANCELADO">Cancelado</option>
            </select>
          </div>
          
          <div class="col-md-3">
            <label class="form-label">Desde</label>
            <input type="date" class="form-control" v-model="filtros.fecha_desde" />
          </div>
          
          <div class="col-md-3">
            <label class="form-label">Hasta</label>
            <input type="date" class="form-control" v-model="filtros.fecha_hasta" />
          </div>
          
          <div class="col-md-3">
            <label class="form-label">Cliente</label>
            <input 
              type="text" 
              class="form-control"
              placeholder="Nombre del cliente"
              v-model="filtros.cliente_nombre"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="d-flex justify-content-center p-5">
      <div class="spinner-border" role="status">
        <span class="visually-hidden">Cargando...</span>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>

    <!-- Tabla -->
    <div v-if="!loading" class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>N° Pedido</th>
                <th>Fecha</th>
                <th>Cliente</th>
                <th>Total</th>
                <th>Pagado</th>
                <th>Pendiente</th>
                <th>Estado</th>
                <th>Pago</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="pedido in pedidos" :key="pedido.id">
                <td><strong>{{ pedido.numero_pedido }}</strong></td>
                <td>{{ formatFecha(pedido.fecha_pedido) }}</td>
                <td>{{ pedido.cliente_nombre }}</td>
                <td>Bs. {{ formatMonto(pedido.total) }}</td>
                <td>Bs. {{ formatMonto(pedido.total_pagado) }}</td>
                <td>Bs. {{ formatMonto(pedido.saldo_pendiente) }}</td>
                <td>
                  <span :class="`badge ${getEstadoBadgeClass(pedido.estado)}`">
                    {{ pedido.estado }}
                  </span>
                </td>
                <td>
                  <span :class="`badge ${getEstadoPagoBadgeClass(pedido.estado_pago)}`">
                    {{ pedido.estado_pago }}
                  </span>
                </td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-primary me-1"
                    @click="$router.push(`/pedidos/${pedido.id}`)"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button 
                    v-if="pedido.saldo_pendiente > 0 && pedido.estado !== 'CANCELADO'"
                    class="btn btn-sm btn-outline-success"
                    @click="$router.push(`/pagos/nuevo?pedido_id=${pedido.id}`)"
                  >
                    <i class="bi bi-cash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Paginación -->
        <nav v-if="estadisticas.total_pages > 1" class="mt-3">
          <ul class="pagination justify-content-center">
            <li :class="`page-item ${filtros.page === 1 ? 'disabled' : ''}`">
              <button 
                class="page-link"
                @click="cambiarPagina(filtros.page - 1)"
                :disabled="filtros.page === 1"
              >
                Anterior
              </button>
            </li>
            
            <li 
              v-for="i in estadisticas.total_pages" 
              :key="i"
              :class="`page-item ${filtros.page === i ? 'active' : ''}`"
            >
              <button class="page-link" @click="cambiarPagina(i)">
                {{ i }}
              </button>
            </li>
            
            <li :class="`page-item ${filtros.page === estadisticas.total_pages ? 'disabled' : ''}`">
              <button 
                class="page-link"
                @click="cambiarPagina(filtros.page + 1)"
                :disabled="filtros.page === estadisticas.total_pages"
              >
                Siguiente
              </button>
            </li>
          </ul>
        </nav>

        <div class="text-center text-muted mt-2">
          Mostrando {{ pedidos.length }} de {{ estadisticas.count }} pedidos
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { pedidosService } from '@/api/pagosService';
import { format } from 'date-fns';
import { es } from 'date-fns/locale';

const pedidos = ref([]);
const loading = ref(true);
const error = ref(null);
const filtros = ref({
  estado: '',
  fecha_desde: '',
  fecha_hasta: '',
  cliente_nombre: '',
  page: 1
});
const estadisticas = ref({
  count: 0,
  total_pages: 0
});

onMounted(() => {
  cargarPedidos();
});

watch(filtros, () => {
  cargarPedidos();
}, { deep: true });

const cargarPedidos = async () => {
  try {
    loading.value = true;
    const data = await pedidosService.listar(filtros.value);
    pedidos.value = data.results;
    estadisticas.value = {
      count: data.count,
      total_pages: data.total_pages || Math.ceil(data.count / 20)
    };
    error.value = null;
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};

const cambiarPagina = (nuevaPagina) => {
  filtros.value.page = nuevaPagina;
};

const formatFecha = (fecha) => {
  return format(new Date(fecha), 'dd/MM/yyyy HH:mm', { locale: es });
};

const formatMonto = (monto) => {
  return parseFloat(monto).toFixed(2);
};

const getEstadoBadgeClass = (estado) => {
  const clases = {
    'PENDIENTE': 'badge-warning',
    'CONFIRMADO': 'badge-info',
    'EN_PROCESO': 'badge-primary',
    'COMPLETADO': 'badge-success',
    'CANCELADO': 'badge-danger'
  };
  return clases[estado] || 'badge-secondary';
};

const getEstadoPagoBadgeClass = (estadoPago) => {
  const clases = {
    'PENDIENTE': 'badge-danger',
    'PARCIAL': 'badge-warning',
    'PAGADO': 'badge-success'
  };
  return clases[estadoPago] || 'badge-secondary';
};
</script>
```

---

## 💳 Integración Completa Stripe

### Configuración en main.js/App.jsx

```javascript
// React - index.jsx o App.jsx
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';

const stripePromise = loadStripe(import.meta.env.VITE_STRIPE_PUBLIC_KEY);

function App() {
  return (
    <Elements stripe={stripePromise}>
      {/* Tu aplicación aquí */}
    </Elements>
  );
}
```

```javascript
// Vue - main.js
import { createApp } from 'vue';
import App from './App.vue';

const app = createApp(App);

// Configurar Stripe globalmente
app.config.globalProperties.$stripeKey = import.meta.env.VITE_STRIPE_PUBLIC_KEY;

app.mount('#app');
```

---

## 📊 Dashboard de Resumen

```jsx
// components/Dashboard/ResumenVentas.jsx
import React, { useState, useEffect } from 'react';
import { historialService } from '../../api/pagosService';
import { format, subDays } from 'date-fns';

const ResumenVentas = () => {
  const [estadisticas, setEstadisticas] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarEstadisticas();
  }, []);

  const cargarEstadisticas = async () => {
    try {
      setLoading(true);
      
      // Últimos 30 días
      const fecha_hasta = format(new Date(), 'yyyy-MM-dd');
      const fecha_desde = format(subDays(new Date(), 30), 'yyyy-MM-dd');
      
      const data = await historialService.obtenerHistorial({
        fecha_desde,
        fecha_hasta,
        page_size: 1 // Solo necesitamos las estadísticas
      });
      
      setEstadisticas(data.estadisticas);
    } catch (err) {
      console.error('Error al cargar estadísticas:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-5">Cargando estadísticas...</div>;
  }

  if (!estadisticas) {
    return null;
  }

  return (
    <div className="row g-4">
      <div className="col-md-3">
        <div className="card bg-primary text-white">
          <div className="card-body">
            <h5 className="card-title">Total Ventas</h5>
            <h2 className="mb-0">{estadisticas.total_ventas}</h2>
            <small>Últimos 30 días</small>
          </div>
        </div>
      </div>

      <div className="col-md-3">
        <div className="card bg-success text-white">
          <div className="card-body">
            <h5 className="card-title">Monto Total</h5>
            <h2 className="mb-0">Bs. {parseFloat(estadisticas.total_monto).toFixed(2)}</h2>
            <small>Total facturado</small>
          </div>
        </div>
      </div>

      <div className="col-md-3">
        <div className="card bg-info text-white">
          <div className="card-body">
            <h5 className="card-title">Total Pagado</h5>
            <h2 className="mb-0">Bs. {parseFloat(estadisticas.total_pagado).toFixed(2)}</h2>
            <small>Pagos recibidos</small>
          </div>
        </div>
      </div>

      <div className="col-md-3">
        <div className="card bg-warning text-white">
          <div className="card-body">
            <h5 className="card-title">Pendiente</h5>
            <h2 className="mb-0">Bs. {parseFloat(estadisticas.total_pendiente).toFixed(2)}</h2>
            <small>Por cobrar</small>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResumenVentas;
```

---

**Fin de los Ejemplos Frontend**

Para más información, consultar el documento principal: `SISTEMA_PAGOS_API.md`
