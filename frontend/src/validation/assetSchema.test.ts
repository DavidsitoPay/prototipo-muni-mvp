import { describe, expect, it } from "vitest";
import { assetSchema } from "./assetSchema";

const validAsset = {
  name: "Servidor de correo",
  type: "servidor",
  department: "Direccion de TI",
  criticality: "alta",
  status: "activo",
  owner: "Juan Perez",
  location: "on_prem",
};

describe("assetSchema", () => {
  it("accepts a fully valid asset", () => {
    const result = assetSchema.safeParse(validAsset);
    expect(result.success).toBe(true);
  });

  it("rejects a name shorter than 2 characters", () => {
    const result = assetSchema.safeParse({ ...validAsset, name: "A" });
    expect(result.success).toBe(false);
  });

  it("rejects an empty department", () => {
    const result = assetSchema.safeParse({ ...validAsset, department: "" });
    expect(result.success).toBe(false);
  });

  it("rejects an empty owner", () => {
    const result = assetSchema.safeParse({ ...validAsset, owner: "" });
    expect(result.success).toBe(false);
  });

  it("rejects a type outside the allowed enum", () => {
    const result = assetSchema.safeParse({ ...validAsset, type: "dron" });
    expect(result.success).toBe(false);
  });

  it("rejects a criticality outside the allowed enum", () => {
    const result = assetSchema.safeParse({ ...validAsset, criticality: "extrema" });
    expect(result.success).toBe(false);
  });

  it("rejects a location outside the allowed enum", () => {
    const result = assetSchema.safeParse({ ...validAsset, location: "luna" });
    expect(result.success).toBe(false);
  });
});
