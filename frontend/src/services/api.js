
const API_URL = "http://127.0.0.1:8000";

// ==========================================
// FUNCIÓN AUXILIAR PARA CONSTRUIR FILTROS
// ==========================================

function construirParametros(filtros = {}) {
  const params = new URLSearchParams();

  Object.entries(filtros).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      params.append(key, value);
    }
  });

  return params.toString();
}

// ==========================================
// DASHBOARD
// ==========================================

export async function obtenerResumen(filtros = {}) {
  const parametros = construirParametros(filtros);

  const response = await fetch(
    `${API_URL}/api/dashboard/resumen?${parametros}`
  );

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

export async function obtenerVentasMensuales(filtros = {}) {
  const parametros = construirParametros(filtros);

  const response = await fetch(
    `${API_URL}/api/dashboard/ventas-mensuales?${parametros}`
  );

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

export async function obtenerVentasCategoria(filtros = {}) {
  const parametros = construirParametros(filtros);

  const response = await fetch(
    `${API_URL}/api/dashboard/ventas-categoria?${parametros}`
  );

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

// ==========================================
// VENTAS
// ==========================================

export async function obtenerVentas() {
  const response = await fetch(`${API_URL}/api/ventas`);

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

// ==========================================
// CLIENTES
// ==========================================

export async function obtenerClientes() {
  const response = await fetch(`${API_URL}/api/clientes`);

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

// ==========================================
// PRODUCTOS
// ==========================================

export async function obtenerProductos() {
  const response = await fetch(`${API_URL}/api/productos`);

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

// ==========================================
// PAGOS
// ==========================================

export async function obtenerPagos() {
  const response = await fetch(`${API_URL}/api/pagos`);

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

// ==========================================
// INVENTARIO
// ==========================================

export async function obtenerInventario() {
  const response = await fetch(`${API_URL}/api/inventario`);

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

// ==========================================
// DATA WAREHOUSE
// ==========================================

export async function obtenerEstadoDataWarehouse() {
  const response = await fetch(`${API_URL}/api/datawarehouse`);

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

// ==========================================
// MACHINE LEARNING
// ==========================================

export async function obtenerPronostico() {
  const response = await fetch(`${API_URL}/api/ml/pronostico`);

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

// ==========================================
// INTELIGENCIA ARTIFICIAL GENERATIVA - GEMINI
// ==========================================

export async function consultarIA(pregunta) {
  if (!pregunta || !pregunta.trim()) {
    throw new Error("Debes escribir una pregunta.");
  }

  const params = new URLSearchParams({
    pregunta: pregunta.trim()
  });

  const response = await fetch(
    `${API_URL}/api/ia/consultar?${params.toString()}`
  );

  if (!response.ok) {
    let mensaje = "Error al consultar Gemini.";

    try {
      const error = await response.json();
      mensaje = error.detail || mensaje;
    } catch {
      // Mantener mensaje predeterminado si la respuesta no es JSON.
    }

    throw new Error(mensaje);
  }

  return await response.json();
}
