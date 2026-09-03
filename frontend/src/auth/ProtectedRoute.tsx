import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import type { UserRole } from "../types";
import { useAuth } from "./AuthContext";

export function ProtectedRoute({
  children,
  allowedRoles,
}: {
  children: ReactNode;
  allowedRoles?: UserRole[];
}) {
  const { user, isAuthenticated, isCheckingSession } = useAuth();

  if (isCheckingSession) {
    return <div className="min-h-screen flex items-center justify-center text-sm text-[var(--color-text-muted)]">Verificando sesión...</div>;
  }

  if (!isAuthenticated || !user) {
    return <Navigate to="/login" replace />;
  }

  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to="/" replace />;
  }

  return <>{children}</>;
}
