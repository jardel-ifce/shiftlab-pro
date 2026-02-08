import { useCallback, useState } from "react"
import { Outlet } from "react-router-dom"
import { Sidebar, MobileSidebar } from "./Sidebar"
import { Header } from "./Header"

export function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const closeMobile = useCallback(() => setMobileOpen(false), [])

  return (
    <div className="flex h-screen">
      <Sidebar />
      <MobileSidebar open={mobileOpen} onClose={closeMobile} />
      <div className="flex flex-1 flex-col overflow-hidden">
        <Header onMenuClick={() => setMobileOpen(true)} />
        <main className="flex-1 overflow-auto p-4 lg:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
