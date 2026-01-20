"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { PageHeader } from "@/components/ui/page-header"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import { GitBranch, ArrowLeft, Save, Loader2, Database, CheckCircle, AlertCircle } from "lucide-react"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { createETLPipeline } from "@/lib/store/slices/etlSlice"
import { fetchConnections } from "@/lib/store/slices/connectionSlice"
import { useErrorToast } from "@/components/ui/error-toast"
import { DatabaseLogo } from "@/lib/database-logo-loader"
import { cn } from "@/lib/utils"

export default function CreateETLPipelinePage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { showError, ErrorToastComponent } = useErrorToast()
  const { connections } = useAppSelector((state) => state.connections)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    source_type: "connection", // Changed default to connection
    source_connection_id: "",
    source_config: {},
    target_type: "connection", // Changed default to connection
    target_connection_id: "",
    target_config: {},
    transformation_ids: [] as string[],
    schedule_config: {},
  })

  useEffect(() => {
    // Fetch connections when component mounts
    if (connections.length === 0) {
      dispatch(fetchConnections())
    }
  }, [dispatch, connections.length])

  // Filter connections by test status and role
  const sourceConnections = connections.filter(
    c => (c.last_test_status === "success" || c.last_test_status === true) && 
         (c.role === "source" || !c.role) // Include connections without role or with source role
  )

  const targetConnections = connections.filter(
    c => (c.last_test_status === "success" || c.last_test_status === true) && 
         (c.role === "target" || !c.role) // Include connections without role or with target role
  )

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      // Validate form data
      if (!formData.name || formData.name.trim() === "") {
        showError("Pipeline name is required", "Validation Error")
        setIsSubmitting(false)
        return
      }

      // Validate source configuration
      if (formData.source_type === "connection" && !formData.source_connection_id) {
        showError("Please select a source connection", "Validation Error")
        setIsSubmitting(false)
        return
      }

      // Validate target configuration
      if (formData.target_type === "connection" && !formData.target_connection_id) {
        showError("Please select a target connection", "Validation Error")
        setIsSubmitting(false)
        return
      }

      // Prepare source config based on selected connection or type
      let sourceConfig: Record<string, any> = {}
      if (formData.source_type === "connection" && formData.source_connection_id) {
        const sourceConn = connections.find(c => String(c.id) === formData.source_connection_id)
        if (!sourceConn) {
          showError("Selected source connection not found", "Validation Error")
          setIsSubmitting(false)
          return
        }
        sourceConfig = {
          connection_id: String(sourceConn.id),
          connection_name: sourceConn.name,
          connection_type: sourceConn.connection_type || sourceConn.database_type || "unknown",
          host: sourceConn.host,
          port: sourceConn.port,
          database: sourceConn.database,
        }
      } else {
        sourceConfig = formData.source_config || {}
      }

      // Prepare target config based on selected connection or type
      let targetConfig: Record<string, any> = {}
      if (formData.target_type === "connection" && formData.target_connection_id) {
        const targetConn = connections.find(c => String(c.id) === formData.target_connection_id)
        if (!targetConn) {
          showError("Selected target connection not found", "Validation Error")
          setIsSubmitting(false)
          return
        }
        targetConfig = {
          connection_id: String(targetConn.id),
          connection_name: targetConn.name,
          connection_type: targetConn.connection_type || targetConn.database_type || "unknown",
          host: targetConn.host,
          port: targetConn.port,
          database: targetConn.database,
        }
      } else {
        targetConfig = formData.target_config || {}
      }

      const pipelineData = {
        name: formData.name.trim(),
        description: formData.description?.trim() || null,
        source_type: formData.source_type === "connection" ? "database" : formData.source_type,
        source_config: sourceConfig,
        target_type: formData.target_type === "connection" ? "database" : formData.target_type,
        target_config: targetConfig,
        transformation_ids: formData.transformation_ids || [],
        schedule_config: formData.schedule_config || {},
      }

      await dispatch(createETLPipeline(pipelineData)).unwrap()
      showError("ETL Pipeline created successfully!", "Success", "success")
      router.push("/etl/pipelines")
    } catch (error: any) {
      console.error("ETL Pipeline creation error:", error)
      
      // Extract error message from various possible locations
      let errorMessage = "Failed to create ETL pipeline"
      
      // Check payload first (from Redux slice)
      if (error?.payload) {
        if (typeof error.payload === 'string') {
          errorMessage = error.payload
        } else if (error.payload?.detail) {
          errorMessage = typeof error.payload.detail === 'string' 
            ? error.payload.detail 
            : JSON.stringify(error.payload.detail)
        } else if (error.payload?.message) {
          errorMessage = error.payload.message
        }
      } 
      // Check message directly from error
      else if (error?.message) {
        errorMessage = error.message
      }
      // Check axios response
      else if (error?.response?.data?.detail) {
        errorMessage = typeof error.response.data.detail === 'string'
          ? error.response.data.detail
          : JSON.stringify(error.response.data.detail)
      } else if (error?.response?.data?.message) {
        errorMessage = error.response.data.message
      }
      
      // Handle specific database migration errors
      if (errorMessage.toLowerCase().includes('does not exist') || 
          errorMessage.toLowerCase().includes('relation') ||
          errorMessage.toLowerCase().includes('table')) {
        errorMessage = "Database tables not found. Please run database migrations:\n\ncd backend && alembic upgrade head"
      }
      
      showError(errorMessage, "Creation Failed")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <ProtectedPage path="/etl/pipelines/create">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <PageHeader
            title="Create ETL Pipeline"
            subtitle="Define a new data transformation pipeline"
            icon={GitBranch}
          />
          <Button
            variant="outline"
            onClick={() => router.back()}
            className="border-border text-foreground-muted hover:text-foreground"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
        </div>

        <form onSubmit={handleSubmit}>
          <Card className="p-6 bg-surface border-border shadow-lg space-y-6">
            <div className="space-y-2">
              <Label htmlFor="name">Pipeline Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Customer Data Pipeline"
                required
                className="bg-background border-border"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe what this pipeline does..."
                rows={3}
                className="bg-background border-border"
              />
            </div>

            {/* Source Configuration */}
            <div className="space-y-4 p-4 bg-cyan-500/5 border border-cyan-500/20 rounded-lg">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <Database className="w-5 h-5 text-cyan-400" />
                Source Configuration
              </h3>
              
              <div className="space-y-2">
                <Label htmlFor="source_type">Source Type *</Label>
                <select
                  id="source_type"
                  value={formData.source_type}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    source_type: e.target.value,
                    source_connection_id: "", // Reset connection when type changes
                  })}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground"
                  required
                >
                  <option value="connection">Existing Connection</option>
                  <option value="kafka">Kafka Topic</option>
                  <option value="cdc">CDC Pipeline</option>
                  <option value="s3">S3 Bucket</option>
                </select>
              </div>

              {formData.source_type === "connection" && (
                <div className="space-y-2">
                  <Label htmlFor="source_connection_id">Source Connection *</Label>
                  {sourceConnections.length === 0 ? (
                    <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-md">
                      <div className="flex items-center gap-2 text-yellow-400">
                        <AlertCircle className="w-4 h-4" />
                        <p className="text-sm">No successful source connections found.</p>
                      </div>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => router.push("/connections?create=true")}
                        className="mt-2 border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10"
                      >
                        Create Connection
                      </Button>
                    </div>
                  ) : (
                    <select
                      id="source_connection_id"
                      value={formData.source_connection_id}
                      onChange={(e) => setFormData({ ...formData, source_connection_id: e.target.value })}
                      className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground"
                      required
                    >
                      <option value="">Select a source connection</option>
                      {sourceConnections.map((conn) => (
                        <option key={conn.id} value={String(conn.id)}>
                          {conn.name} ({conn.connection_type || conn.database_type || "Unknown"})
                        </option>
                      ))}
                    </select>
                  )}
                  
                  {formData.source_connection_id && (() => {
                    const selectedConn = sourceConnections.find(
                      c => String(c.id) === formData.source_connection_id
                    )
                    if (!selectedConn) return null
                    return (
                      <div className="mt-3 p-3 bg-background border border-border rounded-md">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-cyan-500/10 rounded-lg flex items-center justify-center">
                            <DatabaseLogo
                              connectionType={selectedConn.connection_type || selectedConn.database_type || ""}
                              size={20}
                              className="w-5 h-5"
                            />
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-semibold text-foreground">{selectedConn.name}</p>
                            <p className="text-xs text-foreground-muted">
                              {selectedConn.connection_type || selectedConn.database_type} • {selectedConn.host}:{selectedConn.port}
                            </p>
                          </div>
                          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Active
                          </Badge>
                        </div>
                      </div>
                    )
                  })()}
                </div>
              )}
            </div>

            {/* Target Configuration */}
            <div className="space-y-4 p-4 bg-emerald-500/5 border border-emerald-500/20 rounded-lg">
              <h3 className="text-lg font-semibold text-foreground flex items-center gap-2">
                <Database className="w-5 h-5 text-emerald-400" />
                Target Configuration
              </h3>
              
              <div className="space-y-2">
                <Label htmlFor="target_type">Target Type *</Label>
                <select
                  id="target_type"
                  value={formData.target_type}
                  onChange={(e) => setFormData({ 
                    ...formData, 
                    target_type: e.target.value,
                    target_connection_id: "", // Reset connection when type changes
                  })}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground"
                  required
                >
                  <option value="connection">Existing Connection</option>
                  <option value="database">Database (Manual)</option>
                  <option value="kafka">Kafka Topic</option>
                  <option value="s3">S3 Bucket</option>
                </select>
              </div>

              {formData.target_type === "connection" && (
                <div className="space-y-2">
                  <Label htmlFor="target_connection_id">Target Connection *</Label>
                  {targetConnections.length === 0 ? (
                    <div className="p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-md">
                      <div className="flex items-center gap-2 text-yellow-400">
                        <AlertCircle className="w-4 h-4" />
                        <p className="text-sm">No successful target connections found.</p>
                      </div>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => router.push("/connections?create=true")}
                        className="mt-2 border-yellow-500/30 text-yellow-400 hover:bg-yellow-500/10"
                      >
                        Create Connection
                      </Button>
                    </div>
                  ) : (
                    <select
                      id="target_connection_id"
                      value={formData.target_connection_id}
                      onChange={(e) => setFormData({ ...formData, target_connection_id: e.target.value })}
                      className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground"
                      required
                    >
                      <option value="">Select a target connection</option>
                      {targetConnections.map((conn) => (
                        <option key={conn.id} value={String(conn.id)}>
                          {conn.name} ({conn.connection_type || conn.database_type || "Unknown"})
                        </option>
                      ))}
                    </select>
                  )}
                  
                  {formData.target_connection_id && (() => {
                    const selectedConn = targetConnections.find(
                      c => String(c.id) === formData.target_connection_id
                    )
                    if (!selectedConn) return null
                    return (
                      <div className="mt-3 p-3 bg-background border border-border rounded-md">
                        <div className="flex items-center gap-3">
                          <div className="p-2 bg-emerald-500/10 rounded-lg flex items-center justify-center">
                            <DatabaseLogo
                              connectionType={selectedConn.connection_type || selectedConn.database_type || ""}
                              size={20}
                              className="w-5 h-5"
                            />
                          </div>
                          <div className="flex-1">
                            <p className="text-sm font-semibold text-foreground">{selectedConn.name}</p>
                            <p className="text-xs text-foreground-muted">
                              {selectedConn.connection_type || selectedConn.database_type} • {selectedConn.host}:{selectedConn.port}
                            </p>
                          </div>
                          <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                            <CheckCircle className="w-3 h-3 mr-1" />
                            Active
                          </Badge>
                        </div>
                      </div>
                    )
                  })()}
                </div>
              )}
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-border">
              <Button
                type="button"
                variant="outline"
                onClick={() => router.back()}
                disabled={isSubmitting}
                className="border-border text-foreground-muted hover:text-foreground"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={
                  isSubmitting || 
                  !formData.name ||
                  (formData.source_type === "connection" && !formData.source_connection_id) ||
                  (formData.target_type === "connection" && !formData.target_connection_id)
                }
                className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Create Pipeline
                  </>
                )}
              </Button>
            </div>
          </Card>
        </form>
        <ErrorToastComponent />
      </div>
    </ProtectedPage>
  )
}

