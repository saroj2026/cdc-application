"use client"

import { ReactNode } from "react"
import { LucideIcon } from "lucide-react"

interface PageHeaderProps {
  title: string
  subtitle: string
  icon: LucideIcon
  action?: ReactNode
}

export function PageHeader({ title, subtitle, icon: Icon, action }: PageHeaderProps) {
  return (
    <div className="flex items-center justify-between">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2 flex items-center gap-3">
          <Icon className="w-8 h-8 text-cyan-400" />
          {title}
        </h1>
        <p className="text-foreground-muted">{subtitle}</p>
      </div>
      {action && <div>{action}</div>}
    </div>
  )
}

