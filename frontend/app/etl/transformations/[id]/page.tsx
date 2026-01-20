"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { PageHeader } from "@/components/ui/page-header"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import {
  Code2,
  ArrowLeft,
  Edit,
  Trash2,
  Loader2,
  CheckCircle,
  XCircle,
  AlertCircle,
  Copy,
  Play,
  FileText,
  Tag,
  Calendar,
  Database,
  Download,
} from "lucide-react"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { useErrorToast } from "@/components/ui/error-toast"
import { useConfirmDialog } from "@/components/ui/confirm-dialog"
import { fetchConnections } from "@/lib/store/slices/connectionSlice"
import { apiClient } from "@/lib/api/client"
import { format } from "date-fns"
import { cn } from "@/lib/utils"
import { motion } from "framer-motion"

export default function ETLTransformationDetailPage() {
  const router = useRouter()
  const params = useParams()
  const transformationId = params?.id as string
  const dispatch = useAppDispatch()
  const { connections } = useAppSelector((state) => state.connections)
  const { showError, ErrorToastComponent } = useErrorToast()
  const { showConfirm, ConfirmDialogComponent } = useConfirmDialog()
  const [transformation, setTransformation] = useState<any>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)
  const [testDialogOpen, setTestDialogOpen] = useState(false)
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>("")
  const [testLimit, setTestLimit] = useState<number>(100)
  const [testResults, setTestResults] = useState<any>(null)
  const [testing, setTesting] = useState(false)

  useEffect(() => {
    if (transformationId) {
      fetchTransformation()
    }
    dispatch(fetchConnections())
  }, [dispatch, transformationId])

  const fetchTransformation = async () => {
    try {
      setIsLoading(true)
      const data = await apiClient.getETLTransformation(transformationId)
      setTransformation(data)
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || "Failed to load transformation"
      showError(errorMessage, "Load Failed")
      router.push("/etl/transformations")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async () => {
    if (!transformationId || !transformation) return
    
    const confirmed = await showConfirm({
      title: "Delete Transformation",
      message: `Are you sure you want to delete "${transformation.name}"? This action cannot be undone.`,
      confirmText: "Delete",
      cancelText: "Cancel",
      variant: "destructive"
    })

    if (!confirmed) return

    setActionLoading("delete")
    try {
      await apiClient.deleteETLTransformation(transformationId)
      showError("Transformation deleted successfully!", "Success", "success")
      router.push("/etl/transformations")
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || "Failed to delete transformation"
      showError(errorMessage, "Delete Failed")
    } finally {
      setActionLoading(null)
    }
  }

  const handleEdit = () => {
    router.push(`/etl/transformations/${transformationId}/edit`)
  }

  const handleCopy = () => {
    if (transformation?.sql_query) {
      navigator.clipboard.writeText(transformation.sql_query)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const handleTest = () => {
    setTestDialogOpen(true)
    setTestResults(null)
    setSelectedConnectionId("")
  }

  const executeTest = async () => {
    if (!selectedConnectionId) {
      showError("Please select a connection to test against", "Validation Error")
      return
    }

    if (!transformationId) return

    setTesting(true)
    setTestResults(null)
    try {
      const result = await apiClient.testETLTransformation(transformationId, selectedConnectionId, testLimit)
      setTestResults(result)
      if (result.success) {
        showError(result.message || "Test executed successfully!", "Success", "success")
      } else {
        showError(result.message || "Test failed", "Test Failed")
      }
    } catch (error: any) {
      const errorMessage = error?.response?.data?.detail || error?.message || "Failed to execute test"
      showError(errorMessage, "Test Failed")
      setTestResults({
        success: false,
        message: errorMessage,
        error: errorMessage
      })
    } finally {
      setTesting(false)
    }
  }

  const handleExportResults = () => {
    if (!testResults?.rows || testResults.rows.length === 0) {
      showError("No results to export", "Export Error")
      return
    }

    const headers = testResults.columns || Object.keys(testResults.rows[0] || {})
    const csv = [
      headers.join(","),
      ...testResults.rows.map((row: any) => 
        headers.map(header => {
          const value = row[header] ?? row[header.toLowerCase()] ?? ""
          return typeof value === 'string' && value.includes(',') ? `"${value}"` : value
        }).join(",")
      )
    ].join("\n")
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `transformation-test-${transformationId}-${Date.now()}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  if (isLoading) {
    return (
      <ProtectedPage path="/etl/transformations">
        <div className="flex items-center justify-center h-screen">
          <Loader2 className="w-6 h-6 animate-spin text-blue-500" />
          <span className="ml-2 text-foreground-muted">Loading transformation...</span>
        </div>
      </ProtectedPage>
    )
  }

  if (!transformation) {
    return (
      <ProtectedPage path="/etl/transformations">
        <div className="p-6">
          <Card className="p-12 text-center">
            <AlertCircle className="w-16 h-16 mx-auto mb-4 text-red-400/50" />
            <h3 className="text-xl font-bold text-foreground mb-2">Transformation Not Found</h3>
            <p className="text-foreground-muted mb-6">The transformation you're looking for doesn't exist or has been deleted.</p>
            <Button onClick={() => router.push("/etl/transformations")}>
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Transformations
            </Button>
          </Card>
        </div>
      </ProtectedPage>
    )
  }

  return (
    <ProtectedPage path="/etl/transformations">
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
              title={transformation.name}
              subtitle={transformation.description || "Transformation Details"}
              icon={Code2}
            />
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              onClick={handleTest}
              className="border-green-500/30 text-green-400 hover:bg-green-500/10"
            >
              <Play className="w-4 h-4 mr-2" />
              Test
            </Button>
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

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main SQL Query */}
          <Card className="lg:col-span-2 p-6 bg-surface border-border shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Code2 className="w-5 h-5 text-blue-400" /> SQL Query
              </h3>
              <Button
                variant="outline"
                size="sm"
                onClick={handleCopy}
                className="border-border text-foreground-muted hover:text-foreground"
              >
                {copied ? (
                  <>
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="w-4 h-4 mr-2" />
                    Copy
                  </>
                )}
              </Button>
            </div>
            <div className="bg-background border border-border rounded-lg p-4 font-mono text-sm text-foreground overflow-x-auto max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap break-words m-0">{transformation.sql_query || "-- No SQL query defined"}</pre>
            </div>
          </Card>

          {/* Metadata */}
          <Card className="p-6 bg-surface border-border shadow-lg">
            <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-purple-400" /> Details
            </h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-foreground-muted mb-2">Status</p>
                {transformation.is_reusable ? (
                  <Badge className="bg-blue-500/20 text-blue-400 border-blue-500/30 flex items-center gap-1 w-fit">
                    <CheckCircle className="w-3 h-3" /> Reusable
                  </Badge>
                ) : (
                  <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30 flex items-center gap-1 w-fit">
                    <XCircle className="w-3 h-3" /> Single Use
                  </Badge>
                )}
              </div>

              <div>
                <p className="text-sm text-foreground-muted mb-2">Version</p>
                <p className="text-foreground font-semibold">Version {transformation.version || 1}</p>
              </div>

              <div>
                <p className="text-sm text-foreground-muted mb-2 flex items-center gap-1">
                  <Tag className="w-4 h-4" /> Tags
                </p>
                {transformation.tags && transformation.tags.length > 0 ? (
                  <div className="flex flex-wrap gap-2">
                    {transformation.tags.map((tag: string, idx: number) => (
                      <Badge key={idx} variant="secondary" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-foreground-muted">{transformation.tags?.length || 0} tags</p>
                )}
              </div>

              {transformation.created_at && (
                <div>
                  <p className="text-sm text-foreground-muted mb-2 flex items-center gap-1">
                    <Calendar className="w-4 h-4" /> Created
                  </p>
                  <p className="text-foreground font-medium text-sm">
                    {format(new Date(transformation.created_at), "PPP 'at' p")}
                  </p>
                </div>
              )}

              {transformation.updated_at && (
                <div>
                  <p className="text-sm text-foreground-muted mb-2 flex items-center gap-1">
                    <Calendar className="w-4 h-4" /> Last Updated
                  </p>
                  <p className="text-foreground font-medium text-sm">
                    {format(new Date(transformation.updated_at), "PPP 'at' p")}
                  </p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Input/Output Schemas */}
        {(transformation.input_schema || transformation.output_schema) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {transformation.input_schema && Object.keys(transformation.input_schema).length > 0 && (
              <Card className="p-6 bg-surface border-border shadow-lg">
                <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-cyan-400" /> Input Schema
                </h3>
                <div className="bg-background border border-border rounded-lg p-4">
                  <pre className="text-sm text-foreground-muted overflow-x-auto">
                    {JSON.stringify(transformation.input_schema, null, 2)}
                  </pre>
                </div>
              </Card>
            )}

            {transformation.output_schema && Object.keys(transformation.output_schema).length > 0 && (
              <Card className="p-6 bg-surface border-border shadow-lg">
                <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5 text-emerald-400" /> Output Schema
                </h3>
                <div className="bg-background border border-border rounded-lg p-4">
                  <pre className="text-sm text-foreground-muted overflow-x-auto">
                    {JSON.stringify(transformation.output_schema, null, 2)}
                  </pre>
                </div>
              </Card>
            )}
          </div>
        )}

        {/* Test Dialog */}
        <Dialog open={testDialogOpen} onOpenChange={setTestDialogOpen}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Play className="w-5 h-5 text-green-400" />
                Test Transformation: {transformation?.name}
              </DialogTitle>
              <DialogDescription>
                Execute the SQL query against a selected connection to test the transformation.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="connection">Select Connection *</Label>
                {connections.length === 0 ? (
                  <div className="text-sm text-red-400">
                    No active connections found. Please create a connection first.
                  </div>
                ) : (
                  <Select value={selectedConnectionId} onValueChange={setSelectedConnectionId}>
                    <SelectTrigger className="w-full bg-background border-border">
                      <SelectValue placeholder="Select a connection" />
                    </SelectTrigger>
                    <SelectContent>
                      {connections.filter(c => c.is_active).map((conn) => (
                        <SelectItem key={conn.id} value={conn.id}>
                          <div className="flex items-center gap-2">
                            <Database className="w-4 h-4" />
                            <span>{conn.name}</span>
                            <Badge variant="outline" className="ml-2 text-xs">
                              {conn.connection_type}
                            </Badge>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="limit">Result Limit</Label>
                <Input
                  id="limit"
                  type="number"
                  min={1}
                  max={1000}
                  value={testLimit}
                  onChange={(e) => setTestLimit(parseInt(e.target.value) || 100)}
                  className="bg-background border-border"
                />
                <p className="text-xs text-foreground-muted">Maximum number of rows to return (1-1000)</p>
              </div>

              {transformation?.sql_query && (
                <div className="space-y-2">
                  <Label>SQL Query to Execute</Label>
                  <div className="bg-background border border-border rounded-lg p-3 font-mono text-xs text-foreground-muted overflow-x-auto">
                    <pre className="whitespace-pre-wrap break-words m-0">{transformation.sql_query}</pre>
                  </div>
                </div>
              )}

              {testResults && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Test Results</Label>
                    {testResults.success && testResults.rows && testResults.rows.length > 0 && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={handleExportResults}
                        className="border-border text-foreground-muted hover:text-foreground"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Export CSV
                      </Button>
                    )}
                  </div>
                  
                  {testResults.success ? (
                    <Card className="p-4 bg-green-500/10 border-green-500/30">
                      <div className="flex items-center gap-2 mb-3">
                        <CheckCircle className="w-5 h-5 text-green-400" />
                        <span className="font-semibold text-green-400">{testResults.message}</span>
                      </div>
                      
                      {testResults.rows && testResults.rows.length > 0 ? (
                        <div className="space-y-2">
                          <p className="text-sm text-foreground-muted">
                            Returned {testResults.row_count} row(s) with {testResults.columns?.length || 0} column(s)
                          </p>
                          <div className="overflow-x-auto max-h-96 overflow-y-auto border border-border rounded-lg">
                            <table className="w-full text-sm text-left">
                              <thead className="text-xs text-foreground-muted uppercase bg-surface-hover border-b border-border sticky top-0">
                                <tr>
                                  {testResults.columns?.map((col: string) => (
                                    <th key={col} scope="col" className="px-4 py-2 font-semibold">
                                      {col}
                                    </th>
                                  ))}
                                </tr>
                              </thead>
                              <tbody>
                                {testResults.rows.map((row: any, idx: number) => (
                                  <motion.tr
                                    key={idx}
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    transition={{ delay: idx * 0.02 }}
                                    className="bg-background border-b border-border hover:bg-surface-hover transition-colors"
                                  >
                                    {testResults.columns?.map((col: string) => (
                                      <td key={col} className="px-4 py-2 text-foreground-muted">
                                        {row[col] ?? row[col.toLowerCase()] ?? "NULL"}
                                      </td>
                                    ))}
                                  </motion.tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        </div>
                      ) : (
                        <p className="text-sm text-foreground-muted">Query executed successfully but returned no rows.</p>
                      )}
                    </Card>
                  ) : (
                    <Card className="p-4 bg-red-500/10 border-red-500/30">
                      <div className="flex items-center gap-2 mb-2">
                        <XCircle className="w-5 h-5 text-red-400" />
                        <span className="font-semibold text-red-400">Test Failed</span>
                      </div>
                      <p className="text-sm text-foreground-muted">{testResults.message || testResults.error}</p>
                      {testResults.query && (
                        <div className="mt-3 p-2 bg-background border border-border rounded text-xs font-mono text-foreground-muted">
                          {testResults.query}
                        </div>
                      )}
                    </Card>
                  )}
                </div>
              )}
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => {
                  setTestDialogOpen(false)
                  setTestResults(null)
                }}
              >
                Close
              </Button>
              <Button
                onClick={executeTest}
                disabled={!selectedConnectionId || testing || connections.length === 0}
                className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white"
              >
                {testing ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Testing...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Run Test
                  </>
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <ErrorToastComponent />
        <ConfirmDialogComponent />
      </div>
    </ProtectedPage>
  )
}

