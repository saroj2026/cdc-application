"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { User, Bell, Settings, Moon, Sun, LogOut } from "lucide-react"
import { useTheme } from "@/contexts/theme-context"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { logout } from "@/lib/store/slices/authSlice"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function TopNav() {
  const { theme, toggleTheme } = useTheme()
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { user } = useAppSelector((state) => state.auth)
  const { unreadCount } = useAppSelector((state) => state.alerts)
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const handleLogout = async () => {
    try {
      await dispatch(logout())
      router.push("/auth/login")
    } catch (error) {
      console.error("Logout error:", error)
      // Still redirect even if logout fails
      router.push("/auth/login")
    }
  }

  // Safety check for user data
  const userName = user?.full_name || "User"
  const userEmail = user?.email || ""

  return (
    <div className="h-16 border-b border-border bg-sidebar flex items-center justify-between px-6">
      <div>
        <h2 className="text-xl font-semibold text-foreground">Change Data Capture Platform</h2>
        <p className="text-sm text-foreground-muted">Real-time Replication & Monitoring</p>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={() => router.push("/errors")}
          className="relative p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary"
          aria-label="Notifications"
        >
          <Bell className="w-5 h-5 text-foreground-muted hover:text-primary transition-colors" />
          {mounted && unreadCount > 0 && (
            <span className="absolute top-0 right-0 w-4 h-4 bg-error text-white text-xs rounded-full flex items-center justify-center">
              {unreadCount > 9 ? '9+' : unreadCount}
            </span>
          )}
        </button>
        <button className="p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary" aria-label="Settings">
          <Settings className="w-5 h-5 text-foreground-muted hover:text-primary transition-colors" />
        </button>
        <button
          onClick={toggleTheme}
          className="p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary"
          aria-label="Toggle theme"
          suppressHydrationWarning
        >
          <Sun className={`w-5 h-5 text-foreground-muted ${mounted && theme === "dark" ? "block" : "hidden"}`} />
          <Moon className={`w-5 h-5 text-foreground-muted ${mounted && theme === "light" ? "block" : "hidden"}`} />
          {!mounted && <Moon className="w-5 h-5 text-foreground-muted" />}
        </button>
        
        {/* User Menu with Logout - Always render, but disable interactions until mounted */}
        <div suppressHydrationWarning>
          {mounted ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary" aria-label="User menu">
                  <User className="w-5 h-5 text-foreground-muted hover:text-primary transition-colors" />
                </button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end" className="bg-surface border-border">
                <DropdownMenuLabel>
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium text-foreground">{userName}</p>
                    {userEmail && <p className="text-xs text-foreground-muted">{userEmail}</p>}
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={() => router.push("/settings")} className="cursor-pointer">
                  <Settings className="w-4 h-4 mr-2" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="cursor-pointer text-error focus:text-error">
                  <LogOut className="w-4 h-4 mr-2" />
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <button className="p-2 hover:bg-surface-hover rounded-lg transition-colors hover:text-primary" aria-label="User menu" disabled>
              <User className="w-5 h-5 text-foreground-muted hover:text-primary transition-colors" />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
