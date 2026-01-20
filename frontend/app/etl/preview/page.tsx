"use client"

import { useState, useEffect, useMemo } from "react"
import { useRouter } from "next/navigation"
import { PageHeader } from "@/components/ui/page-header"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import {
  Eye,
  Database,
  ArrowRight,
  RefreshCw,
  Loader2,
  Search,
  Download,
  Filter,
  Code2,
  Sparkles,
  Play,
  CheckCircle,
  AlertCircle,
} from "lucide-react"
import { useAppSelector, useAppDispatch } from "@/lib/store/hooks"
import { fetchETLPipelines } from "@/lib/store/slices/etlSlice"
import { useErrorToast } from "@/components/ui/error-toast"
import { format } from "date-fns"
import { motion } from "framer-motion"

// Mock data stages for demonstration
const dataStages = [
  {
    id: "raw",
    label: "Raw Event",
    description: "Original data from source",
    icon: Database,
    color: "cyan",
    sampleData: [
      { id: 1, name: "John Doe", email: "john@example.com", age: 30, status: "active", created_at: "2024-01-15T10:30:00Z" },
      { id: 2, name: "Jane Smith", email: "jane@example.com", age: 25, status: "active", created_at: "2024-01-15T11:00:00Z" },
      { id: 3, name: "Bob Johnson", email: "bob@example.com", age: 35, status: "inactive", created_at: "2024-01-15T12:00:00Z" },
    ]
  },
  {
    id: "sql",
    label: "After SQL",
    description: "Data after SQL transformation",
    icon: Code2,
    color: "blue",
    sampleData: [
      { id: 1, full_name: "JOHN DOE", email: "john@example.com", age: 30, is_active: true, created_at: "2024-01-15T10:30:00Z" },
      { id: 2, full_name: "JANE SMITH", email: "jane@example.com", age: 25, is_active: true, created_at: "2024-01-15T11:00:00Z" },
      { id: 3, full_name: "BOB JOHNSON", email: "bob@example.com", age: 35, is_active: false, created_at: "2024-01-15T12:00:00Z" },
    ]
  },
  {
    id: "filter",
    label: "After Filter",
    description: "Data after filtering rules",
    icon: Filter,
    color: "purple",
    sampleData: [
      { id: 1, full_name: "JOHN DOE", email: "john@example.com", age: 30, is_active: true, created_at: "2024-01-15T10:30:00Z" },
      { id: 2, full_name: "JANE SMITH", email: "jane@example.com", age: 25, is_active: true, created_at: "2024-01-15T11:00:00Z" },
    ]
  },
  {
    id: "final",
    label: "Final Output",
    description: "Data ready for target",
    icon: CheckCircle,
    color: "emerald",
    sampleData: [
      { id: 1, full_name: "JOHN DOE", email: "john@example.com", age: 30, is_active: true, created_at: "2024-01-15T10:30:00Z", enriched: true },
      { id: 2, full_name: "JANE SMITH", email: "jane@example.com", age: 25, is_active: true, created_at: "2024-01-15T11:00:00Z", enriched: true },
    ]
  },
]

