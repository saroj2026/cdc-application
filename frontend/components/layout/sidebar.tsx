"use client"

import { useState, useEffect } from "react"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import {
  Database,
  BarChart3,
  Settings,
  GitBranch,
  AlertTriangle,
  Activity,
  Home,
  Shield,
  Users,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  ChevronUp,
} from "lucide-react"
import { useSidebar } from "@/contexts/sidebar-context"
import { useAppSelector } from "@/lib/store/hooks"
import { canAccessPage } from "@/lib/store/slices/permissionSlice"

const menuSections = [
  {
    title: "PLATFORM",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: Home },
      { href: "/monitoring", label: "Monitoring", icon: Activity },
    ],
  },
  {
    title: "REPLICATION",
    items: [
      { href: "/connections", label: "Connections", icon: Database },
      { href: "/pipelines", label: "Pipelines", icon: GitBranch },
      { href: "/analytics", label: "Analytics", icon: BarChart3 },
    ],
  },
  {
    title: "OPERATIONS",
    items: [
      { href: "/errors", label: "Errors & Alerts", icon: AlertTriangle },
      { href: "/governance", label: "Data Governance", icon: Shield },
      { href: "/users", label: "User Management", icon: Users },
      { href: "/settings", label: "Settings", icon: Settings },
    ],
  },
]

