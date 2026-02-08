import { NavLink, useLocation } from "react-router-dom"
import { LayoutDashboard, Users, Droplets, Car, Wrench, Package, Hammer, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { useEffect } from "react"

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/clientes", icon: Users, label: "Clientes" },
  { to: "/veiculos", icon: Car, label: "Veículos" },
  { to: "/oleos", icon: Droplets, label: "Óleos" },
  { to: "/pecas", icon: Package, label: "Peças" },
  { to: "/servicos", icon: Hammer, label: "Serviços" },
  { to: "/trocas", icon: Wrench, label: "Trocas" },
]

function NavContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="space-y-1 p-4">
      {navItems.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.to === "/"}
          onClick={onNavigate}
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
  )
}

export function Sidebar() {
  return (
    <aside className="hidden w-64 border-r bg-card lg:block">
      <div className="flex h-16 items-center gap-2 border-b px-6">
        <Wrench className="h-6 w-6 text-primary" />
        <span className="text-lg font-bold">ShiftLab Pro</span>
      </div>
      <NavContent />
    </aside>
  )
}

export function MobileSidebar({ open, onClose }: { open: boolean; onClose: () => void }) {
  const location = useLocation()

  useEffect(() => {
    onClose()
  }, [location.pathname, onClose])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      <div className="fixed inset-0 bg-black/50" onClick={onClose} />
      <aside className="fixed inset-y-0 left-0 w-64 bg-card shadow-lg">
        <div className="flex h-16 items-center justify-between border-b px-6">
          <div className="flex items-center gap-2">
            <Wrench className="h-6 w-6 text-primary" />
            <span className="text-lg font-bold">ShiftLab Pro</span>
          </div>
          <button onClick={onClose}>
            <X className="h-5 w-5 text-muted-foreground" />
          </button>
        </div>
        <NavContent onNavigate={onClose} />
      </aside>
    </div>
  )
}
