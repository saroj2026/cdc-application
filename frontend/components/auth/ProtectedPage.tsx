"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { useAppSelector } from "@/lib/store/hooks"
import { canAccessPage, hasPermission } from "@/lib/store/slices/permissionSlice"
import { Loader2 } from "lucide-react"

interface ProtectedPageProps {
  children: React.ReactNode
  requiredPermission?: string
  path?: string
}

export function ProtectedPage({ children, requiredPermission, path }: ProtectedPageProps) {
  const router = useRouter()
  const state = useAppSelector((state) => state)
  const { user, isAuthenticated } = useAppSelector((state) => state.auth)
  const [mounted, setMounted] = useState(false)
  const [hasAccess, setHasAccess] = useState<boolean | null>(null)

  // Handle client-side mounting to prevent hydration mismatch
  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!mounted) return
    
    // Wait for auth to be determined
    if (isAuthenticated === undefined) {
      setHasAccess(null)
      return
    }

    // If not authenticated, redirect to login
    if (!isAuthenticated || !user) {
      setHasAccess(false)
      router.push("/login")
      return
    }

    // Check page access
    let access = true
    if (path) {
      access = canAccessPage(path)(state)
      if (!access) {
        setHasAccess(false)
        router.push("/dashboard") // Redirect to dashboard if no access
        return
      }
    }

    // Check specific permission if provided
    if (requiredPermission) {
      access = hasPermission(requiredPermission)(state)
      if (!access) {
        setHasAccess(false)
        router.push("/dashboard") // Redirect to dashboard if no access
        return
      }
    }

    setHasAccess(access)
  }, [mounted, isAuthenticated, user, path, requiredPermission, router, state])

  // Show loading while checking auth (client-side only to prevent hydration mismatch)
  if (!mounted || isAuthenticated === undefined || hasAccess === null) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-6 h-6 animate-spin text-foreground-muted" />
      </div>
    )
  }

  // If not authenticated, don't render children (redirect will happen)
  if (!isAuthenticated || !user || hasAccess === false) {
    if (hasAccess === false) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-foreground mb-2">Access Denied</h1>
            <p className="text-foreground-muted">You don't have permission to access this page.</p>
          </div>
        </div>
      )
    }
    return null
  }

  return <>{children}</>
}

