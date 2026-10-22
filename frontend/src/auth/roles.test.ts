import { describe, expect, it } from "vitest";
import type { User } from "../types";
import { ASSET_WRITE_ROLES, hasAnyRole, MANAGE_ROLES } from "./roles";

function userWith(role: User["role"]): User {
  return { id: "u1", username: "demo", role, display_name: "Usuario demo" };
}

describe("hasAnyRole", () => {
  it("returns false for a null user", () => {
    expect(hasAnyRole(null, MANAGE_ROLES)).toBe(false);
  });

  it("returns true when the user's role is in the allowed list", () => {
    expect(hasAnyRole(userWith("admin_ti"), MANAGE_ROLES)).toBe(true);
  });

  it("returns false when the user's role is not in the allowed list", () => {
    expect(hasAnyRole(userWith("directivo"), MANAGE_ROLES)).toBe(false);
  });

  it("returns false for an empty allowed-roles list regardless of user", () => {
    expect(hasAnyRole(userWith("admin_ti"), [])).toBe(false);
  });
});

describe("role constants", () => {
  it("MANAGE_ROLES includes admin_ti and analista_riesgo but not directivo", () => {
    expect(MANAGE_ROLES).toContain("admin_ti");
    expect(MANAGE_ROLES).toContain("analista_riesgo");
    expect(MANAGE_ROLES).not.toContain("directivo");
  });

  it("ASSET_WRITE_ROLES only includes admin_ti", () => {
    expect(ASSET_WRITE_ROLES).toEqual(["admin_ti"]);
  });

  it("analista_riesgo can manage NIST/vulnerabilities but not write assets", () => {
    const analista = userWith("analista_riesgo");
    expect(hasAnyRole(analista, MANAGE_ROLES)).toBe(true);
    expect(hasAnyRole(analista, ASSET_WRITE_ROLES)).toBe(false);
  });
});
