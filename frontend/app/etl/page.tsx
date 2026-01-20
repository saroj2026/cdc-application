"use client"

import { useState, useEffect, useMemo } from "react"
import { useRouter } from "next/navigation"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { PageHeader } from "@/components/ui/page-header"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import {
  Sparkles,
  GitBranch,
  Code2,
  Shield,
  Activity,
  Clock,
  ArrowRight,
  Plus,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  DatabaseZap,
} from "lucide-react"
import { useAppSelector, useAppDispatch } from "@/lib/store/hooks"
import { fetchETLStats, fetchETLPipelines } from "@/lib/store/slices/etlSlice"
import { canAccessPage } from "@/lib/store/slices/permissionSlice"

export default function ETLHomePage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { user, isAuthenticated } = useAppSelector((state) => state.auth)
  const permissions = useAppSelector((state) => state.permissions)
  const { etlStats, pipelines: etlPipelines, isLoading } = useAppSelector((state) => state.etl)
  const [mounted, setMounted] = useState(false)
  
  useEffect(() => {
    setMounted(true)
    if (isAuthenticated) {
      dispatch(fetchETLPipelines()) // Also fetch pipelines to get active count
      dispatch(fetchETLStats())
      const interval = setInterval(() => {
        dispatch(fetchETLPipelines())
        dispatch(fetchETLStats())
      }, 15000) // Refresh every 15 seconds
      return () => clearInterval(interval)
    }
  }, [dispatch, isAuthenticated])
  
  // Check if user can access ETL pages
  const canAccessEtl = useMemo(() => {
    if (!user || !isAuthenticated) return false
    const minimalState = { auth: { user, isAuthenticated }, permissions }
    return canAccessPage('/etl')(minimalState)
  }, [user, isAuthenticated, permissions])
  
  // Calculate active pipelines from actual pipeline list
  const activePipelinesCount = etlPipelines.filter(
    (p) => p.status === 'active' || p.status === 'running' || p.status === 'starting'
  ).length

  // Use real stats if available, otherwise use defaults
  const stats = etlStats ? {
    activePipelines: activePipelinesCount || etlStats.active_pipelines || 0,
    failedRuns: etlStats.failed_runs || 0,
    recordsProcessed: etlStats.records_processed || 0,
    avgLatency: etlStats.avg_latency_ms || etlStats.avg_latency || 240,
  } : {
    activePipelines: activePipelinesCount || 0,
    failedRuns: 0,
    recordsProcessed: 0,
    avgLatency: 240,
  }

  if (!mounted) {
    return null
  }

  if (!isAuthenticated || !canAccessEtl) {
    return <ProtectedPage path="/etl" />
  }

  const quickActions = [
    {
      label: "Create ETL Pipeline",
      icon: Plus,
      href: "/etl/pipelines?action=create",
      gradient: "from-purple-500/20 to-pink-500/20",
      iconColor: "text-purple-400",
    },
    {
      label: "New Transformation",
      icon: Code2,
      href: "/etl/transformations?action=create",
      gradient: "from-blue-500/20 to-cyan-500/20",
      iconColor: "text-blue-400",
    },
    {
      label: "Schedule Job",
      icon: Clock,
      href: "/etl/scheduler?action=create",
      gradient: "from-green-500/20 to-emerald-500/20",
      iconColor: "text-green-400",
    },
  ]

  return (
    <ProtectedPage path="/etl">
      <div className="p-6 space-y-6">
      <PageHeader
        title="ETL / ETS Platform"
        subtitle="Transform, validate & enrich your data with powerful SQL-based transformations"
        icon={Sparkles}
      />

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="p-6 bg-gradient-to-br from-purple-500/10 to-pink-500/5 border-purple-500/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 group">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">
                Active ETL Pipelines
              </p>
              <p className="text-4xl font-extrabold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent mb-1">
                {stats.activePipelines}
              </p>
              <p className="text-xs font-medium text-foreground-muted/80 flex items-center gap-1">
                <TrendingUp className="w-3 h-3 text-green-400" />
                <span>+3 this week</span>
              </p>
            </div>
            <div className="p-4 bg-purple-500/20 rounded-xl group-hover:scale-110 transition-transform duration-300">
              <GitBranch className="w-8 h-8 text-purple-400" />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-red-500/10 to-orange-500/5 border-red-500/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 group">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">
                Failed Runs
              </p>
              <p className="text-4xl font-extrabold bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent mb-1">
                {stats.failedRuns}
              </p>
              <p className="text-xs font-medium text-foreground-muted/80 flex items-center gap-1">
                <CheckCircle className="w-3 h-3 text-green-400" />
                <span>99.2% success rate</span>
              </p>
            </div>
            <div className="p-4 bg-red-500/20 rounded-xl group-hover:scale-110 transition-transform duration-300">
              <AlertCircle className="w-8 h-8 text-red-400" />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-cyan-500/10 to-blue-500/5 border-cyan-500/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 group">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">
                Records Processed
              </p>
              <p className="text-4xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-1">
                {(stats.recordsProcessed / 1000000).toFixed(1)}M
              </p>
              <p className="text-xs font-medium text-foreground-muted/80 flex items-center gap-1">
                <DatabaseZap className="w-3 h-3 text-cyan-400" />
                <span>Last 24 hours</span>
              </p>
            </div>
            <div className="p-4 bg-cyan-500/20 rounded-xl group-hover:scale-110 transition-transform duration-300">
              <DatabaseZap className="w-8 h-8 text-cyan-400" />
            </div>
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-green-500/10 to-emerald-500/5 border-green-500/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 group">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">
                Avg Latency
              </p>
              <p className="text-4xl font-extrabold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent mb-1">
                {stats.avgLatency}ms
              </p>
              <p className="text-xs font-medium text-foreground-muted/80 flex items-center gap-1">
                <TrendingUp className="w-3 h-3 text-green-400" />
                <span>-15% improvement</span>
              </p>
            </div>
            <div className="p-4 bg-green-500/20 rounded-xl group-hover:scale-110 transition-transform duration-300">
              <Activity className="w-8 h-8 text-green-400" />
            </div>
          </div>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-foreground">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {quickActions.map((action) => {
            const Icon = action.icon
            return (
              <Card
                key={action.label}
                className={`p-6 bg-gradient-to-br ${action.gradient} border-border shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 cursor-pointer group`}
                onClick={() => router.push(action.href)}
              >
                <div className="flex items-center gap-4">
                  <div className={`p-4 bg-gradient-to-br ${action.gradient} rounded-xl group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className={`w-6 h-6 ${action.iconColor}`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-foreground mb-1">{action.label}</h3>
                    <p className="text-sm text-foreground-muted">Get started quickly</p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-foreground-muted group-hover:translate-x-1 transition-transform" />
                </div>
              </Card>
            )
          })}
        </div>
      </div>

      {/* Navigation Cards */}
      <div className="space-y-4">
        <h2 className="text-2xl font-bold text-foreground">Explore</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card
            className="p-6 bg-surface border-border shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 cursor-pointer group"
            onClick={() => router.push("/etl/pipelines")}
          >
            <div className="flex flex-col items-center text-center space-y-3">
              <div className="p-4 bg-purple-500/20 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <GitBranch className="w-8 h-8 text-purple-400" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground mb-1">ETL Pipelines</h3>
                <p className="text-sm text-foreground-muted">Manage data pipelines</p>
              </div>
            </div>
          </Card>

          <Card
            className="p-6 bg-surface border-border shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 cursor-pointer group"
            onClick={() => router.push("/etl/transformations")}
          >
            <div className="flex flex-col items-center text-center space-y-3">
              <div className="p-4 bg-blue-500/20 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <Code2 className="w-8 h-8 text-blue-400" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground mb-1">Transformations</h3>
                <p className="text-sm text-foreground-muted">SQL & data transforms</p>
              </div>
            </div>
          </Card>

          <Card
            className="p-6 bg-surface border-border shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 cursor-pointer group"
            onClick={() => router.push("/etl/data-quality")}
          >
            <div className="flex flex-col items-center text-center space-y-3">
              <div className="p-4 bg-green-500/20 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <Shield className="w-8 h-8 text-green-400" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground mb-1">Data Quality</h3>
                <p className="text-sm text-foreground-muted">Validate & monitor</p>
              </div>
            </div>
          </Card>

          <Card
            className="p-6 bg-surface border-border shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 cursor-pointer group"
            onClick={() => router.push("/etl/monitoring")}
          >
            <div className="flex flex-col items-center text-center space-y-3">
              <div className="p-4 bg-cyan-500/20 rounded-xl group-hover:scale-110 transition-transform duration-300">
                <Activity className="w-8 h-8 text-cyan-400" />
              </div>
              <div>
                <h3 className="text-lg font-bold text-foreground mb-1">Monitoring</h3>
                <p className="text-sm text-foreground-muted">Track performance</p>
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
    </ProtectedPage>
  )
}

