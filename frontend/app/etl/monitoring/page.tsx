"use client"

import { useState, useEffect, useMemo } from "react"
import { useRouter } from "next/navigation"
import { PageHeader } from "@/components/ui/page-header"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import {
  Activity,
  Search,
  Filter,
  Play,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Loader2,
  Eye,
  RefreshCw,
  TrendingUp,
  Database,
  Timer,
  FileText,
} from "lucide-react"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { fetchETLRuns, fetchETLPipelines } from "@/lib/store/slices/etlSlice"
import { formatDistanceToNow, format } from "date-fns"
import { useErrorToast } from "@/components/ui/error-toast"
import { cn } from "@/lib/utils"

export default function ETLMonitoringPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { showError, ErrorToastComponent } = useErrorToast()
  const { runs, pipelines: etlPipelines, isLoading } = useAppSelector((state) => state.etl)
  
  const [searchQuery, setSearchQuery] = useState("")
  const [filterStatus, setFilterStatus] = useState("all")
  const [filterPipeline, setFilterPipeline] = useState("all")
  const [selectedRun, setSelectedRun] = useState<string | null>(null)

  useEffect(() => {
    dispatch(fetchETLRuns())
    dispatch(fetchETLPipelines())
    const interval = setInterval(() => {
      dispatch(fetchETLRuns())
      dispatch(fetchETLPipelines())
    }, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [dispatch])

  // Get pipeline name mapping
  const pipelineNameMap = useMemo(() => {
    const map = new Map<string, string>()
    etlPipelines.forEach(p => {
      map.set(p.id, p.name)
    })
    return map
  }, [etlPipelines])

  // Filter runs
  const filteredRuns = useMemo(() => {
    let filtered = runs

    // Filter by status
    if (filterStatus !== "all") {
      filtered = filtered.filter(r => r.status === filterStatus)
    }

    // Filter by pipeline
    if (filterPipeline !== "all") {
      filtered = filtered.filter(r => r.pipeline_id === filterPipeline)
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(r => {
        const pipelineName = pipelineNameMap.get(r.pipeline_id)?.toLowerCase() || ""
        return (
          r.id.toLowerCase().includes(query) ||
          pipelineName.includes(query) ||
          r.error_message?.toLowerCase().includes(query)
        )
      })
    }

    // Sort by started_at (most recent first)
    return filtered.sort((a, b) => {
      const dateA = a.started_at ? new Date(a.started_at).getTime() : 0
      const dateB = b.started_at ? new Date(b.started_at).getTime() : 0
      return dateB - dateA
    })
  }, [runs, filterStatus, filterPipeline, searchQuery, pipelineNameMap])

  // Calculate statistics
  const stats = useMemo(() => {
    const total = runs.length
    const running = runs.filter(r => r.status === "running").length
    const completed = runs.filter(r => r.status === "completed").length
    const failed = runs.filter(r => r.status === "failed").length
    const totalRecords = runs
      .filter(r => r.status === "completed")
      .reduce((sum, r) => sum + (r.records_processed || 0), 0)
    const totalErrors = runs
      .filter(r => r.status === "failed")
      .reduce((sum, r) => sum + (r.records_failed || 0), 0)

    return {
      total,
      running,
      completed,
      failed,
      totalRecords,
      totalErrors,
      successRate: total > 0 ? ((completed / total) * 100).toFixed(1) : "0",
    }
  }, [runs])

  const getStatusBadge = (status: string) => {
    switch (status?.toLowerCase()) {
      case "running":
        return (
          <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 flex items-center gap-1">
            <Loader2 className="w-3 h-3 animate-spin" />
            Running
          </Badge>
        )
      case "completed":
        return (
          <Badge className="bg-green-500/20 text-green-400 border-green-500/30 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            Completed
          </Badge>
        )
      case "failed":
        return (
          <Badge className="bg-red-500/20 text-red-400 border-red-500/30 flex items-center gap-1">
            <XCircle className="w-3 h-3" />
            Failed
          </Badge>
        )
      default:
        return (
          <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">
            {status || "Unknown"}
          </Badge>
        )
    }
  }

  const formatDuration = (seconds?: number) => {
    if (!seconds) return "N/A"
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const handleRefresh = () => {
    dispatch(fetchETLRuns())
    dispatch(fetchETLPipelines())
    showError("Data refreshed", "Success", "success")
  }

  return (
    <ProtectedPage path="/etl/monitoring">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <PageHeader
            title="ETL Monitoring"
            subtitle="Track all ETL pipeline executions and their status"
            icon={Activity}
          />
          <Button
            onClick={handleRefresh}
            variant="outline"
            disabled={isLoading}
            className="border-border text-foreground-muted hover:text-foreground"
          >
            <RefreshCw className={cn("w-4 h-4 mr-2", isLoading && "animate-spin")} />
            Refresh
          </Button>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          <Card className="p-4 bg-gradient-to-br from-blue-500/10 to-cyan-500/5 border-blue-500/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Total Runs</p>
                <p className="text-2xl font-bold text-foreground">{stats.total}</p>
              </div>
              <Database className="w-8 h-8 text-blue-400 opacity-50" />
            </div>
          </Card>

          <Card className="p-4 bg-gradient-to-br from-blue-500/10 to-cyan-500/5 border-blue-500/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Running</p>
                <p className="text-2xl font-bold text-blue-400">{stats.running}</p>
              </div>
              <Activity className="w-8 h-8 text-blue-400 opacity-50" />
            </div>
          </Card>

          <Card className="p-4 bg-gradient-to-br from-green-500/10 to-emerald-500/5 border-green-500/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Completed</p>
                <p className="text-2xl font-bold text-green-400">{stats.completed}</p>
              </div>
              <CheckCircle className="w-8 h-8 text-green-400 opacity-50" />
            </div>
          </Card>

          <Card className="p-4 bg-gradient-to-br from-red-500/10 to-orange-500/5 border-red-500/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Failed</p>
                <p className="text-2xl font-bold text-red-400">{stats.failed}</p>
              </div>
              <XCircle className="w-8 h-8 text-red-400 opacity-50" />
            </div>
          </Card>

          <Card className="p-4 bg-gradient-to-br from-purple-500/10 to-pink-500/5 border-purple-500/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Records</p>
                <p className="text-2xl font-bold text-purple-400">
                  {stats.totalRecords >= 1000000
                    ? `${(stats.totalRecords / 1000000).toFixed(1)}M`
                    : stats.totalRecords >= 1000
                    ? `${(stats.totalRecords / 1000).toFixed(1)}K`
                    : stats.totalRecords.toLocaleString()}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-400 opacity-50" />
            </div>
          </Card>

          <Card className="p-4 bg-gradient-to-br from-emerald-500/10 to-green-500/5 border-emerald-500/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Success Rate</p>
                <p className="text-2xl font-bold text-emerald-400">{stats.successRate}%</p>
              </div>
              <CheckCircle className="w-8 h-8 text-emerald-400 opacity-50" />
            </div>
          </Card>
        </div>

        {/* Filters */}
        <Card className="p-4 bg-surface border-border">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-foreground-muted" />
              <Input
                placeholder="Search by pipeline name, run ID, or error..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-background border-border"
              />
            </div>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 bg-background border border-border rounded-md text-foreground text-sm"
            >
              <option value="all">All Statuses</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
            <select
              value={filterPipeline}
              onChange={(e) => setFilterPipeline(e.target.value)}
              className="px-3 py-2 bg-background border border-border rounded-md text-foreground text-sm min-w-[200px]"
            >
              <option value="all">All Pipelines</option>
              {etlPipelines.map(p => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
          </div>
        </Card>

        {/* Runs Table */}
        {isLoading && runs.length === 0 ? (
          <Card className="p-12">
            <div className="flex flex-col items-center justify-center">
              <Loader2 className="w-8 h-8 animate-spin text-purple-400 mb-4" />
              <p className="text-foreground-muted">Loading ETL runs...</p>
            </div>
          </Card>
        ) : filteredRuns.length === 0 ? (
          <Card className="p-12 text-center">
            <Activity className="w-16 h-16 mx-auto mb-4 text-purple-400/50" />
            <h3 className="text-xl font-bold text-foreground mb-2">No ETL Runs Found</h3>
            <p className="text-foreground-muted">
              {searchQuery || filterStatus !== "all" || filterPipeline !== "all"
                ? "No runs match your filters."
                : "ETL pipeline runs will appear here once pipelines are executed."}
            </p>
          </Card>
        ) : (
          <Card className="p-6 bg-surface border-border shadow-lg overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-surface-hover border-b border-border">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                      Pipeline
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                      Started
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                      Duration
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                      Records
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                      Triggered By
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-foreground-muted uppercase tracking-wider">
                      Actions
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {filteredRuns.map((run) => (
                    <tr
                      key={run.id}
                      className={cn(
                        "hover:bg-surface-hover transition-colors",
                        selectedRun === run.id && "bg-purple-500/10"
                      )}
                    >
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex flex-col">
                          <span className="text-sm font-medium text-foreground">
                            {pipelineNameMap.get(run.pipeline_id) || run.pipeline_id.slice(0, 8)}
                          </span>
                          <span className="text-xs text-foreground-muted font-mono">
                            {run.id.slice(0, 8)}...
                          </span>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        {getStatusBadge(run.status)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex flex-col">
                          <span className="text-sm text-foreground">
                            {run.started_at
                              ? format(new Date(run.started_at), "MMM dd, yyyy HH:mm:ss")
                              : "N/A"}
                          </span>
                          {run.started_at && (
                            <span className="text-xs text-foreground-muted">
                              {formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-2 text-sm text-foreground">
                          <Timer className="w-4 h-4 text-foreground-muted" />
                          {formatDuration(run.duration_seconds)}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <div className="flex flex-col">
                          <span className="text-sm font-medium text-foreground">
                            {(run.records_processed || 0).toLocaleString()}
                          </span>
                          {run.records_failed > 0 && (
                            <span className="text-xs text-red-400">
                              {run.records_failed.toLocaleString()} failed
                            </span>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <Badge variant="outline" className="text-xs">
                          {run.triggered_by || "manual"}
                        </Badge>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedRun(selectedRun === run.id ? null : run.id)}
                          className="text-purple-400 hover:text-purple-300"
                        >
                          <Eye className="w-4 h-4 mr-2" />
                          {selectedRun === run.id ? "Hide" : "Details"}
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Expanded Run Details */}
            {selectedRun && (
              <div className="mt-4 p-4 bg-surface-hover border border-border rounded-lg">
                {(() => {
                  const run = filteredRuns.find(r => r.id === selectedRun)
                  if (!run) return null
                  return (
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <h4 className="text-lg font-semibold text-foreground">Run Details</h4>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setSelectedRun(null)}
                          className="text-foreground-muted hover:text-foreground"
                        >
                          Close
                        </Button>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Run ID</p>
                          <p className="text-sm font-mono text-foreground">{run.id}</p>
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Pipeline ID</p>
                          <p className="text-sm font-mono text-foreground">{run.pipeline_id}</p>
                        </div>
                        {run.completed_at && (
                          <div>
                            <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Completed At</p>
                            <p className="text-sm text-foreground">
                              {format(new Date(run.completed_at), "MMM dd, yyyy HH:mm:ss")}
                            </p>
                          </div>
                        )}
                        <div>
                          <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Status</p>
                          {getStatusBadge(run.status)}
                        </div>
                        <div>
                          <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Records Processed</p>
                          <p className="text-sm text-foreground">{(run.records_processed || 0).toLocaleString()}</p>
                        </div>
                        {run.records_failed > 0 && (
                          <div>
                            <p className="text-xs font-semibold text-foreground-muted uppercase mb-1">Records Failed</p>
                            <p className="text-sm text-red-400">{run.records_failed.toLocaleString()}</p>
                          </div>
                        )}
                      </div>
                      {run.error_message && (
                        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                          <div className="flex items-start gap-2">
                            <AlertCircle className="w-5 h-5 text-red-400 mt-0.5 flex-shrink-0" />
                            <div className="flex-1">
                              <p className="text-sm font-semibold text-red-400 mb-1">Error Message</p>
                              <p className="text-sm text-foreground-muted whitespace-pre-wrap font-mono">
                                {run.error_message}
                              </p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )
                })()}
              </div>
            )}
          </Card>
        )}

        <ErrorToastComponent />
      </div>
    </ProtectedPage>
  )
}
