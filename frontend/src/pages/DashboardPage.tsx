import { useAuth } from "@/hooks/useAuth"
import { useClientes } from "@/hooks/useClientes"
import { useVeiculos } from "@/hooks/useVeiculos"
import { useOleos } from "@/hooks/useOleos"
import { useTrocas } from "@/hooks/useTrocas"
import { usePecas } from "@/hooks/usePecas"
import { useServicos } from "@/hooks/useServicos"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, Car, Droplets, Wrench, Package, Hammer } from "lucide-react"

export function DashboardPage() {
  const { user } = useAuth()
  const { data: clientes } = useClientes()
  const { data: veiculos } = useVeiculos()
  const { data: oleos } = useOleos()
  const { data: trocas } = useTrocas()
  const { data: pecas } = usePecas()
  const { data: servicos } = useServicos()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Bem-vindo(a), {user?.nome}!
        </p>
      </div>

      <div className="grid gap-4 grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Clientes</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{clientes?.total ?? "-"}</div>
            <p className="text-xs text-muted-foreground">Cadastrados no sistema</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Veículos</CardTitle>
            <Car className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{veiculos?.total ?? "-"}</div>
            <p className="text-xs text-muted-foreground">Registrados no sistema</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Óleos</CardTitle>
            <Droplets className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{oleos?.total ?? "-"}</div>
            <p className="text-xs text-muted-foreground">Produtos cadastrados</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Peças</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{pecas?.total ?? "-"}</div>
            <p className="text-xs text-muted-foreground">Peças cadastradas</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Serviços</CardTitle>
            <Hammer className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{servicos?.total ?? "-"}</div>
            <p className="text-xs text-muted-foreground">Serviços disponíveis</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Trocas</CardTitle>
            <Wrench className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{trocas?.total ?? "-"}</div>
            <p className="text-xs text-muted-foreground">Realizadas no total</p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
