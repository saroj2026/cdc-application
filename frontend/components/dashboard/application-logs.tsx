"use client"

import { useState, useEffect, useRef, useCallback } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
// import { ScrollArea } from "@/components/ui/scroll-area" // Using div with overflow instead
import { apiClient } from "@/lib/api/client"
import { format } from "date-fns"
import { Search, RefreshCw, Download, Filter, X } from "lucide-react"
import { Loader2 } from "lucide-react"

interface LogEntry {
  id: string
  level: string
  logger: string
  message: string
  timestamp: string
  module?: string
  function?: string
  line?: number
  extra?: any
}

export function ApplicationLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [searchTerm, setSearchTerm] = useState("")
  const [selectedLevel, setSelectedLevel] = useState<string>("all")
  const [availableLevels, setAvailableLevels] = useState<string[]>([])
  const [currentPage, setCurrentPage] = useState(1)
  const [totalLogs, setTotalLogs] = useState(0)
  const logsPerPage = 50
  const scrollAreaRef = useRef<HTMLDivElement>(null)
  const autoRefreshIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Fetch log levels
  useEffect(() => {
    const fetchLevels = async () => {
      try {
        const levels = await apiClient.getLogLevels()
        setAvailableLevels(levels)
      } catch (error) {
        console.error("Error fetching log levels:", error)
        setAvailableLevels(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
      }
    }
    fetchLevels()
  }, [])

  // Fetch logs
  const fetchLogs = useCallback(async (silent = false) => {
    if (!silent) {
      setIsLoading(true)
    } else {
      setIsRefreshing(true)
    }

    try {
      const skip = (currentPage - 1) * logsPerPage
      const level = selectedLevel !== "all" ? selectedLevel : undefined
      const search = searchTerm.trim() || undefined

      const response = await apiClient.getApplicationLogs(
        skip,
        logsPerPage,
        level,
        search
      )

      // Debug logging
      if (process.env.NODE_ENV === 'development') {
        console.log('[ApplicationLogs] API Response:', {
          responseType: typeof response,
          isArray: Array.isArray(response),
          hasLogs: response && typeof response === 'object' && 'logs' in response,
          logsCount: Array.isArray(response) ? response.length : (response?.logs?.length || 0)
        })
      }

      // Handle both array response (backward compatibility) and object response
      if (Array.isArray(response)) {
        setLogs(response)
        setTotalLogs(response.length >= logsPerPage ? currentPage * logsPerPage + 1 : response.length)
      } else if (response && typeof response === 'object' && 'logs' in response) {
        // New format with logs and total
        const logsArray = response.logs || []
        const total = response.total || logsArray.length
        setLogs(logsArray)
        setTotalLogs(total)
        
        if (process.env.NODE_ENV === 'development') {
          console.log('[ApplicationLogs] Set logs:', { count: logsArray.length, total })
        }
      } else {
        console.warn('[ApplicationLogs] Unexpected response format:', response)
        setLogs([])
        setTotalLogs(0)
      }
    } catch (error: any) {
      console.error("Error fetching logs:", error)
      setLogs([])
      setTotalLogs(0)
    } finally {
      setIsLoading(false)
      setIsRefreshing(false)
    }
  }, [currentPage, selectedLevel, searchTerm, logsPerPage])

  // Initial fetch
  useEffect(() => {
    fetchLogs()
  }, [fetchLogs])

  // Auto-refresh every 10 seconds
  useEffect(() => {
    autoRefreshIntervalRef.current = setInterval(() => {
      fetchLogs(true) // Silent refresh
    }, 10000)

    return () => {
      if (autoRefreshIntervalRef.current) {
        clearInterval(autoRefreshIntervalRef.current)
      }
    }
  }, [fetchLogs])

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm, selectedLevel])

  const getLevelColor = (level: string) => {
    const upperLevel = level.toUpperCase()
    if (upperLevel === "ERROR" || upperLevel === "CRITICAL") {
      return "bg-red-500/20 text-red-400 border-red-500/30"
    } else if (upperLevel === "WARNING" || upperLevel === "WARN") {
      return "bg-amber-500/20 text-amber-400 border-amber-500/30"
    } else if (upperLevel === "INFO") {
      return "bg-blue-500/20 text-blue-400 border-blue-500/30"
    } else if (upperLevel === "DEBUG") {
      return "bg-gray-500/20 text-gray-400 border-gray-500/30"
    }
    return "bg-foreground-muted/20 text-foreground-muted border-border"
  }

  const handleExport = () => {
    const logText = logs
      .map(log => {
        const timestamp = format(new Date(log.timestamp), "yyyy-MM-dd HH:mm:ss")
        return `[${timestamp}] [${log.level}] [${log.logger}] ${log.message}`
      })
      .join("\n")

    const blob = new Blob([logText], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = `application-logs-${format(new Date(), "yyyy-MM-dd-HH-mm-ss")}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  return (
    <Card className="p-6 bg-surface border-border shadow-xl">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-bold text-foreground flex items-center gap-2">
          <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
          Application Logs
        </h3>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
            className="bg-transparent border-border hover:bg-cyan-500/10 hover:border-cyan-500/50 hover:text-cyan-400 gap-2"
          >
            <Download className="w-4 h-4" />
            Export
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => fetchLogs()}
            disabled={isRefreshing}
            className="bg-transparent border-border hover:bg-teal-500/10 hover:border-teal-500/50 hover:text-teal-400 gap-2 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRefreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-4 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-foreground-muted" />
          <Input
            placeholder="Search logs..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 bg-surface border-border"
          />
          {searchTerm && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSearchTerm("")}
              className="absolute right-1 top-1/2 transform -translate-y-1/2 h-7 w-7 p-0"
            >
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>
        <Select value={selectedLevel} onValueChange={setSelectedLevel}>
          <SelectTrigger className="w-48 bg-surface border-border">
            <Filter className="w-4 h-4 mr-2" />
            <SelectValue placeholder="All Levels" />
          </SelectTrigger>
          <SelectContent className="bg-surface border-border">
            <SelectItem value="all">All Levels</SelectItem>
            {availableLevels.map((level) => (
              <SelectItem key={level} value={level}>
                {level}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Logs Display */}
      <div className="h-[500px] w-full rounded-md border border-border overflow-y-auto" ref={scrollAreaRef}>
        {isLoading && logs.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            <span className="ml-3 text-foreground-muted font-medium">Loading logs...</span>
          </div>
        ) : logs.length > 0 ? (
          <div className="p-4 space-y-2">
            {logs.map((log) => (
              <div
                key={log.id}
                className="p-3 rounded-lg border border-border/50 hover:bg-surface-hover/30 hover:border-border transition-all duration-200 font-mono text-sm"
              >
                <div className="flex items-start gap-3">
                  <Badge
                    variant="outline"
                    className={`${getLevelColor(log.level)} text-xs font-semibold shrink-0`}
                  >
                    {log.level}
                  </Badge>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-foreground-muted text-xs">
                        {format(new Date(log.timestamp), "yyyy-MM-dd HH:mm:ss.SSS")}
                      </span>
                      {log.logger && (
                        <span className="text-foreground-muted text-xs">[{log.logger}]</span>
                      )}
                      {log.module && (
                        <span className="text-foreground-muted text-xs">
                          {log.module}
                          {log.function && `::${log.function}`}
                          {log.line && `:${log.line}`}
                        </span>
                      )}
                    </div>
                    <p className="text-foreground break-words">{log.message}</p>
                    {log.extra && Object.keys(log.extra).length > 0 && (
                      <details className="mt-2">
                        <summary className="text-xs text-foreground-muted cursor-pointer hover:text-foreground">
                          Show extra data
                        </summary>
                        <pre className="mt-2 p-2 bg-surface-hover rounded text-xs text-foreground-muted overflow-x-auto">
                          {JSON.stringify(log.extra, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-foreground-muted">
            <div className="w-16 h-16 mb-4 opacity-20">
              <svg
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                className="w-full h-full"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
            </div>
            <p className="text-base font-medium">No logs found</p>
            <p className="text-sm mt-2">
              {searchTerm || selectedLevel !== "all"
                ? "Try adjusting your filters"
                : "Logs will appear here as the application runs"}
            </p>
          </div>
        )}
      </div>

      {/* Pagination */}
      {logs.length > 0 && (
        <div className="mt-4 flex items-center justify-between border-t border-border pt-4">
          <div className="text-sm text-foreground-muted">
            Showing {((currentPage - 1) * logsPerPage) + 1} to {Math.min(currentPage * logsPerPage, totalLogs)} of {totalLogs} logs
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
              disabled={currentPage === 1 || isLoading}
              className="bg-transparent border-border hover:bg-teal-500/10 hover:border-teal-500/50 hover:text-teal-400 disabled:opacity-50"
            >
              Previous
            </Button>
            <span className="text-sm text-foreground-muted px-2">
              Page {currentPage}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(prev => prev + 1)}
              disabled={logs.length < logsPerPage || isLoading}
              className="bg-transparent border-border hover:bg-teal-500/10 hover:border-teal-500/50 hover:text-teal-400 disabled:opacity-50"
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </Card>
  )
}

