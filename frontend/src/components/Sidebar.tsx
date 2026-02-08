import { NavLink } from "react-router-dom"
import { LayoutDashboard, Users, Droplets, Car, Wrench, Package, Hammer } from "lucide-react"
import { cn } from "@/lib/utils"

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/clientes", icon: Users, label: "Clientes" },
  { to: "/veiculos", icon: Car, label: "Veículos" },
  { to: "/oleos", icon: Droplets, label: "Óleos" },
  { to: "/pecas", icon: Package, label: "Peças" },
  { to: "/servicos", icon: Hammer, label: "Serviços" },
  { to: "/trocas", icon: Wrench, label: "Trocas" },
]

export function Sidebar() {
  return (
    <aside className="hidden w-64 border-r bg-card lg:block">
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <Wrench className="h-6 w-6 text-primary" />
        <span className="text-lg font-bold">ShiftLab Pro</span>
      </div>
      <nav className="space-y-1 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
              )
            }
          >
            <item.icon className="h-4 w-4" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