export function Sidebar() {
  const pathname = usePathname()
  const { isCollapsed, toggleCollapse, mounted } = useSidebar()
  // Use specific selectors instead of root state to prevent unnecessary rerenders
  const { user, isAuthenticated } = useAppSelector((state) => state.auth)
  const permissions = useAppSelector((state) => state.permissions)
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    PLATFORM: true,
    REPLICATION: true,
    OPERATIONS: true,
  })

  // Filter menu items based on permissions
  const getFilteredMenuSections = () => {
    // If user is not loaded yet, show all items (will be filtered once user loads)
    if (!user || !isAuthenticated) {
      return menuSections
    }
    
    // Super admin bypass - show all menu items for super admin
    const isSuperAdmin = user.is_superuser === true || 
                        user.role_name === 'super_admin' || 
                        user.role_name === 'admin' ||
                        user.is_superuser === 'true' || // Handle string 'true'
                        String(user.is_superuser).toLowerCase() === 'true'
    
    if (isSuperAdmin) {
      return menuSections
    }
    
    // Create minimal state object for permission checks
    const minimalState = { auth: { user, isAuthenticated }, permissions }
    
    return menuSections.map((section) => ({
      ...section,
      items: section.items.filter((item) => {
        // Check if user can access this page
        return canAccessPage(item.href)(minimalState)
      }),
    })).filter((section) => section.items.length > 0) // Remove empty sections
  }

  // Auto-expand section if current path matches any item in that section
  useEffect(() => {
    if (!isCollapsed) {
      const newExpanded: Record<string, boolean> = {}
      menuSections.forEach((section) => {
        const hasActiveItem = section.items.some(
          (item) => pathname === item.href || pathname.startsWith(item.href + "/")
        )
        newExpanded[section.title] = hasActiveItem || expandedSections[section.title]
      })
      setExpandedSections(newExpanded)
    }
  }, [pathname, isCollapsed])

  const toggleSection = (sectionTitle: string) => {
    if (isCollapsed) return
    setExpandedSections((prev) => ({
      ...prev,
      [sectionTitle]: !prev[sectionTitle],
    }))
  }

  // Show loading state if not mounted
  if (!mounted) {
    return (
      <aside className="w-64 border-r border-border bg-sidebar flex flex-col transition-all duration-300">
        <div className="p-6 border-b border-border" />
      </aside>
    )
  }
  
  // Debug: Log user info for super admin check
  if (process.env.NODE_ENV === 'development' && user) {
    console.log('[Sidebar] User check:', {
      is_superuser: user.is_superuser,
      role_name: user.role_name,
      email: user.email,
      willShowAll: user.is_superuser === true || user.role_name === 'super_admin' || user.role_name === 'admin'
    })
  }

  return (
    <aside
      className={cn(
        "border-r border-border bg-sidebar flex flex-col transition-all duration-300",
        isCollapsed ? "w-20" : "w-64",
      )}
    >
      {/* Logo */}
      <div className="p-6 border-b border-border flex items-center justify-between">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-primary to-info rounded-lg flex items-center justify-center flex-shrink-0">
              <Database className="w-5 h-5 text-foreground" />
            </div>
            <div>
              <h1 className="font-bold text-foreground text-sm">CDC Admin</h1>
              <p className="text-xs text-foreground-muted">Platform</p>
            </div>
          </div>
        )}
        {isCollapsed && (
          <div className="w-8 h-8 bg-gradient-to-br from-primary to-info rounded-lg flex items-center justify-center">
            <Database className="w-5 h-5 text-foreground" />
          </div>
        )}
        <button
          onClick={toggleCollapse}
          className="p-1.5 hover:bg-surface-hover rounded-lg transition-colors"
          aria-label="Toggle sidebar"
        >
          {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6">
        {getFilteredMenuSections().map((section) => {
          const isExpanded = expandedSections[section.title] ?? true
          const hasActiveItem = section.items.some(
            (item) => pathname === item.href || pathname.startsWith(item.href + "/")
          )

          return (
            <div key={section.title}>
              {!isCollapsed ? (
                <>
                  {/* Dropdown Header */}
                  <button
                    onClick={() => toggleSection(section.title)}
                    className={cn(
                      "w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-semibold text-foreground-muted uppercase tracking-wider mb-2 transition-colors hover:bg-surface-hover hover:text-primary",
                      hasActiveItem && "text-primary"
                    )}
                  >
                    <span>{section.title}</span>
                    {isExpanded ? (
                      <ChevronUp className="w-3 h-3" />
                    ) : (
                      <ChevronDown className="w-3 h-3" />
                    )}
                  </button>

                  {/* Dropdown Content */}
                  <div
                    className={cn(
                      "space-y-1 overflow-hidden transition-all duration-300 ease-in-out",
                      isExpanded ? "max-h-96 opacity-100" : "max-h-0 opacity-0"
                    )}
                  >
                    {section.items.map((item) => {
                      const Icon = item.icon
                      const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
                      return (
                        <Link
                          key={item.href}
                          href={item.href}
                          className={cn(
                            "flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors",
                            isActive
                              ? "bg-primary/20 text-primary border border-primary/30 font-semibold"
                              : "text-foreground-muted hover:text-primary hover:bg-surface-hover",
                          )}
                        >
                          <Icon className="w-4 h-4 flex-shrink-0" />
                          <span>{item.label}</span>
                        </Link>
                      )
                    })}
                  </div>
                </>
              ) : (
                /* Collapsed Sidebar - Show all items without dropdown */
                <div className="space-y-1">
                  {section.items.map((item) => {
                    const Icon = item.icon
                    const isActive = pathname === item.href || pathname.startsWith(item.href + "/")
                    return (
                      <Link
                        key={item.href}
                        href={item.href}
                        title={item.label}
                        className={cn(
                          "flex items-center gap-3 py-2 rounded-lg text-sm font-medium transition-colors justify-center px-0",
                          isActive
                            ? "bg-primary/20 text-primary border border-primary/30 font-semibold"
                            : "text-foreground-muted hover:text-primary hover:bg-surface-hover",
                        )}
                      >
                        <Icon className="w-4 h-4 flex-shrink-0" />
                      </Link>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="p-3 border-t border-border">
        <div className={cn("glass p-3 rounded-lg text-xs text-foreground-muted", isCollapsed && "flex justify-center")}>
          {!isCollapsed && (
            <>
              <p className="font-semibold mb-1">v1.0.0</p>
              <p>Real-time CDC Platform</p>
            </>
          )}
          {isCollapsed && <p className="font-semibold">v1</p>}
        </div>
      </div>
    </aside>
  )
}
