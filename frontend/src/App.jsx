
import { useEffect, useMemo, useState } from "react";
import {
  LayoutDashboard,
  ShoppingCart,
  Users,
  Package,
  CreditCard,
  BarChart3,
  Bell,
  Search,
  CalendarDays,
  DollarSign,
  Menu,
  Download,
  CircleHelp,
  RefreshCw,
  Database,
  BrainCircuit,
  TrendingUp,
  Target,
} from "lucide-react";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from "recharts";

import {
  obtenerResumen,
  obtenerVentasMensuales,
  obtenerVentasCategoria,
} from "./services/api";

const API_URL = "http://127.0.0.1:8000";

const COLORS = ["#2563eb", "#14b8a6", "#f59e0b", "#8b5cf6", "#ec4899"];

const MESES = [
  "Ene", "Feb", "Mar", "Abr", "May", "Jun",
  "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
];

const formatMoney = (value) =>
  new Intl.NumberFormat("es-HN", {
    style: "currency",
    currency: "HNL",
    maximumFractionDigits: 2,
  }).format(Number(value) || 0);

const formatNumber = (value) =>
  new Intl.NumberFormat("es-HN").format(Number(value) || 0);

function obtenerFilas(respuesta) {
  if (Array.isArray(respuesta)) return respuesta;
  if (Array.isArray(respuesta?.data)) return respuesta.data;
  if (Array.isArray(respuesta?.resultados)) return respuesta.resultados;
  if (Array.isArray(respuesta?.ventas)) return respuesta.ventas;
  if (Array.isArray(respuesta?.datos)) return respuesta.datos;
  return [];
}

function normalizarVentasMensuales(respuesta) {
  return obtenerFilas(respuesta).map((item) => {
    const mes =
      item.mes ??
      item.Mes ??
      item.nombre_mes ??
      item.NombreMes ??
      item.month ??
      "";

    const numeroMes = Number(mes);

    return {
      month:
        numeroMes >= 1 && numeroMes <= 12
          ? MESES[numeroMes - 1]
          : String(mes).substring(0, 3),
      sales: Number(
        item.ventas ??
        item.Ventas ??
        item.total_ventas ??
        item.TotalVentas ??
        item.sales ??
        item.total ??
        0
      ),
    };
  });
}

function normalizarCategorias(respuesta) {
  return obtenerFilas(respuesta).map((item) => ({
    name:
      item.categoria ??
      item.Categoria ??
      item.nombre_categoria ??
      item.NombreCategoria ??
      item.name ??
      "Sin categoría",
    value: Number(
      item.ventas ??
      item.Ventas ??
      item.total_ventas ??
      item.TotalVentas ??
      item.ingresos ??
      item.Ingresos ??
      item.total ??
      item.value ??
      0
    ),
  }));
}