export default function DataPreviewPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { pipelines, isLoading } = useAppSelector((state) => state.etl)
  const { showError, ErrorToastComponent } = useErrorToast()
  const [selectedPipelineId, setSelectedPipelineId] = useState<string>("")
  const [selectedStage, setSelectedStage] = useState<string>("raw")
  const [searchQuery, setSearchQuery] = useState("")
  const [loadingPreview, setLoadingPreview] = useState(false)

  useEffect(() => {
    dispatch(fetchETLPipelines())
  }, [dispatch])

  const selectedPipeline = useMemo(() => {
    return pipelines.find(p => p.id === selectedPipelineId)
  }, [pipelines, selectedPipelineId])

  const currentStage = useMemo(() => {
    return dataStages.find(s => s.id === selectedStage) || dataStages[0]
  }, [selectedStage])

  const filteredData = useMemo(() => {
    if (!currentStage?.sampleData) return []
    if (!searchQuery) return currentStage.sampleData.slice(0, 10) // Limit to 10 rows for preview
    
    const query = searchQuery.toLowerCase()
    return currentStage.sampleData
      .filter((row: any) => 
        Object.values(row).some(val => 
          String(val).toLowerCase().includes(query)
        )
      )
      .slice(0, 10)
  }, [currentStage, searchQuery])

  const handlePreview = async () => {
    if (!selectedPipelineId) {
      showError("Please select a pipeline first", "Validation Error")
      return
    }
    
    setLoadingPreview(true)
    try {
      // TODO: Implement actual data preview API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      showError("Data preview generated successfully!", "Success", "success")
    } catch (error: any) {
      showError(error?.message || "Failed to generate preview", "Preview Failed")
    } finally {
      setLoadingPreview(false)
    }
  }

  const handleExport = () => {
    if (!filteredData.length) {
      showError("No data to export", "Export Error")
      return
    }
    
    // Convert to CSV
    const headers = Object.keys(filteredData[0])
    const csv = [
      headers.join(","),
      ...filteredData.map((row: any) => 
        headers.map(header => {
          const value = row[header]
          return typeof value === 'string' && value.includes(',') ? `"${value}"` : value
        }).join(",")
      )
    ].join("\n")
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `data-preview-${currentStage.id}-${Date.now()}.csv`
    a.click()
    window.URL.revokeObjectURL(url)
  }

  return (
    <ProtectedPage path="/etl/preview">
      <div className="p-6 space-y-6">
        <PageHeader
          title="Data Preview"
          subtitle="Preview and debug data at each stage of your ETL pipeline"
          icon={Eye}
        />

        {/* Pipeline Selection */}
        <Card className="p-6 bg-surface border-border shadow-lg">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div className="space-y-2">
              <Label htmlFor="pipeline">Select Pipeline *</Label>
              {isLoading ? (
                <div className="flex items-center gap-2 text-foreground-muted">
                  <Loader2 className="w-4 h-4 animate-spin" /> Loading pipelines...
                </div>
              ) : pipelines.length === 0 ? (
                <div className="text-sm text-red-400">
                  No pipelines found. Create one first.
                  <Button 
                    variant="link" 
                    className="p-0 h-auto ml-2 text-red-300" 
                    onClick={() => router.push("/etl/pipelines/create")}
                  >
                    Create Pipeline
                  </Button>
                </div>
              ) : (
                <Select
                  value={selectedPipelineId}
                  onValueChange={setSelectedPipelineId}
                >
                  <SelectTrigger className="w-full bg-background border-border">
                    <SelectValue placeholder="Select a pipeline" />
                  </SelectTrigger>
                  <SelectContent>
                    {pipelines.map((pipeline) => (
                      <SelectItem key={pipeline.id} value={pipeline.id}>
                        {pipeline.name} ({pipeline.status})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="stage">Preview Stage</Label>
              <Select value={selectedStage} onValueChange={setSelectedStage}>
                <SelectTrigger className="w-full bg-background border-border">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {dataStages.map((stage) => (
                    <SelectItem key={stage.id} value={stage.id}>
                      {stage.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handlePreview}
              disabled={!selectedPipelineId || loadingPreview}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
            >
              {loadingPreview ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Loading...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Preview Data
                </>
              )}
            </Button>
          </div>

          {selectedPipeline && (
            <div className="mt-4 p-4 bg-background border border-border rounded-lg">
              <div className="flex items-center gap-3">
                <Database className="w-5 h-5 text-cyan-400" />
                <div className="flex-1">
                  <p className="font-semibold text-foreground">{selectedPipeline.name}</p>
                  <p className="text-sm text-foreground-muted">
                    {selectedPipeline.source_type} → {selectedPipeline.target_type}
                  </p>
                </div>
                <Badge className={selectedPipeline.status === 'active' ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}>
                  {selectedPipeline.status}
                </Badge>
              </div>
            </div>
          )}
        </Card>

        {/* Stage Navigation */}
        {selectedPipelineId && (
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {dataStages.map((stage, index) => {
              const StageIcon = stage.icon
              const isActive = selectedStage === stage.id
              const isCompleted = dataStages.findIndex(s => s.id === selectedStage) >= index
              
              return (
                <motion.div
                  key={stage.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-2"
                >
                  <Button
                    variant={isActive ? "default" : "outline"}
                    size="sm"
                    onClick={() => setSelectedStage(stage.id)}
                    className={`
                      ${isActive 
                        ? stage.color === 'cyan' ? 'bg-cyan-600 hover:bg-cyan-700' :
                          stage.color === 'blue' ? 'bg-blue-600 hover:bg-blue-700' :
                          stage.color === 'purple' ? 'bg-purple-600 hover:bg-purple-700' :
                          stage.color === 'emerald' ? 'bg-emerald-600 hover:bg-emerald-700' :
                          'bg-purple-600 hover:bg-purple-700'
                        : 'border-border text-foreground-muted hover:text-foreground'}
                      min-w-[150px] justify-start
                    `}
                  >
                    <StageIcon className="w-4 h-4 mr-2" />
                    {stage.label}
                  </Button>
                  {index < dataStages.length - 1 && (
                    <ArrowRight className="w-4 h-4 text-foreground-muted flex-shrink-0" />
                  )}
                </motion.div>
              )
            })}
          </div>
        )}

        {/* Data Preview Table */}
        {selectedPipelineId ? (
          <Card className="p-6 bg-surface border-border shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg font-bold text-foreground flex items-center gap-2 mb-1">
                  {currentStage && (() => {
                    const StageIcon = currentStage.icon
                    const colorClass = 
                      currentStage.color === 'cyan' ? 'text-cyan-400' :
                      currentStage.color === 'blue' ? 'text-blue-400' :
                      currentStage.color === 'purple' ? 'text-purple-400' :
                      currentStage.color === 'emerald' ? 'text-emerald-400' :
                      'text-purple-400'
                    return <StageIcon className={`w-5 h-5 ${colorClass}`} />
                  })()}
                  {currentStage?.label || "Data Preview"}
                </h3>
                <p className="text-sm text-foreground-muted">{currentStage?.description}</p>
              </div>
              <div className="flex items-center gap-2">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-foreground-muted" />
                  <Input
                    placeholder="Search data..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10 w-64 bg-background border-border"
                  />
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleExport}
                  disabled={filteredData.length === 0}
                  className="border-border text-foreground-muted hover:text-foreground"
                >
                  <Download className="w-4 h-4 mr-2" />
                  Export
                </Button>
              </div>
            </div>

            {filteredData.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                  <thead className="text-xs text-foreground-muted uppercase bg-surface-hover border-b border-border">
                    <tr>
                      {Object.keys(filteredData[0]).map((key) => (
                        <th key={key} scope="col" className="px-6 py-3 font-semibold">
                          {key}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {filteredData.map((row: any, rowIndex: number) => (
                      <motion.tr
                        key={rowIndex}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: rowIndex * 0.05 }}
                        className="bg-background border-b border-border hover:bg-surface-hover transition-colors"
                      >
                        {Object.values(row).map((value: any, colIndex: number) => (
                          <td key={colIndex} className="px-6 py-4 text-foreground-muted">
                            {typeof value === 'boolean' ? (
                              value ? (
                                <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                                  <CheckCircle className="w-3 h-3 mr-1" /> True
                                </Badge>
                              ) : (
                                <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                                  <AlertCircle className="w-3 h-3 mr-1" /> False
                                </Badge>
                              )
                            ) : typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}/) ? (
                              format(new Date(value), "PPP 'at' p")
                            ) : (
                              String(value)
                            )}
                          </td>
                        ))}
                      </motion.tr>
                    ))}
                  </tbody>
                </table>
                <div className="mt-4 text-sm text-foreground-muted text-center">
                  Showing {filteredData.length} of {currentStage?.sampleData?.length || 0} rows
                </div>
              </div>
            ) : (
              <div className="text-center py-12 text-foreground-muted">
                <Eye className="w-16 h-16 mx-auto mb-4 opacity-20" />
                <p className="text-lg font-semibold mb-2">No Data Available</p>
                <p className="text-sm">
                  {searchQuery ? "No data matches your search." : "Preview data by selecting a pipeline and clicking Preview Data."}
                </p>
              </div>
            )}
          </Card>
        ) : (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <Card className="p-12 text-center bg-gradient-to-br from-purple-500/10 via-pink-500/5 to-transparent border-purple-500/20">
              <motion.div
                initial={{ scale: 0.8 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="inline-block mb-6"
              >
                <div className="w-24 h-24 bg-gradient-to-br from-purple-500/30 to-pink-500/30 rounded-2xl flex items-center justify-center shadow-2xl shadow-purple-500/20">
                  <Eye className="w-12 h-12 text-purple-400" />
                </div>
              </motion.div>
              <h3 className="text-2xl font-bold text-foreground mb-2">Data Preview & Debug</h3>
              <p className="text-foreground-muted mb-6 max-w-md mx-auto">
                View data transformations step by step. Select a pipeline above to get started.
              </p>
              {pipelines.length > 0 && (
                <Button
                  onClick={() => setSelectedPipelineId(pipelines[0].id)}
                  className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
                >
                  <Sparkles className="w-4 h-4 mr-2" />
                  Select First Pipeline
                </Button>
              )}
            </Card>
          </motion.div>
        )}

        <ErrorToastComponent />
      </div>
    </ProtectedPage>
  )
}
