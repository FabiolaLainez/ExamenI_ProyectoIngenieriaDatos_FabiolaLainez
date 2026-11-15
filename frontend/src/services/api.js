
const API_URL = "http://127.0.0.1:8000";

export async function obtenerResumen(filtros = {}) {
  const params = new URLSearchParams();

  Object.entries(filtros).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      params.append(key, value);
    }
  });

  const response = await fetch(
    `${API_URL}/api/dashboard/resumen?${params.toString()}`
  );

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

export async function obtenerVentasMensuales(filtros = {}) {
  const params = new URLSearchParams();

  Object.entries(filtros).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      params.append(key, value);
    }
  });

  const response = await fetch(
    `${API_URL}/api/dashboard/ventas-mensuales?${params.toString()}`
  );

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}

export async function obtenerVentasCategoria(filtros = {}) {
  const params = new URLSearchParams();

  Object.entries(filtros).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) {
      params.append(key, value);
    }
  });

  const response = await fetch(
    `${API_URL}/api/dashboard/ventas-categoria?${params.toString()}`
  );

  if (!response.ok) {
    throw new Error(`Error HTTP: ${response.status}`);
  }

  return await response.json();
}
