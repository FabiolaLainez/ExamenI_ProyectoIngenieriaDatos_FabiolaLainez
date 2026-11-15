
import { useMemo, useState } from "react";
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
  TrendingUp,
  TrendingDown,
  DollarSign,
  Menu,
  ArrowUpRight,
  ArrowDownRight,
  Download,
  ChevronDown,
  CircleHelp,
} from "lucide-react";

import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
} from "recharts";

const salesData = [
  { month: "Ene", sales: 125000, previous: 98000 },
  { month: "Feb", sales: 148000, previous: 115000 },
  { month: "Mar", sales: 132000, previous: 120000 },
  { month: "Abr", sales: 175000, previous: 138000 },
  { month: "May", sales: 160000, previous: 142000 },
  { month: "Jun", sales: 195000, previous: 155000 },
  { month: "Jul", sales: 182000, previous: 160000 },
  { month: "Ago", sales: 215000, previous: 175000 },
  { month: "Sep", sales: 205000, previous: 182000 },
  { month: "Oct", sales: 238000, previous: 195000 },
  { month: "Nov", sales: 225000, previous: 205000 },
  { month: "Dic", sales: 270000, previous: 220000 },
];

const products = [
  { name: "Laptop Lenovo IdeaPad", category: "Tecnología", employee: "Carlos López", units: 145, revenue: 145000 },
  { name: "Mouse Logitech M170", category: "Accesorios", employee: "María García", units: 132, revenue: 26400 },
  { name: "Monitor Samsung 24”", category: "Tecnología", employee: "Carlos López", units: 98, revenue: 98000 },
  { name: "Teclado mecánico", category: "Accesorios", employee: "Ana Martínez", units: 86, revenue: 43000 },
  { name: "Impresora HP LaserJet", category: "Oficina", employee: "María García", units: 72, revenue: 86400 },
];

const categories = [
  { name: "Tecnología", value: 48 },
  { name: "Accesorios", value: 30 },
  { name: "Oficina", value: 22 },
];

const COLORS = ["#2563eb", "#14b8a6", "#f59e0b"];

const formatMoney = (value) =>
  new Intl.NumberFormat("es-HN", {
    style: "currency",
    currency: "HNL",
    maximumFractionDigits: 0,
  }).format(value);

