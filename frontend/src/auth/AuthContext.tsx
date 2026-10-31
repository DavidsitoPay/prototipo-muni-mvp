import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { fetchMe, login as apiLogin } from "../api/auth";
import type { User, UserRole } from "../types";

const VALID_ROLES: Set<UserRole> = new Set(["admin_ti", "analista_riesgo", "directivo"]);
// Allowlist de caracteres para texto libre persistido en localStorage
// (username, display_name): si el valor no calza, se rechaza en vez de
// limpiarlo, para no guardar silenciosamente una versión mutilada de lo
// que mandó el backend.
const SAFE_FREE_TEXT = /^[\p{L}\p{N}\s.@_()-]{1,200}$/u;

function isValidUser(value: unknown): value is User {
  if (typeof value !== "object" || value === null) return false;
  const candidate = value as Record<string, unknown>;
  return (
    typeof candidate.id === "string" &&
    candidate.id.length > 0 &&
    typeof candidate.username === "string" &&
    candidate.username.length > 0 &&
    typeof candidate.display_name === "string" &&
    typeof candidate.role === "string" &&
    VALID_ROLES.has(candidate.role as UserRole)
  );
}

interface AuthContextValue {
  user: User | null;
  isAuthenticated: boolean;
  isCheckingSession: boolean;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function loadStoredUser(): User | null {
  if (!localStorage.getItem("sgcm_token")) return null;
  const raw = localStorage.getItem("sgcm_user");
  if (!raw) return null;
  try {
    const parsed: unknown = JSON.parse(raw);
    return isValidUser(parsed) ? parsed : null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: Readonly<{ children: ReactNode }>) {
  const [user, setUser] = useState<User | null>(loadStoredUser);
  const [isCheckingSession, setIsCheckingSession] = useState(true);

  const logout = useCallback(() => {
    localStorage.removeItem("sgcm_token");
    localStorage.removeItem("sgcm_user");
    setUser(null);
  }, []);

  useEffect(() => {
    // Revalida contra el backend en cada carga: localStorage puede tener un
    // usuario "en caché" cuyo token ya expiró o fue invalidado en el server.
    if (!localStorage.getItem("sgcm_token")) {
      setIsCheckingSession(false);
      return;
    }
    fetchMe()
      .then((rawUser) => {
        if (!isValidUser(rawUser)) {
          logout();
          return;
        }
        const username = rawUser.username;
        const displayName = rawUser.display_name;
        if (!SAFE_FREE_TEXT.test(username) || !SAFE_FREE_TEXT.test(displayName)) {
          logout();
          return;
        }
        const safeUser: User = { id: rawUser.id, username, display_name: displayName, role: rawUser.role };
        setUser(safeUser);
        localStorage.setItem("sgcm_user", JSON.stringify(safeUser));
      })
      .catch(() => logout())
      .finally(() => setIsCheckingSession(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const response = await apiLogin(username, password);
    if (!isValidUser(response.user)) {
      throw new Error("Respuesta de login inválida");
    }
    const safeUsername = response.user.username;
    const safeDisplayName = response.user.display_name;
    if (!SAFE_FREE_TEXT.test(safeUsername) || !SAFE_FREE_TEXT.test(safeDisplayName)) {
      throw new Error("Respuesta de login inválida");
    }
    const safeUser: User = {
      id: response.user.id,
      username: safeUsername,
      display_name: safeDisplayName,
      role: response.user.role,
    };
    localStorage.setItem("sgcm_token", response.access_token);
    localStorage.setItem("sgcm_user", JSON.stringify(safeUser));
    setUser(safeUser);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isAuthenticated: user !== null, isCheckingSession, login, logout }),
    [user, isCheckingSession, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de AuthProvider");
  return ctx;
}
