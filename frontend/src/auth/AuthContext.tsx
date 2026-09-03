import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import { fetchMe, login as apiLogin } from "../api/auth";
import type { User } from "../types";

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
    const parsed = JSON.parse(raw);
    if (parsed && typeof parsed.id === "string" && typeof parsed.role === "string") {
      return parsed as User;
    }
    return null;
  } catch {
    return null;
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
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
      .then((freshUser) => {
        setUser(freshUser);
        localStorage.setItem("sgcm_user", JSON.stringify(freshUser));
      })
      .catch(() => logout())
      .finally(() => setIsCheckingSession(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const response = await apiLogin(username, password);
    localStorage.setItem("sgcm_token", response.access_token);
    localStorage.setItem("sgcm_user", JSON.stringify(response.user));
    setUser(response.user);
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
