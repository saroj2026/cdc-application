"use client"

import { useState, useEffect } from "react"
import { X, AlertCircle, XCircle, CheckCircle, Info, AlertTriangle } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

type ToastType = "error" | "success" | "info" | "warning"

interface ErrorToastProps {
  message: string
  title?: string
  type?: ToastType
  onClose: () => void
  duration?: number
}

export function ErrorToast({ message, title, type = "error", onClose, duration = 5000 }: ErrorToastProps) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
    if (duration > 0) {
      const timer = setTimeout(() => {
        onClose()
      }, duration)
      return () => clearTimeout(timer)
    }
  }, [duration, onClose])

  if (!mounted) return null

  // Get styling based on type
  const getTypeStyles = () => {
    switch (type) {
      case "success":
        return {
          cardClass: "bg-gradient-to-br from-green-500/10 to-emerald-600/5 border-2 border-green-500/30",
          iconBgClass: "bg-green-500/10",
          iconClass: "text-green-400",
          Icon: CheckCircle,
          buttonHoverClass: "hover:bg-green-500/10",
          defaultTitle: "Success"
        }
      case "info":
        return {
          cardClass: "bg-gradient-to-br from-blue-500/10 to-cyan-600/5 border-2 border-blue-500/30",
          iconBgClass: "bg-blue-500/10",
          iconClass: "text-blue-400",
          Icon: Info,
          buttonHoverClass: "hover:bg-blue-500/10",
          defaultTitle: "Info"
        }
      case "warning":
        return {
          cardClass: "bg-gradient-to-br from-yellow-500/10 to-orange-600/5 border-2 border-yellow-500/30",
          iconBgClass: "bg-yellow-500/10",
          iconClass: "text-yellow-400",
          Icon: AlertTriangle,
          buttonHoverClass: "hover:bg-yellow-500/10",
          defaultTitle: "Warning"
        }
      case "error":
      default:
        return {
          cardClass: "bg-gradient-to-br from-red-500/10 to-red-600/5 border-2 border-red-500/30",
          iconBgClass: "bg-red-500/10",
          iconClass: "text-red-400",
          Icon: XCircle,
          buttonHoverClass: "hover:bg-red-500/10",
          defaultTitle: "Error"
        }
    }
  }

  const styles = getTypeStyles()
  const Icon = styles.Icon

  return (
    <div className="fixed top-4 right-4 z-50 animate-in slide-in-from-top-5">
      <Card className={`${styles.cardClass} shadow-2xl max-w-md w-full`}>
        <div className="p-4">
          <div className="flex items-start gap-3">
            <div className={`w-10 h-10 rounded-full ${styles.iconBgClass} flex items-center justify-center flex-shrink-0`}>
              <Icon className={`w-6 h-6 ${styles.iconClass}`} />
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="text-sm font-semibold text-foreground mb-1">{title || styles.defaultTitle}</h3>
              <p className="text-sm text-foreground-muted whitespace-pre-wrap break-words">{message}</p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={onClose}
              className={`h-6 w-6 p-0 flex-shrink-0 ${styles.buttonHoverClass}`}
            >
              <X className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

// Hook for easier usage
export function useErrorToast() {
  const [toast, setToast] = useState<{ message: string; title?: string; type?: ToastType } | null>(null)

  const showError = (message: string, title?: string, type?: ToastType) => {
    setToast({ message, title, type: type || "error" })
  }

  const ErrorToastComponent = () => {
    if (!toast) return null
    return (
      <ErrorToast
        message={toast.message}
        title={toast.title}
        type={toast.type}
        onClose={() => setToast(null)}
      />
    )
  }

  return { showError, ErrorToastComponent, error: toast }
}

