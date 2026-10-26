import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import type { User } from "../types";

const { login: apiLogin, fetchMe } = vi.hoisted(() => ({
  login: vi.fn(),
  fetchMe: vi.fn(),
}));

vi.mock("../api/auth", () => ({ login: apiLogin, fetchMe }));

import { AuthProvider, useAuth } from "./AuthContext";

const VALID_USER: User = {
  id: "u1",
  username: "demo.user",
  display_name: "Usuario Demo",
  role: "admin_ti",
};

function Harness() {
  const { user, isAuthenticated, isCheckingSession, login, logout } = useAuth();
  return (
    <div>
      <span data-testid="checking">{String(isCheckingSession)}</span>
      <span data-testid="authed">{String(isAuthenticated)}</span>
      <span data-testid="username">{user?.username ?? ""}</span>
      <button onClick={() => login("demo.user", "pw").catch(() => undefined)}>login</button>
      <button onClick={logout}>logout</button>
    </div>
  );
}

function renderHarness() {
  return render(
    <AuthProvider>
      <Harness />
    </AuthProvider>
  );
}

async function waitForCheckDone() {
  await waitFor(() => expect(screen.getByTestId("checking")).toHaveTextContent("false"));
}

describe("AuthProvider - session restore", () => {
  beforeEach(() => {
    localStorage.clear();
    apiLogin.mockReset();
    fetchMe.mockReset();
  });

  it("starts unauthenticated with no stored session and never calls fetchMe", async () => {
    renderHarness();
    await waitForCheckDone();
    expect(screen.getByTestId("authed")).toHaveTextContent("false");
    expect(fetchMe).not.toHaveBeenCalled();
  });

  it("discards a corrupted stored user payload instead of throwing", async () => {
    localStorage.setItem("sgcm_token", "t1");
    localStorage.setItem("sgcm_user", "{not-valid-json");
    fetchMe.mockRejectedValue(new Error("network down"));

    renderHarness();
    await waitForCheckDone();

    expect(screen.getByTestId("authed")).toHaveTextContent("false");
  });

  it("revalidates a stored session and keeps the user when the backend confirms it", async () => {
    localStorage.setItem("sgcm_token", "t1");
    localStorage.setItem("sgcm_user", JSON.stringify(VALID_USER));
    fetchMe.mockResolvedValue(VALID_USER);

    renderHarness();
    await waitForCheckDone();

    expect(screen.getByTestId("authed")).toHaveTextContent("true");
    expect(screen.getByTestId("username")).toHaveTextContent("demo.user");
    expect(JSON.parse(localStorage.getItem("sgcm_user")!)).toEqual(VALID_USER);
  });

  it("logs out when the backend reports a malformed user shape", async () => {
    localStorage.setItem("sgcm_token", "t1");
    localStorage.setItem("sgcm_user", JSON.stringify(VALID_USER));
    fetchMe.mockResolvedValue({ id: "u1" });

    renderHarness();
    await waitForCheckDone();

    expect(screen.getByTestId("authed")).toHaveTextContent("false");
    expect(localStorage.getItem("sgcm_token")).toBeNull();
  });

  it("logs out when the backend user has free text outside the safe allowlist", async () => {
    localStorage.setItem("sgcm_token", "t1");
    localStorage.setItem("sgcm_user", JSON.stringify(VALID_USER));
    fetchMe.mockResolvedValue({ ...VALID_USER, username: "bad<script>" });

    renderHarness();
    await waitForCheckDone();

    expect(screen.getByTestId("authed")).toHaveTextContent("false");
    expect(localStorage.getItem("sgcm_user")).toBeNull();
  });

  it("logs out when the revalidation request fails", async () => {
    localStorage.setItem("sgcm_token", "t1");
    localStorage.setItem("sgcm_user", JSON.stringify(VALID_USER));
    fetchMe.mockRejectedValue(new Error("network down"));

    renderHarness();
    await waitForCheckDone();

    expect(screen.getByTestId("authed")).toHaveTextContent("false");
    expect(localStorage.getItem("sgcm_token")).toBeNull();
  });
});

describe("AuthProvider - login", () => {
  const user = userEvent.setup();

  beforeEach(() => {
    localStorage.clear();
    apiLogin.mockReset();
    fetchMe.mockReset();
  });

  it("logs in and persists the user when the response is valid and safe", async () => {
    apiLogin.mockResolvedValue({ access_token: "tok", token_type: "bearer", user: VALID_USER });

    renderHarness();
    await waitForCheckDone();
    await user.click(screen.getByText("login"));

    await waitFor(() => expect(screen.getByTestId("authed")).toHaveTextContent("true"));
    expect(localStorage.getItem("sgcm_token")).toBe("tok");
    expect(JSON.parse(localStorage.getItem("sgcm_user")!)).toEqual(VALID_USER);
  });

  it("rejects a login response with a malformed user shape and stores nothing", async () => {
    apiLogin.mockResolvedValue({ access_token: "tok", token_type: "bearer", user: { id: "u1" } });

    renderHarness();
    await waitForCheckDone();
    await user.click(screen.getByText("login"));

    await waitFor(() => expect(apiLogin).toHaveBeenCalled());
    expect(screen.getByTestId("authed")).toHaveTextContent("false");
    expect(localStorage.getItem("sgcm_token")).toBeNull();
  });

  it("rejects a login response whose free text is outside the safe allowlist", async () => {
    apiLogin.mockResolvedValue({
      access_token: "tok",
      token_type: "bearer",
      user: { ...VALID_USER, display_name: "no permitido <>" },
    });

    renderHarness();
    await waitForCheckDone();
    await user.click(screen.getByText("login"));

    await waitFor(() => expect(apiLogin).toHaveBeenCalled());
    expect(screen.getByTestId("authed")).toHaveTextContent("false");
    expect(localStorage.getItem("sgcm_token")).toBeNull();
  });
});

describe("useAuth", () => {
  it("throws when used outside an AuthProvider", () => {
    const Broken = () => {
      useAuth();
      return null;
    };
    expect(() => render(<Broken />)).toThrow("useAuth debe usarse dentro de AuthProvider");
  });
});
