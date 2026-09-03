import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../../auth/AuthContext";
import { MANAGE_ROLES } from "../../auth/roles";
import type { UserRole } from "../../types";

interface NavItem {
  to: string;
  label: string;
  roles?: UserRole[];
}

const NAV_ITEMS: NavItem[] = [
  { to: "/", label: "Dashboard" },
  { to: "/activos", label: "Activos", roles: MANAGE_ROLES },
  { to: "/riesgos", label: "Riesgos", roles: MANAGE_ROLES },
  { to: "/nist", label: "NIST", roles: MANAGE_ROLES },
  { to: "/reportes", label: "Reportes" },
];

const ROLE_LABELS: Record<UserRole, string> = {
  admin_ti: "Administrador TI",
  analista_riesgo: "Analista de Riesgo",
  directivo: "Directivo / Lectura",
};

export default function Shell() {
  const { user, logout } = useAuth();

  const visibleItems = NAV_ITEMS.filter((item) => !item.roles || (user && item.roles.includes(user.role)));

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-white border-b border-[var(--color-border)]">
        <div className="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <img src="/logo.webp" alt="Muniguate" className="h-9 w-auto" />
              <div>
                <span className="text-lg font-bold text-primary leading-tight block">Muniguate</span>
                <span className="hidden sm:block text-xs text-[var(--color-text-muted)]">
                  Gestión de Ciberseguridad Municipal
                </span>
              </div>
            </div>
            <nav className="flex gap-1">
              {visibleItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    `px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                      isActive
                        ? "bg-primary text-white"
                        : "text-[var(--color-text)] hover:bg-[var(--color-bg)]"
                    }`
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>
          </div>

          <div className="flex items-center gap-3">
            {user && (
              <div className="text-right hidden sm:block">
                <div className="text-sm font-medium">{user.display_name}</div>
                <div className="text-xs text-[var(--color-text-muted)]">{ROLE_LABELS[user.role]}</div>
              </div>
            )}
            <button
              onClick={logout}
              className="text-sm px-3 py-1.5 rounded-md border border-[var(--color-border)] hover:bg-[var(--color-bg)] transition-colors"
            >
              Salir
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 py-6">
        <Outlet />
      </main>
    </div>
  );
}
