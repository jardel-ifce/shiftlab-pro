import * as React from "react"
import { cn } from "@/lib/utils"

interface HoverCardProps {
  children: React.ReactNode
}

interface HoverCardTriggerProps extends React.HTMLAttributes<HTMLSpanElement> {
  asChild?: boolean
}

interface HoverCardContentProps extends React.HTMLAttributes<HTMLDivElement> {
  side?: "top" | "bottom" | "left" | "right"
  align?: "start" | "center" | "end"
}

const HoverCardContext = React.createContext<{
  open: boolean
  setOpen: (open: boolean) => void
  triggerRef: React.RefObject<HTMLSpanElement | null>
}>({ open: false, setOpen: () => {}, triggerRef: { current: null } })

function HoverCard({ children }: HoverCardProps) {
  const [open, setOpen] = React.useState(false)
  const triggerRef = React.useRef<HTMLSpanElement | null>(null)

  return (
    <HoverCardContext.Provider value={{ open, setOpen, triggerRef }}>
      <span className="inline">{children}</span>
    </HoverCardContext.Provider>
  )
}

function HoverCardTrigger({ children, className, ...props }: HoverCardTriggerProps) {
  const { setOpen, triggerRef } = React.useContext(HoverCardContext)
  const timeoutRef = React.useRef<ReturnType<typeof setTimeout>>()

  function handleEnter() {
    clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => setOpen(true), 200)
  }

  function handleLeave() {
    clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => setOpen(false), 300)
  }

  React.useEffect(() => {
    return () => clearTimeout(timeoutRef.current)
  }, [])

  return (
    <span
      ref={triggerRef}
      className={className}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      onFocus={handleEnter}
      onBlur={handleLeave}
      {...props}
    >
      {children}
    </span>
  )
}

function HoverCardContent({
  className,
  children,
  side = "bottom",
  ...props
}: HoverCardContentProps) {
  const { open, setOpen } = React.useContext(HoverCardContext)
  const timeoutRef = React.useRef<ReturnType<typeof setTimeout>>()

  function handleEnter() {
    clearTimeout(timeoutRef.current)
  }

  function handleLeave() {
    clearTimeout(timeoutRef.current)
    timeoutRef.current = setTimeout(() => setOpen(false), 300)
  }

  React.useEffect(() => {
    return () => clearTimeout(timeoutRef.current)
  }, [])

  if (!open) return null

  const sideClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 mb-2",
    bottom: "top-full left-1/2 -translate-x-1/2 mt-2",
    left: "right-full top-1/2 -translate-y-1/2 mr-2",
    right: "left-full top-1/2 -translate-y-1/2 ml-2",
  }

  return (
    <div
      className={cn(
        "absolute z-50 w-52 rounded-md border bg-popover p-3 shadow-md animate-in fade-in-0 zoom-in-95",
        sideClasses[side],
        className
      )}
      onMouseEnter={handleEnter}
      onMouseLeave={handleLeave}
      {...props}
    >
      {children}
    </div>
  )
}

export { HoverCard, HoverCardTrigger, HoverCardContent }
