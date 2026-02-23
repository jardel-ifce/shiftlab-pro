import { NavLink, useLocation } from "react-router-dom"
import { LayoutDashboard, Users, Droplets, Car, Wrench, Package, Hammer, PackagePlus, Filter, DollarSign, Receipt, ChevronDown, Boxes, X } from "lucide-react"
import { cn } from "@/lib/utils"
import { useEffect, useState } from "react"

type NavItem = { to: string; icon: React.ComponentType<{ className?: string }>; label: string }
type NavGroup = { group: string; icon: React.ComponentType<{ className?: string }>; items: NavItem[] }
type NavEntry = NavItem | NavGroup

function isGroup(entry: NavEntry): entry is NavGroup {
  return "group" in entry
}

const navEntries: NavEntry[] = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/clientes", icon: Users, label: "Clientes" },
  { to: "/veiculos", icon: Car, label: "Veículos" },
  {
    group: "Componentes",
    icon: Boxes,
    items: [
      { to: "/oleos", icon: Droplets, label: "Óleos" },
      { to: "/filtros", icon: Filter, label: "Filtros" },
      { to: "/pecas", icon: Package, label: "Peças" },
      { to: "/servicos", icon: Hammer, label: "Serviços" },
    ],
  },
  { to: "/entradas", icon: PackagePlus, label: "Entradas" },
  { to: "/trocas", icon: Wrench, label: "Trocas" },
  { to: "/despesas", icon: Receipt, label: "Despesas" },
  { to: "/financeiro", icon: DollarSign, label: "Financeiro" },
]

function NavItemLink({ item, onNavigate, indent }: { item: NavItem; onNavigate?: () => void; indent?: boolean }) {
  return (
    <NavLink
      to={item.to}
      end={item.to === "/"}
      onClick={onNavigate}
      className={({ isActive }) =>
        cn(
          "flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
          indent && "pl-9",
          isActive
            ? "bg-primary text-primary-foreground"
            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        )
      }
    >
      <item.icon className="h-4 w-4" />
      {item.label}
    </NavLink>
  )
}

function NavGroupCollapsible({ entry, onNavigate }: { entry: NavGroup; onNavigate?: () => void }) {
  const location = useLocation()
  const isChildActive = entry.items.some((item) => location.pathname.startsWith(item.to))
  const [open, setOpen] = useState(isChildActive)

  // Auto-expand when a child route is active
  useEffect(() => {
    if (isChildActive) setOpen(true)
  }, [isChildActive])

  return (
    <div>
      <button
        type="button"
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          "flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors",
          isChildActive
            ? "text-foreground"
            : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
        )}
      >
        <entry.icon className="h-4 w-4" />
        <span className="flex-1 text-left">{entry.group}</span>
        <ChevronDown className={cn("h-4 w-4 transition-transform", open && "rotate-180")} />
      </button>
      {open && (
        <div className="mt-0.5 space-y-0.5">
          {entry.items.map((item) => (
            <NavItemLink key={item.to} item={item} onNavigate={onNavigate} indent />
          ))}
        </div>
      )}
    </div>
  )
}

function NavContent({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <nav className="space-y-1 p-4">
      {navEntries.map((entry) => {
        if (isGroup(entry)) {
          return <NavGroupCollapsible key={entry.group} entry={entry} onNavigate={onNavigate} />
        }
        return <NavItemLink key={entry.to} item={entry} onNavigate={onNavigate} />
      })}
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
