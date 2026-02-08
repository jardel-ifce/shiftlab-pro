import { LogOut, Menu, User } from "lucide-react"
import { useAuth } from "@/hooks/useAuth"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"

export function Header({ onMenuClick }: { onMenuClick?: () => void }) {
  const { user, logout } = useAuth()

  return (
    <header className="flex h-16 items-center justify-between border-b bg-card px-4 lg:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onMenuClick}
      >
        <Menu className="h-5 w-5" />
      </Button>
      <div className="hidden lg:block" />
      <div className="flex items-center gap-2 sm:gap-4">
        <div className="flex items-center gap-2 text-sm">
          <User className="h-4 w-4 text-muted-foreground hidden sm:block" />
          <span className="font-medium">{user?.nome}</span>
          <Badge variant="secondary" className="text-xs hidden sm:inline-flex">
            {user?.role === "admin" ? "Admin" : "Funcionário"}
          </Badge>
        </div>
        <Separator orientation="vertical" className="h-6" />
        <Button variant="ghost" size="icon" onClick={logout} title="Sair">
          <LogOut className="h-4 w-4" />
        </Button>
      </div>
    </header>
  )
}
