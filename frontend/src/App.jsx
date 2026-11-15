
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
} from "recharts";

import {
  obtenerResumen,
  obtenerVentasMensuales,
  obtenerVentasCategoria,
} from "./services/api";

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

    const nombreMes =
      numeroMes >= 1 && numeroMes <= 12
        ? MESES[numeroMes - 1]
        : String(mes).substring(0, 3);

    return {
      month: nombreMes,
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

  useEffect(() => {
    cargarDatos();
  }, []);

  const chartData = useMemo(() => {
    if (period === "Primer semestre") {
      return ventasMensuales.slice(0, 6);
    }

    if (period === "Últimos 6 meses") {
      return ventasMensuales.slice(-6);
    }

    return ventasMensuales;
  }, [period, ventasMensuales]);

  const categoriasDisponibles = useMemo(() => {
    return ventasCategoria.map((item) => item.name);
  }, [ventasCategoria]);

  const categoriasFiltradas = useMemo(() => {
    if (category === "Todas") return ventasCategoria;

    return ventasCategoria.filter((item) => item.name === category);
  }, [category, ventasCategoria]);

  const totalCategorias = categoriasFiltradas.reduce(
    (total, item) => total + item.value,
    0
  );

  const menuItems = [
    { label: "Dashboard", icon: LayoutDashboard },
    { label: "Ventas", icon: ShoppingCart },
    { label: "Clientes", icon: Users },
    { label: "Productos", icon: Package },
    { label: "Pagos", icon: CreditCard },
    { label: "Inventario", icon: BarChart3 },
  ];

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
              onClick={cargarDatos}
              title="Actualizar datos"
            >
              <RefreshCw size={18} />
            </button>

            <button className="icon-button" aria-label="Notificaciones">
              <Bell size={19} />
              <span className="notification-dot"></span>
            </button>

            <div className="top-avatar">FL</div>
          </div>
        </header>

        <div className="page-container">
          <section className="page-heading">
            <div>
              <div className="eyebrow">RESUMEN DEL NEGOCIO</div>
              <h1>
                {activePage === "Dashboard"
                  ? "Dashboard ejecutivo"
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

          {error && (
            <div className="error-message">
              {error}
            </div>
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
                    margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
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
                  <strong>
                    {formatMoney(totalCategorias)}
                  </strong>
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
                  <p>Información pendiente de conexión con la API</p>
                </div>
              </div>

              <div className="empty-state">
                Próximamente conectaremos el análisis de productos
                directamente con el Data Warehouse.
              </div>
            </div>

            <div className="panel ranking-panel">
              <div className="panel-header">
                <div>
                  <h3>Rendimiento comercial</h3>
                  <p>Información pendiente de conexión con la API</p>
                </div>
              </div>

              <div className="empty-state">
                Próximamente conectaremos el análisis por empleado.
              </div>
            </div>
          </section>

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

export default App;
