import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom"
import { ProtectedRoute } from "@/components/ProtectedRoute"
import { AppLayout } from "@/components/AppLayout"
import { LoginPage } from "@/pages/LoginPage"
import { DashboardPage } from "@/pages/DashboardPage"
import { ClientesPage } from "@/pages/clientes/ClientesPage"
import { ClienteFormPage } from "@/pages/clientes/ClienteFormPage"
import { VeiculosPage } from "@/pages/veiculos/VeiculosPage"
import { VeiculoFormPage } from "@/pages/veiculos/VeiculoFormPage"
import { OleosPage } from "@/pages/oleos/OleosPage"
import { OleoFormPage } from "@/pages/oleos/OleoFormPage"
import { PecasPage } from "@/pages/pecas/PecasPage"
import { PecaFormPage } from "@/pages/pecas/PecaFormPage"
import { ServicosPage } from "@/pages/servicos/ServicosPage"
import { ServicoFormPage } from "@/pages/servicos/ServicoFormPage"
import { TrocasPage } from "@/pages/trocas/TrocasPage"
import { TrocaFormPage } from "@/pages/trocas/TrocaFormPage"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/" element={<DashboardPage />} />

            <Route path="/clientes" element={<ClientesPage />} />
            <Route path="/clientes/novo" element={<ClienteFormPage />} />
            <Route path="/clientes/:id/editar" element={<ClienteFormPage />} />

            <Route path="/veiculos" element={<VeiculosPage />} />
            <Route path="/veiculos/novo" element={<VeiculoFormPage />} />
            <Route path="/veiculos/:id/editar" element={<VeiculoFormPage />} />

            <Route path="/oleos" element={<OleosPage />} />
            <Route path="/oleos/novo" element={<OleoFormPage />} />
            <Route path="/oleos/:id/editar" element={<OleoFormPage />} />

            <Route path="/pecas" element={<PecasPage />} />
            <Route path="/pecas/novo" element={<PecaFormPage />} />
            <Route path="/pecas/:id/editar" element={<PecaFormPage />} />

            <Route path="/servicos" element={<ServicosPage />} />
            <Route path="/servicos/novo" element={<ServicoFormPage />} />
            <Route path="/servicos/:id/editar" element={<ServicoFormPage />} />

            <Route path="/trocas" element={<TrocasPage />} />
            <Route path="/trocas/nova" element={<TrocaFormPage />} />
            <Route path="/trocas/:id/editar" element={<TrocaFormPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
