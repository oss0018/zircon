import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from './store/authStore'
import Layout from './components/layout/Layout'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import DashboardPage from './pages/DashboardPage'
import FilesPage from './pages/FilesPage'
import SearchPage from './pages/SearchPage'
import IntegrationsPage from './pages/IntegrationsPage'
import MonitoringPage from './pages/MonitoringPage'
import BrandProtectionPage from './pages/BrandProtectionPage'

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.token)
  return token ? <>{children}</> : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<DashboardPage />} />
          <Route path="files" element={<FilesPage />} />
          <Route path="search" element={<SearchPage />} />
          <Route path="integrations" element={<IntegrationsPage />} />
          <Route path="monitoring" element={<MonitoringPage />} />
          <Route path="brand" element={<BrandProtectionPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