function MetricCard({ title, value, change, positive, icon: Icon, description }) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span className="metric-title">{title}</span>
        <div className="metric-icon">
          <Icon size={19} />
        </div>
      </div>

      <div className="metric-value">{value}</div>

      <div className="metric-bottom">
        <span className={positive ? "change positive" : "change negative"}>
          {positive ? <ArrowUpRight size={15} /> : <ArrowDownRight size={15} />}
          {change}
        </span>
        <span className="metric-description">{description}</span>
      </div>
    </div>
  );
}

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [period, setPeriod] = useState("Anual");
  const [category, setCategory] = useState("Todas");
  const [employee, setEmployee] = useState("Todos");
  const [search, setSearch] = useState("");

  const visibleProducts = useMemo(() => {
    return products.filter((product) => {
      const matchesCategory = category === "Todas" || product.category === category;
      const matchesEmployee = employee === "Todos" || product.employee === employee;
      const matchesSearch = product.name.toLowerCase().includes(search.toLowerCase());

      return matchesCategory && matchesEmployee && matchesSearch;
    });
  }, [category, employee, search]);

  const chartData = useMemo(() => {
    if (period === "Últimos 6 meses") return salesData.slice(6);
    if (period === "Primer semestre") return salesData.slice(0, 6);
    return salesData;
  }, [period]);

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
                className={`nav-item ${activePage === item.label ? "active" : ""}`}
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
              <small>Conexión de demostración</small>
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
                placeholder="Buscar producto..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
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
              <h1>{activePage === "Dashboard" ? "Dashboard ejecutivo" : `Análisis de ${activePage}`}</h1>
              <p>Monitorea el rendimiento y comportamiento de tu empresa.</p>
            </div>

            <button className="export-button" onClick={() => window.print()}>
              <Download size={17} />
              Exportar
            </button>
          </section>

          <section className="filters-panel">
            <div className="filter-heading">
              <CalendarDays size={18} />
              <strong>Filtros de análisis</strong>
            </div>

            <div className="filter-controls">
              <label>
                Período
                <select value={period} onChange={(e) => setPeriod(e.target.value)}>
                  <option>Anual</option>
                  <option>Primer semestre</option>
                  <option>Últimos 6 meses</option>
                </select>
              </label>

              <label>
                Categoría
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                  <option>Todas</option>
                  <option>Tecnología</option>
                  <option>Accesorios</option>
                  <option>Oficina</option>
                </select>
              </label>

              <label>
                Empleado
                <select value={employee} onChange={(e) => setEmployee(e.target.value)}>
                  <option>Todos</option>
                  <option>Carlos López</option>
                  <option>María García</option>
                  <option>Ana Martínez</option>
                </select>
              </label>
            </div>
          </section>

          <section className="metrics-grid">
            <MetricCard
              title="Ventas totales"
              value="L 2,170,000"
              change="12.8%"
              positive
              icon={DollarSign}
              description="vs. período anterior"
            />
            <MetricCard
              title="Unidades vendidas"
              value="4,285"
              change="8.4%"
              positive
              icon={ShoppingCart}
              description="vs. período anterior"
            />
            <MetricCard
              title="Clientes registrados"
              value="100"
              change="5.2%"
              positive
              icon={Users}
              description="vs. período anterior"
            />
            <MetricCard
              title="Ticket promedio"
              value="L 4,340"
              change="2.1%"
              positive
              icon={CreditCard}
              description="vs. período anterior"
            />
          </section>

          <section className="charts-grid">
            <div className="panel sales-panel">
              <div className="panel-header">
                <div>
                  <h3>Evolución de ventas</h3>
                  <p>Comparación de ventas por mes</p>
                </div>
                <span className="chart-tag">HNL</span>
              </div>

              <div className="chart-legend">
                <span><i className="legend-dot blue"></i> Período actual</span>
                <span><i className="legend-dot gray"></i> Período anterior</span>
              </div>

              <div className="chart-area">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={chartData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                    <defs>
                      <linearGradient id="salesGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#2563eb" stopOpacity={0.22} />
                        <stop offset="100%" stopColor="#2563eb" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#edf0f5" />
                    <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{ fill: "#8490a3", fontSize: 12 }} />
                    <YAxis
                      axisLine={false}
                      tickLine={false}
                      tick={{ fill: "#8490a3", fontSize: 11 }}
                      tickFormatter={(value) => `${value / 1000}k`}
                      width={45}
                    />
                    <Tooltip formatter={(value) => formatMoney(value)} />
                    <Area type="monotone" dataKey="previous" stroke="#aab4c3" strokeWidth={2} strokeDasharray="5 5" fill="transparent" name="Período anterior" />
                    <Area type="monotone" dataKey="sales" stroke="#2563eb" strokeWidth={3} fill="url(#salesGradient)" name="Período actual" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="panel category-panel">
              <div className="panel-header">
                <div>
                  <h3>Ventas por categoría</h3>
                  <p>Distribución de ingresos</p>
                </div>
                <button className="more-button">•••</button>
              </div>

              <div className="donut-container">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={categories}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      innerRadius={65}
                      outerRadius={92}
                      paddingAngle={4}
                      stroke="none"
                    >
                      {categories.map((entry, index) => (
                        <Cell key={entry.name} fill={COLORS[index]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value) => `${value}%`} />
                  </PieChart>
                </ResponsiveContainer>
                <div className="donut-center">
                  <strong>100%</strong>
                  <span>Total</span>
                </div>
              </div>

              <div className="category-legend">
                {categories.map((item, index) => (
                  <div className="category-row" key={item.name}>
                    <span className="category-name">
                      <i style={{ backgroundColor: COLORS[index] }}></i>
                      {item.name}
                    </span>
                    <strong>{item.value}%</strong>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="bottom-grid">
            <div className="panel products-panel">
              <div className="panel-header">
                <div>
                  <h3>Productos destacados</h3>
                  <p>Rendimiento según los filtros seleccionados</p>
                </div>
                <button className="text-button">Ver todos <ArrowUpRight size={15} /></button>
              </div>

              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr>
                      <th>PRODUCTO</th>
                      <th>CATEGORÍA</th>
                      <th>UNIDADES</th>
                      <th>INGRESOS</th>
                    </tr>
                  </thead>
                  <tbody>
                    {visibleProducts.map((product) => (
                      <tr key={product.name}>
                        <td>
                          <div className="product-cell">
                            <div className="product-symbol"><Package size={17} /></div>
                            <strong>{product.name}</strong>
                          </div>
                        </td>
                        <td><span className="category-badge">{product.category}</span></td>
                        <td>{product.units}</td>
                        <td className="revenue-cell">{formatMoney(product.revenue)}</td>
                      </tr>
                    ))}
                    {visibleProducts.length === 0 && (
                      <tr>
                        <td colSpan="4" className="empty-state">No se encontraron productos.</td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="panel ranking-panel">
              <div className="panel-header">
                <div>
                  <h3>Rendimiento comercial</h3>
                  <p>Ingresos por empleado</p>
                </div>
              </div>

              <div className="ranking-chart">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    layout="vertical"
                    data={[
                      { name: "Carlos", value: 145000 },
                      { name: "María", value: 112000 },
                      { name: "Ana", value: 89000 },
                    ]}
                    margin={{ top: 5, right: 15, left: 5, bottom: 5 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#edf0f5" />
                    <XAxis type="number" hide />
                    <YAxis type="category" dataKey="name" axisLine={false} tickLine={false} tick={{ fill: "#64748b", fontSize: 12 }} width={55} />
                    <Tooltip formatter={(value) => formatMoney(value)} />
                    <Bar dataKey="value" fill="#2563eb" radius={[0, 6, 6, 0]} barSize={18} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>

          <footer className="footer">
            <span>EmpresaComercial · Plataforma de Analítica Inteligente</span>
            <span>Versión inicial · Datos de demostración</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

export default App;
