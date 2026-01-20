"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { PageHeader } from "@/components/ui/page-header"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import { Plus, Code2, Search, Edit, Trash2, Eye, Loader2 } from "lucide-react"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { fetchETLTransformations } from "@/lib/store/slices/etlSlice"
import { useErrorToast } from "@/components/ui/error-toast"
import { useConfirmDialog } from "@/components/ui/confirm-dialog"

export default function TransformationsPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { showError, ErrorToastComponent } = useErrorToast()
  const { showConfirm, ConfirmDialogComponent } = useConfirmDialog()
  const { transformations, isLoading } = useAppSelector((state) => state.etl)
  const [searchQuery, setSearchQuery] = useState("")

  useEffect(() => {
    dispatch(fetchETLTransformations())
    const interval = setInterval(() => {
      dispatch(fetchETLTransformations())
    }, 30000) // Refresh every 30 seconds
    return () => clearInterval(interval)
  }, [dispatch])

  const filteredTransformations = transformations.filter((t) =>
    t.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    t.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  const handleDelete = async (id: string) => {
    const confirmed = await showConfirm({
      title: "Delete Transformation",
      message: "Are you sure you want to delete this transformation? This action cannot be undone.",
      confirmText: "Delete",
      cancelText: "Cancel",
      variant: "destructive",
    })
    if (!confirmed) return

    showError("Delete functionality will be implemented soon", "Coming Soon", "info")
  }

  return (
    <ProtectedPage path="/etl/transformations">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <PageHeader
            title="Transformations"
            subtitle="Manage reusable SQL transformations and data enrichment logic"
            icon={Code2}
          />
          <Button
            onClick={() => router.push("/etl/transformations/create")}
            className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            New Transformation
          </Button>
        </div>

        <div className="flex items-center gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-foreground-muted" />
            <Input
              placeholder="Search transformations..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 bg-background border-border"
            />
          </div>
          <Badge variant="outline" className="text-sm">
            {filteredTransformations.length} transformation{filteredTransformations.length !== 1 ? 's' : ''}
          </Badge>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <Loader2 className="w-8 h-8 animate-spin text-blue-400" />
            <span className="ml-3 text-foreground-muted">Loading transformations...</span>
          </div>
        ) : filteredTransformations.length === 0 ? (
          <Card className="p-12 text-center">
            <Code2 className="w-16 h-16 mx-auto mb-4 text-purple-400/50" />
            <h3 className="text-xl font-bold text-foreground mb-2">No Transformations Found</h3>
            <p className="text-foreground-muted mb-6">
              {searchQuery ? "No transformations match your search." : "Create reusable SQL transformations for your ETL pipelines"}
            </p>
            <Button
              onClick={() => router.push("/etl/transformations/create")}
              className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white"
            >
              <Plus className="w-4 h-4 mr-2" />
              Create Transformation
            </Button>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredTransformations.map((transformation) => (
              <Card
                key={transformation.id}
                className="p-6 bg-surface border-border shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 group"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-foreground mb-1 group-hover:text-blue-400 transition-colors">
                      {transformation.name}
                    </h3>
                    <p className="text-sm text-foreground-muted line-clamp-2">
                      {transformation.description || "No description"}
                    </p>
                  </div>
                  {transformation.is_reusable && (
                    <Badge variant="outline" className="text-xs bg-blue-500/10 text-blue-400 border-blue-500/30">
                      Reusable
                    </Badge>
                  )}
                </div>

                <div className="mb-4">
                  <div className="bg-background border border-border rounded p-3 font-mono text-xs text-foreground-muted line-clamp-3 overflow-hidden sql-preview">
                    <pre className="whitespace-pre-wrap break-words m-0">
                      {transformation.sql_query || "-- No SQL query defined"}
                    </pre>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-foreground-muted mb-4">
                  <span>Version {transformation.version}</span>
                  <span>{transformation.tags?.length || 0} tag{transformation.tags?.length !== 1 ? 's' : ''}</span>
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push(`/etl/transformations/${transformation.id}`)}
                    className="flex-1 border-blue-500/30 text-blue-400 hover:bg-blue-500/10"
                  >
                    <Eye className="w-4 h-4 mr-2" />
                    View
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => router.push(`/etl/transformations/${transformation.id}/edit`)}
                    className="flex-1 border-purple-500/30 text-purple-400 hover:bg-purple-500/10"
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Edit
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleDelete(transformation.id)}
                    className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </Card>
            ))}
          </div>
        )}
        <ErrorToastComponent />
        <ConfirmDialogComponent />
      </div>
    </ProtectedPage>
  )
}

