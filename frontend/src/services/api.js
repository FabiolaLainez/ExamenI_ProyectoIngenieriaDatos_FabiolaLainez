
const API_URL = "http://127.0.0.1:8000";

// Función general para construir los filtros
function construirParametros(filtros = {}) {
  const params = new URLSearchParams();

  Object.entries(filtros).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      params.append(key, value);
    }
  });

  return params.toString();
}

// DASHBOARD: RESUMEN
export async function obtenerResumen(filtros = {}) {
  const parametros = construirParametros(filtros);

  const response = await fetch(
    `${API_URL}/api/dashboard/resumen?${parametros}`
  );

  if (!response.ok) {
    throw new Error(`Error al obtener resumen: ${response.status}`);
  }

  return await response.json();
}

// DASHBOARD: VENTAS MENSUALES
export async function obtenerVentasMensuales(filtros = {}) {
  const parametros = construirParametros(filtros);

  const response = await fetch(
    `${API_URL}/api/dashboard/ventas-mensuales?${parametros}`
  );

  if (!response.ok) {
    throw new Error(`Error al obtener ventas mensuales: ${response.status}`);
  }

  return await response.json();
}

// DASHBOARD: VENTAS POR CATEGORÍA
export async function obtenerVentasCategoria(filtros = {}) {
  const parametros = construirParametros(filtros);

  const response = await fetch(
    `${API_URL}/api/dashboard/ventas-categoria?${parametros}`
  );

  if (!response.ok) {
    throw new Error(`Error al obtener ventas por categoría: ${response.status}`);
  }

  return await response.json();
}

// MACHINE LEARNING: PRONÓSTICO DE VENTAS
export async function obtenerPronostico() {
  const response = await fetch(
    `${API_URL}/api/ml/pronostico`
  );

  if (!response.ok) {
    throw new Error(`Error al obtener pronóstico: ${response.status}`);
  }

  return await response.json();
}