function MetricCard({ title, value, icon: Icon, description, loading }) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span className="metric-title">{title}</span>
        <div className="metric-icon">
          <Icon size={19} />
        </div>
      </div>

      <div className="metric-value">
        {loading ? "..." : value}
      </div>

      <div className="metric-bottom">
        <span className="metric-description">{description}</span>
      </div>
    </div>
  );
}

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [period, setPeriod] = useState("Anual");
  const [category, setCategory] = useState("Todas");
  const [search, setSearch] = useState("");

  const [resumen, setResumen] = useState(null);
  const [ventasMensuales, setVentasMensuales] = useState([]);
  const [ventasCategoria, setVentasCategoria] = useState([]);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [seccionDatos, setSeccionDatos] = useState([]);
  const [seccionLoading, setSeccionLoading] = useState(false);
  const [seccionError, setSeccionError] = useState("");

  // Estados de Machine Learning
  const [pronostico, setPronostico] = useState([]);
  const [modeloML, setModeloML] = useState("");
  const [horizonteML, setHorizonteML] = useState(7);
  const [mlLoading, setMlLoading] = useState(false);
  const [mlError, setMlError] = useState("");

  const menuItems = [
    { label: "Dashboard", icon: LayoutDashboard },
    { label: "Ventas", icon: ShoppingCart },
    { label: "Clientes", icon: Users },
    { label: "Productos", icon: Package },
    { label: "Pagos", icon: CreditCard },
    { label: "Inventario", icon: BarChart3 },
    { label: "Data Warehouse", icon: Database },
    { label: "Pronóstico ML", icon: BrainCircuit },
  ];

  const endpoints = {
    Ventas: "/api/ventas",
    Clientes: "/api/clientes",
    Productos: "/api/productos",
    Pagos: "/api/pagos",
    Inventario: "/api/inventario",
    "Data Warehouse": "/api/datawarehouse",
  };

  // Cargar información del dashboard
  const cargarDatos = async () => {
    setLoading(true);
    setError("");

    const resultados = await Promise.allSettled([
      obtenerResumen(),
      obtenerVentasMensuales(),
      obtenerVentasCategoria(),
    ]);

    if (resultados[0].status === "fulfilled") {
      setResumen(resultados[0].value);
    } else {
      setError(
        "No se pudieron cargar los indicadores. Verifica que FastAPI esté activo."
      );
    }

    if (resultados[1].status === "fulfilled") {
      setVentasMensuales(
        normalizarVentasMensuales(resultados[1].value)
      );
    }

    if (resultados[2].status === "fulfilled") {
      setVentasCategoria(
        normalizarCategorias(resultados[2].value)
      );
    }

    setLoading(false);
  };

  // Cargar información de cada sección
  const cargarDatosSeccion = async (pagina) => {
    const endpoint = endpoints[pagina];

    if (!endpoint) return;

    setSeccionLoading(true);
    setSeccionError("");
    setSeccionDatos([]);

    try {
      const response = await fetch(`${API_URL}${endpoint}`);

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }

      const resultado = await response.json();

      if (pagina === "Data Warehouse") {
        const filas = Object.entries(resultado)
          .filter(([tabla]) => tabla !== "total_registros")
          .map(([tabla, registros]) => ({
            tabla,
            registros,
          }));

        setSeccionDatos(filas);
      } else {
        setSeccionDatos(obtenerFilas(resultado));
      }
    } catch (error) {
      setSeccionError(
        `No se pudieron cargar los datos: ${error.message}`
      );
    } finally {
      setSeccionLoading(false);
    }
  };

  // Consultar pronóstico de Machine Learning
  const cargarPronostico = async () => {
    setMlLoading(true);
    setMlError("");

    try {
      const response = await fetch(
        `${API_URL}/api/ml/pronostico`
      );

      if (!response.ok) {
        throw new Error(`Error HTTP: ${response.status}`);
      }

      const resultado = await response.json();

      setModeloML(resultado.modelo || "Modelo predictivo");
      setHorizonteML(resultado.horizonte_dias || 7);

      const datos = Array.isArray(resultado.pronosticos)
        ? resultado.pronosticos.map((item) => ({
            fecha: item.fecha,
            ventas: Number(item.ventas_pronosticadas) || 0,
            fechaCorta: new Date(
              `${item.fecha}T00:00:00`
            ).toLocaleDateString("es-HN", {
              day: "2-digit",
              month: "short",
            }),
          }))
        : [];

      setPronostico(datos);

      if (datos.length === 0) {
        setMlError("El modelo no devolvió pronósticos.");
      }
    } catch (error) {
      setMlError(
        `No se pudo cargar el pronóstico: ${error.message}`
      );
    } finally {
      setMlLoading(false);
    }
  };

  const actualizarDatos = () => {
    if (activePage === "Dashboard") {
      cargarDatos();
    } else if (activePage === "Pronóstico ML") {
      cargarPronostico();
    } else {
      cargarDatosSeccion(activePage);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    if (activePage !== "Dashboard") {
      setSearch("");

      if (activePage === "Pronóstico ML") {
        cargarPronostico();
      } else {
        cargarDatosSeccion(activePage);
      }
    }
  }, [activePage]);

  const chartData = useMemo(() => {
    if (period === "Primer semestre") {
      return ventasMensuales.slice(0, 6);
    }

    if (period === "Últimos 6 meses") {
      return ventasMensuales.slice(-6);
    }

    return ventasMensuales;
  }, [period, ventasMensuales]);

  const categoriasDisponibles = useMemo(
    () => ventasCategoria.map((item) => item.name),
    [ventasCategoria]
  );

  const categoriasFiltradas = useMemo(() => {
    if (category === "Todas") return ventasCategoria;

    return ventasCategoria.filter(
      (item) => item.name === category
    );
  }, [category, ventasCategoria]);

  const totalCategorias = categoriasFiltradas.reduce(
    (total, item) => total + item.value,
    0
  );

  const datosFiltrados = useMemo(() => {
    return seccionDatos.filter((fila) =>
      Object.values(fila).some((valor) =>
        String(valor ?? "")
          .toLowerCase()
          .includes(search.toLowerCase())
      )
    );
  }, [seccionDatos, search]);

  const columnas = seccionDatos.length > 0
    ? Object.keys(seccionDatos[0])
    : [];

  const totalPronosticado = pronostico.reduce(
    (total, item) => total + item.ventas,
    0
  );

  const promedioPronosticado = pronostico.length
    ? totalPronosticado / pronostico.length
    : 0;

  const mejorDia = pronostico.length
    ? pronostico.reduce((mayor, actual) =>
        actual.ventas > mayor.ventas ? actual : mayor
      )
    : null;

  return (
    <div className="app-layout">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-logo">EC</div>
          <div>
            <h2>EmpresaComercial</h2>
            <span>Business Intelligence</span>
          </div>
        </div>

        <div className="menu-label">MENÚ PRINCIPAL</div>

        <nav className="navigation">
          {menuItems.map((item) => {
            const Icon = item.icon;

            return (
              <button
                key={item.label}
                className={`nav-item ${
                  activePage === item.label ? "active" : ""
                }`}
                onClick={() => setActivePage(item.label)}
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="sidebar-bottom">
          <div className="data-status">
            <span className="status-dot"></span>
            <div>
              <strong>Data Warehouse</strong>
              <small>SQL Server · EmpresaComercial</small>
            </div>
          </div>

          <div className="sidebar-help">
            <CircleHelp size={18} />
            <span>Centro de ayuda</span>
          </div>

          <div className="user-profile">
            <div className="avatar">FL</div>
            <div>
              <strong>Administrador</strong>
              <small>Analista de datos</small>
            </div>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            <Menu size={19} className="mobile-menu-icon" />
            <span>EmpresaComercial</span>
            <span className="breadcrumb-separator">/</span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-actions">
            <div className="search-box">
              <Search size={17} />
              <input
                type="text"
                placeholder="Buscar..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>

            <button
              className="icon-button"
              aria-label="Actualizar datos"
              onClick={actualizarDatos}
              title="Actualizar datos"
            >
              <RefreshCw size={18} />
            </button>

            <button
              className="icon-button"
              aria-label="Notificaciones"
            >
              <Bell size={19} />
              <span className="notification-dot"></span>
            </button>

            <div className="top-avatar">FL</div>
          </div>
        </header>

        <div className="page-container">
          <section className="page-heading">
            <div>
              <div className="eyebrow">
                {activePage === "Dashboard"
                  ? "RESUMEN DEL NEGOCIO"
                  : activePage === "Pronóstico ML"
                    ? "ANALÍTICA PREDICTIVA"
                    : "GESTIÓN Y ANÁLISIS DE DATOS"}
              </div>

              <h1>
                {activePage === "Dashboard"
                  ? "Dashboard ejecutivo"
                  : activePage === "Pronóstico ML"
                    ? "Pronóstico de ventas"
                    : `Análisis de ${activePage}`}
              </h1>

              <p>
                Monitorea el rendimiento y comportamiento de tu empresa.
              </p>
            </div>

            <button
              className="export-button"
              onClick={() => window.print()}
            >
              <Download size={17} />
              Exportar
            </button>
          </section>

          {/* DASHBOARD */}
          {activePage === "Dashboard" && (
            <>
              {error && (
                <div className="error-message">{error}</div>
              )}

              <section className="filters-panel">
                <div className="filter-heading">
                  <CalendarDays size={18} />
                  <strong>Filtros de análisis</strong>
                </div>

                <div className="filter-controls">
                  <label>
                    Período
                    <select
                      value={period}
                      onChange={(e) => setPeriod(e.target.value)}
                    >
                      <option>Anual</option>
                      <option>Primer semestre</option>
                      <option>Últimos 6 meses</option>
                    </select>
                  </label>

                  <label>
                    Categoría
                    <select
                      value={category}
                      onChange={(e) => setCategory(e.target.value)}
                    >
                      <option value="Todas">Todas</option>
                      {categoriasDisponibles.map((item) => (
                        <option key={item} value={item}>
                          {item}
                        </option>
                      ))}
                    </select>
                  </label>
                </div>
              </section>

              <section className="metrics-grid">
                <MetricCard
                  title="Ventas totales"
                  value={formatMoney(resumen?.ventas_totales)}
                  icon={DollarSign}
                  description="Ingresos registrados"
                  loading={loading}
                />

                <MetricCard
                  title="Unidades vendidas"
                  value={formatNumber(resumen?.unidades_vendidas)}
                  icon={ShoppingCart}
                  description="Unidades comercializadas"
                  loading={loading}
                />

                <MetricCard
                  title="Clientes registrados"
                  value={formatNumber(resumen?.clientes_registrados)}
                  icon={Users}
                  description="Clientes en el Data Warehouse"
                  loading={loading}
                />

                <MetricCard
                  title="Ticket promedio"
                  value={formatMoney(resumen?.ticket_promedio)}
                  icon={CreditCard}
                  description="Promedio por venta"
                  loading={loading}
                />
              </section>

              <section className="charts-grid">
                <div className="panel sales-panel">
                  <div className="panel-header">
                    <div>
                      <h3>Evolución de ventas</h3>
                      <p>Ventas registradas por mes</p>
                    </div>
                    <span className="chart-tag">HNL</span>
                  </div>

                  <div className="chart-legend">
                    <span>
                      <i className="legend-dot blue"></i>
                      Ventas reales
                    </span>
                  </div>

                  <div className="chart-area">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart
                        data={chartData}
                        margin={{
                          top: 10,
                          right: 10,
                          left: 0,
                          bottom: 0,
                        }}
                      >
                        <defs>
                          <linearGradient
                            id="salesGradient"
                            x1="0"
                            y1="0"
                            x2="0"
                            y2="1"
                          >
                            <stop
                              offset="0%"
                              stopColor="#2563eb"
                              stopOpacity={0.22}
                            />
                            <stop
                              offset="100%"
                              stopColor="#2563eb"
                              stopOpacity={0}
                            />
                          </linearGradient>
                        </defs>

                        <CartesianGrid
                          strokeDasharray="3 3"
                          vertical={false}
                          stroke="#edf0f5"
                        />

                        <XAxis
                          dataKey="month"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fill: "#8490a3", fontSize: 12 }}
                        />

                        <YAxis
                          axisLine={false}
                          tickLine={false}
                          tick={{ fill: "#8490a3", fontSize: 11 }}
                          tickFormatter={(value) => `${value / 1000}k`}
                          width={45}
                        />

                        <Tooltip
                          formatter={(value) => formatMoney(value)}
                        />

                        <Area
                          type="monotone"
                          dataKey="sales"
                          stroke="#2563eb"
                          strokeWidth={3}
                          fill="url(#salesGradient)"
                          name="Ventas"
                        />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>

                  {!loading && chartData.length === 0 && (
                    <p className="empty-state">
                      No hay datos mensuales disponibles.
                    </p>
                  )}
                </div>

                <div className="panel category-panel">
                  <div className="panel-header">
                    <div>
                      <h3>Ventas por categoría</h3>
                      <p>Distribución de ingresos</p>
                    </div>
                  </div>

                  <div className="donut-container">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={categoriasFiltradas}
                          dataKey="value"
                          nameKey="name"
                          cx="50%"
                          cy="50%"
                          innerRadius={65}
                          outerRadius={92}
                          paddingAngle={4}
                          stroke="none"
                        >
                          {categoriasFiltradas.map((entry, index) => (
                            <Cell
                              key={entry.name}
                              fill={COLORS[index % COLORS.length]}
                            />
                          ))}
                        </Pie>

                        <Tooltip
                          formatter={(value) => formatMoney(value)}
                        />
                      </PieChart>
                    </ResponsiveContainer>

                    <div className="donut-center">
                      <strong>{formatMoney(totalCategorias)}</strong>
                      <span>Total</span>
                    </div>
                  </div>

                  <div className="category-legend">
                    {categoriasFiltradas.map((item, index) => {
                      const porcentaje =
                        totalCategorias > 0
                          ? (item.value / totalCategorias) * 100
                          : 0;

                      return (
                        <div className="category-row" key={item.name}>
                          <span className="category-name">
                            <i
                              style={{
                                backgroundColor:
                                  COLORS[index % COLORS.length],
                              }}
                            ></i>
                            {item.name}
                          </span>

                          <strong>{porcentaje.toFixed(1)}%</strong>
                        </div>
                      );
                    })}

                    {!loading && categoriasFiltradas.length === 0 && (
                      <p className="empty-state">
                        No hay datos por categoría.
                      </p>
                    )}
                  </div>
                </div>
              </section>

              <section className="bottom-grid">
                <div className="panel products-panel">
                  <div className="panel-header">
                    <div>
                      <h3>Productos destacados</h3>
                      <p>Información de productos</p>
                    </div>
                  </div>

                  <div className="empty-state">
                    Consulta el catálogo completo desde la sección Productos.
                  </div>
                </div>

                <div className="panel ranking-panel">
                  <div className="panel-header">
                    <div>
                      <h3>Rendimiento comercial</h3>
                      <p>Información de ventas</p>
                    </div>
                  </div>

                  <div className="empty-state">
                    Consulta el detalle de operaciones desde la sección Ventas.
                  </div>
                </div>
              </section>
            </>
          )}

          {/* PRONÓSTICO MACHINE LEARNING */}
          {activePage === "Pronóstico ML" && (
            <section>
              {mlError && (
                <div className="error-message">{mlError}</div>
              )}

              <div className="panel" style={{ padding: "24px", marginBottom: "22px" }}>
                <div className="panel-header">
                  <div>
                    <h3>
                      <BrainCircuit
                        size={20}
                        style={{ verticalAlign: "middle", marginRight: "8px" }}
                      />
                      Modelo de Machine Learning
                    </h3>
                    <p>
                      Predicción de ventas generada a partir del historial
                      comercial de EmpresaComercial.
                    </p>
                  </div>

                  <span className="chart-tag">
                    {modeloML || "Modelo predictivo"}
                  </span>
                </div>

                <p style={{ color: "#64748b", fontSize: "13px", marginTop: "15px" }}>
                  Algoritmo utilizado: {modeloML || "Cargando modelo..."}
                  {" · "}
                  Horizonte de predicción: {horizonteML} días
                </p>

                <button
                  className="export-button"
                  style={{ marginTop: "15px" }}
                  onClick={cargarPronostico}
                  disabled={mlLoading}
                >
                  <RefreshCw size={16} />
                  {mlLoading ? "Calculando..." : "Actualizar pronóstico"}
                </button>
              </div>

              <section className="metrics-grid">
                <MetricCard
                  title="Ventas pronosticadas"
                  value={formatMoney(totalPronosticado)}
                  icon={DollarSign}
                  description="Total esperado para el período"
                  loading={mlLoading}
                />

                <MetricCard
                  title="Promedio diario"
                  value={formatMoney(promedioPronosticado)}
                  icon={TrendingUp}
                  description="Venta promedio pronosticada"
                  loading={mlLoading}
                />

                <MetricCard
                  title="Días pronosticados"
                  value={formatNumber(pronostico.length)}
                  icon={CalendarDays}
                  description="Días incluidos en el modelo"
                  loading={mlLoading}
                />

                <MetricCard
                  title="Día de mayor venta"
                  value={mejorDia ? formatMoney(mejorDia.ventas) : "-"}
                  icon={Target}
                  description={
                    mejorDia
                      ? `Fecha: ${mejorDia.fecha}`
                      : "Sin información disponible"
                  }
                  loading={mlLoading}
                />
              </section>

              <div className="panel" style={{ padding: "24px", marginTop: "22px" }}>
                <div className="panel-header">
                  <div>
                    <h3>Pronóstico de ventas de los próximos días</h3>
                    <p>Valores estimados por el modelo Random Forest Regressor</p>
                  </div>
                  <span className="chart-tag">HNL</span>
                </div>

                {mlLoading ? (
                  <p className="empty-state">
                    Calculando pronóstico...
                  </p>
                ) : pronostico.length > 0 ? (
                  <div style={{ width: "100%", height: "350px", marginTop: "20px" }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart
                        data={pronostico}
                        margin={{
                          top: 10,
                          right: 20,
                          left: 10,
                          bottom: 10,
                        }}
                      >
                        <CartesianGrid
                          strokeDasharray="3 3"
                          vertical={false}
                          stroke="#edf0f5"
                        />

                        <XAxis
                          dataKey="fechaCorta"
                          axisLine={false}
                          tickLine={false}
                          tick={{ fill: "#8490a3", fontSize: 12 }}
                        />

                        <YAxis
                          axisLine={false}
                          tickLine={false}
                          tick={{ fill: "#8490a3", fontSize: 11 }}
                          tickFormatter={(value) => `${Math.round(value / 1000)}k`}
                          width={50}
                        />

                        <Tooltip
                          formatter={(value) => [
                            formatMoney(value),
                            "Ventas pronosticadas",
                          ]}
                          labelFormatter={(label) => `Fecha: ${label}`}
                        />

                        <Line
                          type="monotone"
                          dataKey="ventas"
                          name="Ventas pronosticadas"
                          stroke="#8b5cf6"
                          strokeWidth={3}
                          dot={{ r: 5, fill: "#8b5cf6" }}
                          activeDot={{ r: 7 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                ) : (
                  <p className="empty-state">
                    No hay pronósticos disponibles.
                  </p>
                )}
              </div>

              <div className="panel" style={{ padding: "24px", marginTop: "22px" }}>
                <div className="panel-header">
                  <div>
                    <h3>Detalle del pronóstico</h3>
                    <p>Estimación de ingresos por fecha</p>
                  </div>

                  <span className="chart-tag">
                    {pronostico.length} días
                  </span>
                </div>

                {pronostico.length > 0 ? (
                  <div style={{ overflowX: "auto", marginTop: "20px" }}>
                    <table
                      style={{
                        width: "100%",
                        borderCollapse: "collapse",
                        fontSize: "13px",
                        textAlign: "left",
                      }}
                    >
                      <thead>
                        <tr>
                          <th style={estiloEncabezado}>Fecha</th>
                          <th style={estiloEncabezado}>Ventas pronosticadas</th>
                        </tr>
                      </thead>

                      <tbody>
                        {pronostico.map((item) => (
                          <tr key={item.fecha}>
                            <td style={estiloCelda}>{item.fecha}</td>
                            <td style={estiloCelda}>
                              {formatMoney(item.ventas)}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  <p className="empty-state">
                    El detalle aparecerá cuando se cargue el pronóstico.
                  </p>
                )}
              </div>
            </section>
          )}

          {/* VENTAS, CLIENTES, PRODUCTOS, PAGOS, INVENTARIO Y DW */}
          {activePage !== "Dashboard" &&
            activePage !== "Pronóstico ML" && (
              <section className="panel" style={{ padding: "24px" }}>
                <div className="panel-header">
                  <div>
                    <h3>{activePage}</h3>
                    <p>
                      Información obtenida desde el Data Warehouse de
                      EmpresaComercial.
                    </p>
                  </div>

                  <span className="chart-tag">
                    {datosFiltrados.length} registros
                  </span>
                </div>

                {seccionLoading && (
                  <p className="empty-state">
                    Cargando información...
                  </p>
                )}

                {seccionError && (
                  <div className="error-message">
                    {seccionError}
                  </div>
                )}

                {!seccionLoading && !seccionError && (
                  <>
                    <div style={{ overflowX: "auto", marginTop: "20px" }}>
                      {datosFiltrados.length > 0 ? (
                        <table
                          style={{
                            width: "100%",
                            borderCollapse: "collapse",
                            fontSize: "13px",
                            textAlign: "left",
                          }}
                        >
                          <thead>
                            <tr>
                              {columnas.map((columna) => (
                                <th
                                  key={columna}
                                  style={estiloEncabezado}
                                >
                                  {columna
                                    .replaceAll("_", " ")
                                    .toUpperCase()}
                                </th>
                              ))}
                            </tr>
                          </thead>

                          <tbody>
                            {datosFiltrados.map((fila, index) => (
                              <tr key={index}>
                                {columnas.map((columna) => {
                                  const valor = fila[columna];

                                  return (
                                    <td
                                      key={columna}
                                      style={estiloCelda}
                                    >
                                      {valor === null || valor === undefined
                                        ? "-"
                                        : typeof valor === "boolean"
                                          ? valor ? "Sí" : "No"
                                          : String(valor)}
                                    </td>
                                  );
                                })}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      ) : (
                        <p className="empty-state">
                          {seccionDatos.length > 0
                            ? "No se encontraron resultados para la búsqueda."
                            : "No hay registros disponibles."}
                        </p>
                      )}
                    </div>

                    {seccionDatos.length > 0 && (
                      <p
                        style={{
                          marginTop: "16px",
                          color: "#8490a3",
                          fontSize: "12px",
                        }}
                      >
                        Datos consultados desde SQL Server · EmpresaComercial
                      </p>
                    )}
                  </>
                )}
              </section>
            )}

          <footer className="footer">
            <span>
              EmpresaComercial · Plataforma de Analítica Inteligente
            </span>
            <span>Data Warehouse · SQL Server</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

const estiloEncabezado = {
  padding: "13px 12px",
  background: "#f1f5f9",
  color: "#475569",
  borderBottom: "1px solid #e2e8f0",
  whiteSpace: "nowrap",
};

const estiloCelda = {
  padding: "13px 12px",
  borderBottom: "1px solid #edf0f5",
  color: "#475569",
  whiteSpace: "nowrap",
};

export default App;
