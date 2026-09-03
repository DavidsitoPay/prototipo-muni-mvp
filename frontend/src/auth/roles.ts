import type { User, UserRole } from "../types";

/** Roles que pueden crear/editar/eliminar activos, vulnerabilidades y NIST. */
export const MANAGE_ROLES: UserRole[] = ["admin_ti", "analista_riesgo"];

/** Solo Administrador TI puede crear/editar/eliminar activos (no analista_riesgo). */
export const ASSET_WRITE_ROLES: UserRole[] = ["admin_ti"];

export function hasAnyRole(user: User | null, roles: UserRole[]): boolean {
  return user !== null && roles.includes(user.role);
}
