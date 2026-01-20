"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { PageHeader } from "@/components/ui/page-header"
import {
  Plus,
  GitBranch,
  Play,
  Pause,
  Square,
  Edit,
  Trash2,
  Eye,
  Database,
  ArrowRight,
  Sparkles,
  CheckCircle,
  AlertCircle,
  Clock,
} from "lucide-react"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { fetchETLPipelines, runETLPipeline, pauseETLPipeline, deleteETLPipeline } from "@/lib/store/slices/etlSlice"
import { useErrorToast } from "@/components/ui/error-toast"
import { useConfirmDialog } from "@/components/ui/confirm-dialog"

export default function ETLPipelinesPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { pipelines: etlPipelines, isLoading } = useAppSelector((state) => state.etl)
  const { showError, ErrorToastComponent } = useErrorToast()
  const { showConfirm } = useConfirmDialog()
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  useEffect(() => {
    dispatch(fetchETLPipelines())
    // Refresh every 10 seconds
    const interval = setInterval(() => {
      dispatch(fetchETLPipelines())
    }, 10000)
    return () => clearInterval(interval)
  }, [dispatch])

  const handleRun = async (pipelineId: string) => {
    setActionLoading(pipelineId)
    try {
      await dispatch(runETLPipeline(pipelineId)).unwrap()
      showError("ETL Pipeline started successfully!", "Success", "success")
      dispatch(fetchETLPipelines()) // Refresh list
    } catch (error: any) {
      const errorMessage = error?.message || error?.payload || "Failed to start ETL pipeline"
      showError(errorMessage, "Start Failed")
    } finally {
      setActionLoading(null)
    }
  }

  const handlePause = async (pipelineId: string) => {
    setActionLoading(pipelineId)
    try {
      await dispatch(pauseETLPipeline(pipelineId)).unwrap()
      showError("ETL Pipeline paused successfully!", "Success", "success")
      dispatch(fetchETLPipelines()) // Refresh list
    } catch (error: any) {
      const errorMessage = error?.message || error?.payload || "Failed to pause ETL pipeline"
      showError(errorMessage, "Pause Failed")
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async (pipelineId: string, pipelineName: string) => {
    const confirmed = await showConfirm({
      title: "Delete ETL Pipeline",
      message: `Are you sure you want to delete "${pipelineName}"? This action cannot be undone.`,
      confirmText: "Delete",
      cancelText: "Cancel",
      variant: "destructive"
    })

    if (!confirmed) return

    setActionLoading(pipelineId)
    try {
      await dispatch(deleteETLPipeline(pipelineId)).unwrap()
      showError("ETL Pipeline deleted successfully!", "Success", "success")
      dispatch(fetchETLPipelines()) // Refresh list
    } catch (error: any) {
      const errorMessage = error?.message || error?.payload || "Failed to delete ETL pipeline"
      showError(errorMessage, "Delete Failed")
    } finally {
      setActionLoading(null)
    }
  }

  const handleView = (pipelineId: string) => {
    router.push(`/etl/pipelines/${pipelineId}`)
  }

  const handleEdit = (pipelineId: string) => {
    router.push(`/etl/pipelines/${pipelineId}/edit`)
  }

  // Transform ETL pipelines to display format
  const pipelines = etlPipelines.map((p) => ({
    id: p.id,
    name: p.name,
    status: p.status,
    source: p.source_config?.topic || p.source_config?.connection || `${p.source_type}://${p.source_config?.host || ''}`,
    target: p.target_config?.table || p.target_config?.topic || `${p.target_type}://${p.target_config?.host || ''}`,
    transformations: p.transformation_ids?.length || 0,
    lastRun: p.latest_run?.started_at,
    nextRun: p.schedule_config?.next_run,
    recordsProcessed: p.latest_run?.records_processed || 0,
  }))

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-500/20 text-green-400 border-green-500/30">Active</Badge>
      case "paused":
        return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">Paused</Badge>
      case "failed":
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/30">Failed</Badge>
      default:
        return <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">{status}</Badge>
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <PageHeader
          title="ETL Pipelines"
          subtitle="Manage your data transformation pipelines"
          icon={GitBranch}
        />
        <Button
          onClick={() => router.push("/etl/pipelines/create")}
          className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 hover:from-purple-500/30 hover:to-pink-500/30 text-purple-400 border border-purple-500/30"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Pipeline
        </Button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-400"></div>
        </div>
      ) : pipelines.length === 0 ? (
        <Card className="p-12 text-center">
          <Sparkles className="w-16 h-16 mx-auto mb-4 text-purple-400/50" />
          <h3 className="text-xl font-bold text-foreground mb-2">No ETL Pipelines</h3>
          <p className="text-foreground-muted mb-6">Get started by creating your first ETL pipeline</p>
          <Button onClick={() => router.push("/etl/pipelines/create")}>
            <Plus className="w-4 h-4 mr-2" />
            Create Pipeline
          </Button>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {pipelines.map((pipeline) => (
            <Card
              key={pipeline.id}
              className="p-6 bg-surface border-border shadow-lg hover:shadow-2xl transition-all duration-300 group"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="p-2 bg-purple-500/20 rounded-lg">
                      <GitBranch className="w-5 h-5 text-purple-400" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-foreground mb-1">{pipeline.name}</h3>
                      {getStatusBadge(pipeline.status)}
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div className="flex items-center gap-2 text-sm text-foreground-muted">
                      <Database className="w-4 h-4" />
                      <span className="truncate">{pipeline.source}</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-foreground-muted hidden md:block" />
                    <div className="flex items-center gap-2 text-sm text-foreground-muted">
                      <Database className="w-4 h-4" />
                      <span className="truncate">{pipeline.target}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-6 mt-4 text-sm text-foreground-muted">
                    <span>{pipeline.transformations} transformations</span>
                    <span>•</span>
                    <span>{(pipeline.recordsProcessed / 1000).toFixed(0)}K records</span>
                    {pipeline.lastRun && (
                      <>
                        <span>•</span>
                        <span className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          Last run: {new Date(pipeline.lastRun).toLocaleString()}
                        </span>
                      </>
                    )}
                  </div>
                </div>

                <div className="flex items-center gap-2 ml-4">
                  {pipeline.status === "active" ? (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handlePause(pipeline.id)}
                      disabled={actionLoading === pipeline.id}
                      title="Pause Pipeline"
                    >
                      <Pause className="w-4 h-4" />
                    </Button>
                  ) : (
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => handleRun(pipeline.id)}
                      disabled={actionLoading === pipeline.id}
                      title="Run Pipeline"
                    >
                      <Play className="w-4 h-4" />
                    </Button>
                  )}
                  <Button 
                    variant="outline" 
                    size="sm" 
                    onClick={() => handleView(pipeline.id)}
                    title="View Pipeline"
                  >
                    <Eye className="w-4 h-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm"
                    onClick={() => handleEdit(pipeline.id)}
                    title="Edit Pipeline"
                  >
                    <Edit className="w-4 h-4" />
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="text-red-400 hover:text-red-300"
                    onClick={() => handleDelete(pipeline.id, pipeline.name)}
                    disabled={actionLoading === pipeline.id}
                    title="Delete Pipeline"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
      <ErrorToastComponent />
    </div>
  )
}

