
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
  Sparkles,
  Send,
  Bot,
  User,
  Trash2,
} from "lucide-react";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
} from "recharts";

import {
  obtenerResumen,
  obtenerVentasMensuales,
  obtenerVentasCategoria,
  consultarIA,
  obtenerPronostico,
} from "./services/api";

const API_URL = "http://127.0.0.1:8000";

const COLORS = [
  "#2563eb",
  "#14b8a6",
  "#f59e0b",
  "#8b5cf6",
  "#ec4899",
];

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

// ======================================================
// COMPONENTE PRINCIPAL
// ======================================================

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

  // Estados de Gemini
  const [pregunta, setPregunta] = useState("");
  const [mensajes, setMensajes] = useState([]);
  const [iaLoading, setIaLoading] = useState(false);
  const [iaError, setIaError] = useState("");

  // Estados de Machine Learning
  const [pronostico, setPronostico] = useState(null);
  const [mlLoading, setMlLoading] = useState(false);
  const [mlError, setMlError] = useState("");

  // ======================================================
  // MENÚ
  // ======================================================

  const menuItems = [
    { label: "Dashboard", icon: LayoutDashboard },
    { label: "Ventas", icon: ShoppingCart },
    { label: "Clientes", icon: Users },
    { label: "Productos", icon: Package },
    { label: "Pagos", icon: CreditCard },
    { label: "Inventario", icon: BarChart3 },
    { label: "Data Warehouse", icon: Database },
    { label: "Pronóstico ML", icon: BrainCircuit },
    { label: "Asistente IA", icon: Sparkles },
  ];

  const endpoints = {
    Ventas: "/api/ventas",
    Clientes: "/api/clientes",
    Productos: "/api/productos",
    Pagos: "/api/pagos",
    Inventario: "/api/inventario",
    "Data Warehouse": "/api/datawarehouse",
  };

  // ======================================================
  // CARGAR DASHBOARD
  // ======================================================

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

  // ======================================================
  // CARGAR SECCIONES DEL DATA WAREHOUSE
  // ======================================================

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

  // ======================================================
  // MACHINE LEARNING
  // ======================================================

  const cargarPronostico = async () => {
    setMlLoading(true);
    setMlError("");

    try {
      const resultado = await obtenerPronostico();
      setPronostico(resultado);
    } catch (error) {
      setMlError(error.message);
    } finally {
      setMlLoading(false);
    }
  };

  // ======================================================
  // INTELIGENCIA ARTIFICIAL - GEMINI
  // ======================================================

  const enviarPregunta = async (texto = pregunta) => {
    const consulta = texto.trim();

    if (!consulta || iaLoading) return;

    setMensajes((anteriores) => [
      ...anteriores,
      {
        tipo: "usuario",
        texto: consulta,
      },
    ]);

    setPregunta("");
    setIaLoading(true);
    setIaError("");

    try {
      const resultado = await consultarIA(consulta);

      setMensajes((anteriores) => [
        ...anteriores,
        {
          tipo: "ia",
          texto: resultado.respuesta || "No se recibió una respuesta.",
        },
      ]);
    } catch (error) {
      setIaError(error.message);
    } finally {
      setIaLoading(false);
    }
  };

  const limpiarConversacion = () => {
    setMensajes([]);
    setIaError("");
    setPregunta("");
  };

  const preguntasSugeridas = [
    "¿Cuánto vendió la empresa en total?",
    "¿Cuál es la categoría que genera más ventas?",
    "¿Cómo se comportaron las ventas mensuales?",
    "¿Qué recomendaciones darías para aumentar las ventas?",
  ];

  // ======================================================
  // ACTUALIZAR INFORMACIÓN
  // ======================================================

  const actualizarDatos = () => {
    if (activePage === "Dashboard") {
      cargarDatos();
    } else if (activePage === "Pronóstico ML") {
      cargarPronostico();
    } else if (activePage !== "Asistente IA") {
      cargarDatosSeccion(activePage);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  useEffect(() => {
    if (endpoints[activePage]) {
      setSearch("");
      cargarDatosSeccion(activePage);
    }

    if (activePage === "Pronóstico ML") {
      cargarPronostico();
    }
  }, [activePage]);

  // ======================================================
  // FILTROS Y DATOS DERIVADOS
  // ======================================================

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

  const columnas =
    seccionDatos.length > 0
      ? Object.keys(seccionDatos[0])
      : [];

  const pronosticos = pronostico?.pronosticos || [];

  const totalPronosticado = pronosticos.reduce(
    (total, item) =>
      total + Number(item.ventas_pronosticadas || 0),
    0
  );

  const promedioPronosticado =
    pronosticos.length > 0
      ? totalPronosticado / pronosticos.length
      : 0;

  const diaMayorVenta = pronosticos.reduce(
    (mayor, item) =>
      Number(item.ventas_pronosticadas) >
      Number(mayor?.ventas_pronosticadas || 0)
        ? item
        : mayor,
    null
  );

  // ======================================================
  // INTERFAZ
  // ======================================================

  return (
    <div className="app-layout">

      {/* MENÚ LATERAL */}

      <aside className="sidebar">

        <div className="brand">
          <div className="brand-logo">EC</div>

          <div>
            <h2>EmpresaComercial</h2>
            <span>Business Intelligence</span>
          </div>
        </div>

        <div className="menu-label">
          MENÚ PRINCIPAL
        </div>

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

      {/* CONTENIDO PRINCIPAL */}

      <main className="main-content">

        {/* BARRA SUPERIOR */}

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

        {/* PÁGINAS */}

        <div className="page-container">

          {/* ENCABEZADO */}

          <section className="page-heading">

            <div>
              <div className="eyebrow">
                {activePage === "Dashboard"
                  ? "RESUMEN DEL NEGOCIO"
                  : activePage === "Pronóstico ML"
                    ? "ANALÍTICA PREDICTIVA"
                    : activePage === "Asistente IA"
                      ? "INTELIGENCIA ARTIFICIAL GENERATIVA"
                      : "GESTIÓN Y ANÁLISIS DE DATOS"}
              </div>

              <h1>
                {activePage === "Dashboard"
                  ? "Dashboard ejecutivo"
                  : activePage === "Pronóstico ML"
                    ? "Pronóstico de ventas"
                    : activePage === "Asistente IA"
                      ? "Asistente inteligente"
                      : `Análisis de ${activePage}`}
              </h1>

              <p>
                {activePage === "Asistente IA"
                  ? "Consulta y analiza la información de tu empresa utilizando Gemini."
                  : "Monitorea el rendimiento y comportamiento de tu empresa."}
              </p>
            </div>

            {activePage !== "Asistente IA" && (
              <button
                className="export-button"
                onClick={() => window.print()}
              >
                <Download size={17} />
                Exportar
              </button>
            )}

          </section>

          {/* ================================================== */}
          {/* DASHBOARD */}
          {/* ================================================== */}

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

                {/* VENTAS MENSUALES */}

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

                {/* VENTAS POR CATEGORÍA */}

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

          {/* ================================================== */}
          {/* MACHINE LEARNING */}
          {/* ================================================== */}

          {activePage === "Pronóstico ML" && (

            <>

              <section className="panel" style={{ padding: "24px" }}>

                <div className="panel-header">

                  <div>
                    <h3>
                      <BrainCircuit
                        size={20}
                        style={{
                          display: "inline",
                          verticalAlign: "middle",
                          marginRight: "8px",
                        }}
                      />
                      Modelo de Machine Learning
                    </h3>

                    <p>
                      Predicción de ventas generada a partir del historial comercial.
                    </p>
                  </div>

                  <span className="chart-tag">
                    {pronostico?.modelo || "RandomForestRegressor"}
                  </span>

                </div>

                <p style={{ marginTop: "16px", color: "#64748b" }}>
                  Algoritmo utilizado: {pronostico?.modelo || "RandomForestRegressor"}
                  {" · "}
                  Horizonte de predicción: {pronostico?.horizonte_dias || 7} días
                </p>

                <button
                  className="export-button"
                  style={{ marginTop: "18px" }}
                  onClick={cargarPronostico}
                  disabled={mlLoading}
                >
                  <RefreshCw size={17} />
                  {mlLoading ? "Actualizando..." : "Actualizar pronóstico"}
                </button>

              </section>

              {mlError && (
                <div className="error-message" style={{ marginTop: "20px" }}>
                  {mlError}
                </div>
              )}

              {mlLoading && (
                <div className="panel empty-state" style={{ marginTop: "20px" }}>
                  Cargando pronóstico...
                </div>
              )}

              {!mlLoading && pronostico && (

                <>

                  <section className="metrics-grid" style={{ marginTop: "22px" }}>

                    <MetricCard
                      title="Ventas pronosticadas"
                      value={formatMoney(totalPronosticado)}
                      icon={DollarSign}
                      description="Total esperado para el período"
                      loading={false}
                    />

                    <MetricCard
                      title="Promedio diario"
                      value={formatMoney(promedioPronosticado)}
                      icon={BarChart3}
                      description="Venta promedio pronosticada"
                      loading={false}
                    />

                    <MetricCard
                      title="Días pronosticados"
                      value={formatNumber(pronosticos.length)}
                      icon={CalendarDays}
                      description="Días incluidos en el modelo"
                      loading={false}
                    />

                    <MetricCard
                      title="Día de mayor venta"
                      value={formatMoney(diaMayorVenta?.ventas_pronosticadas)}
                      icon={DollarSign}
                      description={`Fecha: ${diaMayorVenta?.fecha || "-"}`}
                      loading={false}
                    />

                  </section>

                  <section className="panel" style={{ padding: "24px", marginTop: "22px" }}>

                    <div className="panel-header">
                      <div>
                        <h3>Pronóstico de ventas de los próximos días</h3>
                        <p>
                          Valores estimados por el modelo de Machine Learning
                        </p>
                      </div>

                      <span className="chart-tag">HNL</span>
                    </div>

                    <div style={{ width: "100%", height: "330px", marginTop: "20px" }}>

                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={pronosticos}>

                          <CartesianGrid
                            strokeDasharray="3 3"
                            vertical={false}
                          />

                          <XAxis
                            dataKey="fecha"
                            tick={{ fontSize: 11 }}
                          />

                          <YAxis
                            tickFormatter={(value) => `${value / 1000}k`}
                          />

                          <Tooltip
                            formatter={(value) => formatMoney(value)}
                          />

                          <Bar
                            dataKey="ventas_pronosticadas"
                            name="Ventas pronosticadas"
                            fill="#2563eb"
                            radius={[6, 6, 0, 0]}
                          />

                        </BarChart>
                      </ResponsiveContainer>

                    </div>

                  </section>

                </>

              )}

            </>

          )}

          {/* ================================================== */}
          {/* ASISTENTE IA - GEMINI */}
          {/* ================================================== */}

          {activePage === "Asistente IA" && (

            <section
              className="panel"
              style={{
                padding: "24px",
                minHeight: "580px",
                display: "flex",
                flexDirection: "column",
              }}
            >

              {/* ENCABEZADO DEL CHAT */}

              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  gap: "12px",
                  flexWrap: "wrap",
                  paddingBottom: "20px",
                  borderBottom: "1px solid #edf0f5",
                }}
              >

                <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>

                  <div
                    style={{
                      width: "46px",
                      height: "46px",
                      borderRadius: "14px",
                      background: "#eaf2ff",
                      color: "#2563eb",
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "center",
                    }}
                  >
                    <Sparkles size={24} />
                  </div>

                  <div>
                    <h3 style={{ margin: 0 }}>Gemini Business Assistant</h3>

                    <p style={{ margin: "5px 0 0", color: "#8490a3", fontSize: "13px" }}>
                      Inteligencia artificial conectada al Data Warehouse
                    </p>
                  </div>

                </div>

                <button
                  onClick={limpiarConversacion}
                  disabled={mensajes.length === 0 || iaLoading}
                  style={{
                    border: "1px solid #e2e8f0",
                    background: "#fff",
                    color: "#475569",
                    padding: "9px 13px",
                    borderRadius: "9px",
                    cursor: "pointer",
                    display: "flex",
                    alignItems: "center",
                    gap: "7px",
                  }}
                >
                  <Trash2 size={15} />
                  Limpiar conversación
                </button>

              </div>

              {/* MENSAJE DE BIENVENIDA */}

              {mensajes.length === 0 && (

                <div
                  style={{
                    textAlign: "center",
                    padding: "45px 15px 25px",
                  }}
                >

                  <div
                    style={{
                      width: "66px",
                      height: "66px",
                      borderRadius: "20px",
                      background: "#eaf2ff",
                      color: "#2563eb",
                      display: "inline-flex",
                      alignItems: "center",
                      justifyContent: "center",
                      marginBottom: "16px",
                    }}
                  >
                    <Bot size={34} />
                  </div>

                  <h2 style={{ color: "#17243a", fontSize: "22px" }}>
                    ¿En qué puedo ayudarte?
                  </h2>

                  <p
                    style={{
                      color: "#8490a3",
                      maxWidth: "480px",
                      margin: "0 auto 25px",
                      lineHeight: 1.6,
                    }}
                  >
                    Pregúntame sobre las ventas, clientes, categorías y
                    comportamiento comercial de EmpresaComercial.
                    Analizaré los datos disponibles para darte respuestas
                    y recomendaciones.
                  </p>

                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))",
                      gap: "12px",
                      maxWidth: "800px",
                      margin: "0 auto",
                    }}
                  >

                    {preguntasSugeridas.map((texto) => (

                      <button
                        key={texto}
                        onClick={() => enviarPregunta(texto)}
                        disabled={iaLoading}
                        style={{
                          background: "#fff",
                          border: "1px solid #e2e8f0",
                          borderRadius: "11px",
                          padding: "14px",
                          color: "#475569",
                          textAlign: "left",
                          cursor: "pointer",
                          fontSize: "13px",
                          lineHeight: 1.5,
                        }}
                      >
                        <Sparkles
                          size={15}
                          style={{
                            color: "#2563eb",
                            marginBottom: "8px",
                          }}
                        />

                        <br />

                        {texto}

                      </button>

                    ))}

                  </div>

                </div>

              )}

              {/* CONVERSACIÓN */}

              {mensajes.length > 0 && (

                <div
                  style={{
                    flex: 1,
                    padding: "22px 5px",
                    display: "flex",
                    flexDirection: "column",
                    gap: "20px",
                    maxHeight: "440px",
                    overflowY: "auto",
                  }}
                >

                  {mensajes.map((mensaje, index) => (

                    <div
                      key={index}
                      style={{
                        display: "flex",
                        justifyContent:
                          mensaje.tipo === "usuario"
                            ? "flex-end"
                            : "flex-start",
                        gap: "10px",
                        alignItems: "flex-start",
                      }}
                    >

                      {mensaje.tipo === "ia" && (
                        <div
                          style={{
                            background: "#eaf2ff",
                            color: "#2563eb",
                            width: "34px",
                            height: "34px",
                            borderRadius: "10px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                          }}
                        >
                          <Bot size={19} />
                        </div>
                      )}

                      <div
                        style={{
                          maxWidth: "82%",
                          background:
                            mensaje.tipo === "usuario"
                              ? "#2563eb"
                              : "#f5f7fb",
                          color:
                            mensaje.tipo === "usuario"
                              ? "#fff"
                              : "#334155",
                          padding: "14px 17px",
                          borderRadius: "13px",
                          lineHeight: 1.7,
                          fontSize: "14px",
                          whiteSpace: "pre-wrap",
                          overflowWrap: "anywhere",
                        }}
                      >
                        {mensaje.texto}
                      </div>

                      {mensaje.tipo === "usuario" && (
                        <div
                          style={{
                            background: "#e2e8f0",
                            color: "#475569",
                            width: "34px",
                            height: "34px",
                            borderRadius: "10px",
                            display: "flex",
                            alignItems: "center",
                            justifyContent: "center",
                            flexShrink: 0,
                          }}
                        >
                          <User size={18} />
                        </div>
                      )}

                    </div>

                  ))}

                  {iaLoading && (

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "10px",
                        color: "#64748b",
                        fontSize: "13px",
                      }}
                    >
                      <Bot size={20} />
                      Gemini está analizando los datos...
                    </div>

                  )}

                </div>

              )}

              {/* ERROR DE IA */}

              {iaError && (
                <div
                  className="error-message"
                  style={{ marginBottom: "12px" }}
                >
                  {iaError}
                </div>
              )}

              {/* CAJA PARA ESCRIBIR */}

              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  enviarPregunta();
                }}
                style={{
                  display: "flex",
                  gap: "10px",
                  alignItems: "center",
                  marginTop: "auto",
                  paddingTop: "18px",
                  borderTop: "1px solid #edf0f5",
                }}
              >

                <input
                  type="text"
                  value={pregunta}
                  onChange={(e) => setPregunta(e.target.value)}
                  placeholder="Escribe tu pregunta sobre la empresa..."
                  disabled={iaLoading}
                  style={{
                    flex: 1,
                    minWidth: 0,
                    border: "1px solid #dbe3ef",
                    borderRadius: "11px",
                    padding: "14px 16px",
                    outline: "none",
                    fontSize: "14px",
                  }}
                />

                <button
                  type="submit"
                  disabled={!pregunta.trim() || iaLoading}
                  style={{
                    background: "#2563eb",
                    color: "#fff",
                    border: "none",
                    borderRadius: "11px",
                    padding: "14px 18px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    gap: "8px",
                    cursor: "pointer",
                    opacity:
                      !pregunta.trim() || iaLoading ? 0.5 : 1,
                  }}
                >
                  <Send size={17} />
                  Enviar
                </button>

              </form>

              <p
                style={{
                  textAlign: "center",
                  color: "#94a3b8",
                  fontSize: "11px",
                  margin: "12px 0 0",
                }}
              >
                Gemini utiliza información resumida del Data Warehouse.
                Verifica los datos antes de tomar decisiones empresariales.
              </p>

            </section>

          )}

          {/* ================================================== */}
          {/* VENTAS, CLIENTES, PRODUCTOS, PAGOS, INVENTARIO Y DW */}
          {/* ================================================== */}

          {endpoints[activePage] && (

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
                                style={{
                                  padding: "13px 12px",
                                  background: "#f1f5f9",
                                  color: "#475569",
                                  borderBottom: "1px solid #e2e8f0",
                                  whiteSpace: "nowrap",
                                }}
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
                                    style={{
                                      padding: "13px 12px",
                                      borderBottom: "1px solid #edf0f5",
                                      color: "#475569",
                                      whiteSpace: "nowrap",
                                    }}
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

          {/* PIE DE PÁGINA */}

          <footer className="footer">

            <span>
              EmpresaComercial · Plataforma de Analítica Inteligente
            </span>

            <span>
              Data Warehouse · SQL Server · Gemini AI
            </span>

          </footer>

        </div>
      </main>
    </div>
  );
}

export default App;