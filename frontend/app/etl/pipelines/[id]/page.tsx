"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { PageHeader } from "@/components/ui/page-header"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import {
  GitBranch,
  ArrowLeft,
  Database,
  Play,
  Pause,
  Square,
  Edit,
  Trash2,
  RefreshCw,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Loader2,
  Sparkles,
} from "lucide-react"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { fetchETLPipeline, runETLPipeline, pauseETLPipeline, deleteETLPipeline, fetchETLRuns } from "@/lib/store/slices/etlSlice"
import { useErrorToast } from "@/components/ui/error-toast"
import { useConfirmDialog } from "@/components/ui/confirm-dialog"
import { formatDistanceToNow, format } from "date-fns"

export default function ETLPipelineDetailPage() {
  const router = useRouter()
  const params = useParams()
  const pipelineId = params?.id as string
  const dispatch = useAppDispatch()
  const { selectedPipeline, runs, isLoading } = useAppSelector((state) => state.etl)
  const { showError, ErrorToastComponent } = useErrorToast()
  const { showConfirm } = useConfirmDialog()
  const [actionLoading, setActionLoading] = useState<string | null>(null)

  useEffect(() => {
    if (pipelineId) {
      dispatch(fetchETLPipeline(pipelineId))
      dispatch(fetchETLRuns(pipelineId))
      // Refresh every 10 seconds
      const interval = setInterval(() => {
        dispatch(fetchETLPipeline(pipelineId))
        dispatch(fetchETLRuns(pipelineId))
      }, 10000)
      return () => clearInterval(interval)
    }
  }, [dispatch, pipelineId])

  const handleRun = async () => {
    if (!pipelineId) return
    setActionLoading("run")
    try {
      await dispatch(runETLPipeline(pipelineId)).unwrap()
      showError("ETL Pipeline started successfully!", "Success", "success")
      dispatch(fetchETLPipeline(pipelineId))
    } catch (error: any) {
      const errorMessage = error?.message || error?.payload || "Failed to start ETL pipeline"
      showError(errorMessage, "Start Failed")
    } finally {
      setActionLoading(null)
    }
  }

  const handlePause = async () => {
    if (!pipelineId) return
    setActionLoading("pause")
    try {
      await dispatch(pauseETLPipeline(pipelineId)).unwrap()
      showError("ETL Pipeline paused successfully!", "Success", "success")
      dispatch(fetchETLPipeline(pipelineId))
    } catch (error: any) {
      const errorMessage = error?.message || error?.payload || "Failed to pause ETL pipeline"
      showError(errorMessage, "Pause Failed")
    } finally {
      setActionLoading(null)
    }
  }

  const handleDelete = async () => {
    if (!pipelineId || !selectedPipeline) return
    
    const confirmed = await showConfirm({
      title: "Delete ETL Pipeline",
      message: `Are you sure you want to delete "${selectedPipeline.name}"? This action cannot be undone.`,
      confirmText: "Delete",
      cancelText: "Cancel",
      variant: "destructive"
    })

    if (!confirmed) return

    setActionLoading("delete")
    try {
      await dispatch(deleteETLPipeline(pipelineId)).unwrap()
      showError("ETL Pipeline deleted successfully!", "Success", "success")
      router.push("/etl/pipelines")
    } catch (error: any) {
      const errorMessage = error?.message || error?.payload || "Failed to delete ETL pipeline"
      showError(errorMessage, "Delete Failed")
    } finally {
      setActionLoading(null)
    }
  }

  const handleEdit = () => {
    router.push(`/etl/pipelines/${pipelineId}/edit`)
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "active":
        return <Badge className="bg-green-500/20 text-green-400 border-green-500/30 flex items-center gap-1">
          <CheckCircle className="w-3 h-3" /> Active
        </Badge>
      case "paused":
        return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30 flex items-center gap-1">
          <Pause className="w-3 h-3" /> Paused
        </Badge>
      case "failed":
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/30 flex items-center gap-1">
          <XCircle className="w-3 h-3" /> Failed
        </Badge>
      case "draft":
        return <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30 flex items-center gap-1">
          <Clock className="w-3 h-3" /> Draft
        </Badge>
      default:
        return <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">{status}</Badge>
    }
  }

  const getRunStatusBadge = (status: string) => {
    switch (status) {
      case "running":
        return <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 flex items-center gap-1">
          <Loader2 className="w-3 h-3 animate-spin" /> Running
        </Badge>
      case "completed":
        return <Badge className="bg-green-500/20 text-green-400 border-green-500/30 flex items-center gap-1">
          <CheckCircle className="w-3 h-3" /> Completed
        </Badge>
      case "failed":
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/30 flex items-center gap-1">
          <XCircle className="w-3 h-3" /> Failed
        </Badge>
      default:
        return <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">{status}</Badge>
    }
  }

  if (isLoading && !selectedPipeline) {
    return (
      <ProtectedPage path="/etl/pipelines">
        <div className="flex items-center justify-center h-screen">
          <Loader2 className="w-6 h-6 animate-spin text-purple-500" />
          <span className="ml-2 text-foreground-muted">Loading pipeline...</span>
        </div>
      </ProtectedPage>
    )
  }

  if (!selectedPipeline) {
    return (
      <ProtectedPage path="/etl/pipelines">
        <div className="p-6">
          <Card className="p-12 text-center">
            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400/50" />
            <h3 className="text-xl font-bold text-foreground mb-2">Pipeline Not Found</h3>
            <p className="text-foreground-muted mb-6">The pipeline you're looking for doesn't exist or has been deleted.</p>
            <Button onClick={() => router.push("/etl/pipelines")}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Pipelines
            </Button>
          </Card>
        </div>
      </ProtectedPage>
    )
  }

  return (
    <ProtectedPage path="/etl/pipelines">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              onClick={() => router.back()}
              className="border-border text-foreground-muted hover:text-foreground"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </Button>
            <PageHeader
              title={selectedPipeline.name}
              subtitle={selectedPipeline.description || "ETL Pipeline Details"}
              icon={GitBranch}
            />
          </div>
          <div className="flex items-center gap-2">
            {selectedPipeline.status === "active" ? (
              <Button
                variant="outline"
                onClick={handlePause}
                disabled={actionLoading === "pause"}
                className="border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10"
              >
                {actionLoading === "pause" ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Pause className="w-4 h-4 mr-2" />
                )}
                Pause
              </Button>
            ) : (
              <Button
                variant="outline"
                onClick={handleRun}
                disabled={actionLoading === "run"}
                className="border-green-500/30 text-green-400 hover:bg-green-500/10"
              >
                {actionLoading === "run" ? (
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                ) : (
                  <Play className="w-4 h-4 mr-2" />
                )}
                Run
              </Button>
            )}
            <Button
              variant="outline"
              onClick={handleEdit}
              className="border-border text-foreground-muted hover:text-foreground"
            >
              <Edit className="w-4 h-4 mr-2" />
              Edit
            </Button>
            <Button
              variant="outline"
              onClick={handleDelete}
              disabled={actionLoading === "delete"}
              className="border-red-500/30 text-red-400 hover:bg-red-500/10"
            >
              {actionLoading === "delete" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Trash2 className="w-4 h-4 mr-2" />
              )}
              Delete
            </Button>
          </div>
        </div>

        {/* Pipeline Info */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6 bg-surface border-border shadow-lg">
            <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <GitBranch className="w-5 h-5 text-purple-400" /> Pipeline Information
            </h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-foreground-muted">Status</p>
                <div className="mt-1">{getStatusBadge(selectedPipeline.status)}</div>
              </div>
              <div>
                <p className="text-sm text-foreground-muted">Source Type</p>
                <p className="text-foreground font-medium mt-1">{selectedPipeline.source_type}</p>
              </div>
              <div>
                <p className="text-sm text-foreground-muted">Target Type</p>
                <p className="text-foreground font-medium mt-1">{selectedPipeline.target_type}</p>
              </div>
              <div>
                <p className="text-sm text-foreground-muted">Transformations</p>
                <p className="text-foreground font-medium mt-1">
                  {selectedPipeline.transformation_ids?.length || 0} transformation(s)
                </p>
              </div>
              {selectedPipeline.created_at && (
                <div>
                  <p className="text-sm text-foreground-muted">Created</p>
                  <p className="text-foreground font-medium mt-1">
                    {format(new Date(selectedPipeline.created_at), "PPP 'at' p")}
                  </p>
                </div>
              )}
            </div>
          </Card>

          <Card className="p-6 bg-surface border-border shadow-lg">
            <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <Database className="w-5 h-5 text-cyan-400" /> Connection Details
            </h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-foreground-muted">Source</p>
                <p className="text-foreground font-medium mt-1">
                  {selectedPipeline.source_config?.connection_name || 
                   selectedPipeline.source_config?.connection_type || 
                   selectedPipeline.source_type}
                </p>
              </div>
              <div>
                <p className="text-sm text-foreground-muted">Target</p>
                <p className="text-foreground font-medium mt-1">
                  {selectedPipeline.target_config?.connection_name || 
                   selectedPipeline.target_config?.connection_type || 
                   selectedPipeline.target_type}
                </p>
              </div>
            </div>
          </Card>
        </div>

        {/* Latest Run */}
        {selectedPipeline.latest_run && (
          <Card className="p-6 bg-surface border-border shadow-lg">
            <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-emerald-400" /> Latest Run
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-foreground-muted">Status</p>
                <div className="mt-1">{getRunStatusBadge(selectedPipeline.latest_run.status)}</div>
              </div>
              <div>
                <p className="text-sm text-foreground-muted">Records Processed</p>
                <p className="text-foreground font-medium mt-1">
                  {selectedPipeline.latest_run.records_processed?.toLocaleString() || 0}
                </p>
              </div>
              {selectedPipeline.latest_run.started_at && (
                <div>
                  <p className="text-sm text-foreground-muted">Started</p>
                  <p className="text-foreground font-medium mt-1">
                    {format(new Date(selectedPipeline.latest_run.started_at), "PPP 'at' p")}
                  </p>
                </div>
              )}
            </div>
          </Card>
        )}

        {/* Run History */}
        <Card className="p-6 bg-surface border-border shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-400" /> Run History
            </h3>
            <Button
              variant="outline"
              size="sm"
              onClick={() => dispatch(fetchETLRuns(pipelineId))}
              className="border-border text-foreground-muted hover:text-foreground"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              Refresh
            </Button>
          </div>
          {runs.length === 0 ? (
            <div className="text-center py-8 text-foreground-muted">
              <Clock className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>No runs yet. Start the pipeline to see run history.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {runs.slice(0, 10).map((run) => (
                <div
                  key={run.id}
                  className="p-4 bg-background border border-border rounded-lg hover:border-purple-500/30 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {getRunStatusBadge(run.status)}
                      <div>
                        <p className="text-sm font-medium text-foreground">
                          Run {run.id.substring(0, 8)}
                        </p>
                        {run.started_at && (
                          <p className="text-xs text-foreground-muted">
                            {formatDistanceToNow(new Date(run.started_at), { addSuffix: true })}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-4 text-sm text-foreground-muted">
                      <span>{run.records_processed?.toLocaleString() || 0} records</span>
                      {run.duration_seconds && (
                        <span>{Math.floor(run.duration_seconds / 60)}m {run.duration_seconds % 60}s</span>
                      )}
                    </div>
                  </div>
                  {run.error_message && (
                    <div className="mt-2 p-2 bg-red-500/10 border border-red-500/20 rounded text-sm text-red-400">
                      {run.error_message}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </Card>

        <ErrorToastComponent />
      </div>
    </ProtectedPage>
  )
}

