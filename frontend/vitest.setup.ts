import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";
import "@testing-library/jest-dom/vitest";

// jsdom no implementa ResizeObserver; recharts (ResponsiveContainer) lo necesita
// y sin este stub el efecto lanza y React desmonta todo el arbol en los tests.
global.ResizeObserver ??= class {
  observe() {
    // no-op: jsdom no mide layout real
  }
  unobserve() {
    // no-op
  }
  disconnect() {
    // no-op
  }
};

afterEach(() => {
  cleanup();
});
