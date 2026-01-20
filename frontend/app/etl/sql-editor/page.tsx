"use client"

import { useState, useEffect, useMemo } from "react"
import { useRouter } from "next/navigation"
import { PageHeader } from "@/components/ui/page-header"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import { Code, Play, Save, FileText, Database, Loader2 } from "lucide-react"
import { useAppSelector } from "@/lib/store/hooks"
import { canAccessPage } from "@/lib/store/slices/permissionSlice"

export default function SQLEditorPage() {
  const router = useRouter()
  const { user, isAuthenticated } = useAppSelector((state) => state.auth)
  const permissions = useAppSelector((state) => state.permissions)
  const [sqlQuery, setSqlQuery] = useState("-- Write your SQL query here\nSELECT * FROM table_name LIMIT 100;")
  const [queryResult, setQueryResult] = useState<any>(null)
  const [isExecuting, setIsExecuting] = useState(false)
  const [isSaving, setIsSaving] = useState(false)

  // Check if user can access ETL pages
  const canAccessEtl = useMemo(() => {
    if (!user || !isAuthenticated) return false
    const minimalState = { auth: { user, isAuthenticated }, permissions }
    return canAccessPage('/etl/sql-editor')(minimalState)
  }, [user, isAuthenticated, permissions])

  const handleExecute = async () => {
    setIsExecuting(true)
    try {
      // TODO: Integrate with actual SQL execution API
      await new Promise(resolve => setTimeout(resolve, 1000))
      setQueryResult({
        columns: ["id", "name", "created_at"],
        rows: [
          { id: 1, name: "Sample Data", created_at: new Date().toISOString() },
          { id: 2, name: "Another Row", created_at: new Date().toISOString() },
        ],
        rowCount: 2,
        executionTime: "15ms"
      })
    } catch (error) {
      console.error("Error executing SQL:", error)
      setQueryResult({ error: "Failed to execute query" })
    } finally {
      setIsExecuting(false)
    }
  }

  const handleSave = async () => {
    setIsSaving(true)
    try {
      // TODO: Save query as transformation
      await new Promise(resolve => setTimeout(resolve, 500))
      alert("Query saved as transformation")
    } catch (error) {
      console.error("Error saving query:", error)
    } finally {
      setIsSaving(false)
    }
  }

  if (!canAccessEtl) {
    return <ProtectedPage path="/etl/sql-editor" />
  }

  return (
    <ProtectedPage path="/etl/sql-editor">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <PageHeader
            title="SQL Editor"
            subtitle="Write, execute, and test SQL queries for your ETL transformations"
            icon={Code}
          />
          <div className="flex gap-3">
            <Button
              onClick={handleSave}
              disabled={isSaving}
              variant="outline"
              className="border-purple-500/30 text-purple-400 hover:bg-purple-500/10"
            >
              {isSaving ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4 mr-2" />
                  Save as Transformation
                </>
              )}
            </Button>
            <Button
              onClick={handleExecute}
              disabled={isExecuting || !sqlQuery.trim()}
              className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white"
            >
              {isExecuting ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Executing...
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  Execute Query
                </>
              )}
            </Button>
          </div>
        </div>

        {/* SQL Editor */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card className="p-6 bg-surface border-border shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Code className="w-5 h-5 text-purple-400" />
                SQL Query
              </h3>
              <Badge variant="outline" className="text-xs">
                SQL
              </Badge>
            </div>
            <textarea
              value={sqlQuery}
              onChange={(e) => setSqlQuery(e.target.value)}
              className="w-full h-[500px] p-4 bg-background border border-border rounded-lg font-mono text-sm text-foreground resize-none focus:outline-none focus:ring-2 focus:ring-purple-500/50"
              placeholder="-- Write your SQL query here"
            />
            <div className="mt-4 flex items-center gap-4 text-xs text-foreground-muted">
              <div className="flex items-center gap-2">
                <Database className="w-4 h-4" />
                <span>Connected to: Default Schema</span>
              </div>
              <div className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                <span>{sqlQuery.split('\n').length} lines</span>
              </div>
            </div>
          </Card>

          {/* Results Panel */}
          <Card className="p-6 bg-surface border-border shadow-lg">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-bold text-foreground flex items-center gap-2">
                <Database className="w-5 h-5 text-cyan-400" />
                Results
              </h3>
              {queryResult && !queryResult.error && (
                <Badge variant="outline" className="text-xs">
                  {queryResult.rowCount} rows • {queryResult.executionTime}
                </Badge>
              )}
            </div>
            <div className="h-[500px] overflow-auto">
              {!queryResult ? (
                <div className="h-full flex flex-col items-center justify-center text-foreground-muted">
                  <Database className="w-16 h-16 mb-4 opacity-20" />
                  <p className="text-base font-medium">No results yet</p>
                  <p className="text-sm mt-2">Execute a query to see results</p>
                </div>
              ) : queryResult.error ? (
                <div className="h-full flex flex-col items-center justify-center text-red-400">
                  <Database className="w-16 h-16 mb-4 opacity-20" />
                  <p className="text-base font-medium">{queryResult.error}</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-surface-hover border-b border-border sticky top-0">
                      <tr>
                        {queryResult.columns.map((col: string) => (
                          <th key={col} className="px-4 py-2 text-left font-semibold text-foreground">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {queryResult.rows.map((row: any, idx: number) => (
                        <tr key={idx} className="border-b border-border hover:bg-surface-hover transition-colors">
                          {queryResult.columns.map((col: string) => (
                            <td key={col} className="px-4 py-2 text-foreground-muted">
                              {row[col]?.toString() || "NULL"}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Schema Browser (Optional) */}
        <Card className="p-6 bg-surface border-border shadow-lg">
          <h3 className="text-lg font-bold text-foreground mb-4 flex items-center gap-2">
            <Database className="w-5 h-5 text-emerald-400" />
            Schema Browser
          </h3>
          <div className="text-sm text-foreground-muted">
            <p>Browse available tables and columns to build your queries</p>
            <p className="mt-2 text-xs">Feature coming soon...</p>
          </div>
        </Card>
      </div>
    </ProtectedPage>
  )
}

