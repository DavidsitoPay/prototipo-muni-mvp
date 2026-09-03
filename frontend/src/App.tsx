import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AuthProvider } from "./auth/AuthContext";
import LoginPage from "./auth/LoginPage";
import { ProtectedRoute } from "./auth/ProtectedRoute";
import { MANAGE_ROLES } from "./auth/roles";
import Shell from "./components/layout/Shell";
import AssetDetailPage from "./pages/AssetDetailPage";
import AssetsPage from "./pages/AssetsPage";
import DashboardPage from "./pages/DashboardPage";
import NistPage from "./pages/NistPage";
import ReportsPage from "./pages/ReportsPage";
import RiesgosPage from "./pages/RiesgosPage";

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 10_000 } },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route
              element={
                <ProtectedRoute>
                  <Shell />
                </ProtectedRoute>
              }
            >
              <Route path="/" element={<DashboardPage />} />
              <Route
                path="/activos"
                element={
                  <ProtectedRoute allowedRoles={MANAGE_ROLES}>
                    <AssetsPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/activos/:assetId"
                element={
                  <ProtectedRoute allowedRoles={MANAGE_ROLES}>
                    <AssetDetailPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/riesgos"
                element={
                  <ProtectedRoute allowedRoles={MANAGE_ROLES}>
                    <RiesgosPage />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/nist"
                element={
                  <ProtectedRoute allowedRoles={MANAGE_ROLES}>
                    <NistPage />
                  </ProtectedRoute>
                }
              />
              <Route path="/reportes" element={<ReportsPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
