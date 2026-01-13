"use client"

import { ProtectedPage } from "@/components/auth/ProtectedPage"

import { useState, useEffect, useMemo, useRef } from "react"
import { useRouter } from "next/navigation"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useAppSelector, useAppDispatch } from "@/lib/store/hooks"
import { fetchReplicationEvents, fetchMonitoringMetrics, setSelectedPipeline } from "@/lib/store/slices/monitoringSlice"
import { fetchPipelines } from "@/lib/store/slices/pipelineSlice"
import { wsClient } from "@/lib/websocket/client"
import { formatDistanceToNow } from "date-fns"
import { Loader2, Activity, Database, AlertCircle, CheckCircle, RefreshCw, Eye, RotateCw } from "lucide-react"
import { apiClient } from "@/lib/api/client"
import { PageHeader } from "@/components/ui/page-header"
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

export default function MonitoringPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { isAuthenticated, isLoading: authLoading } = useAppSelector((state) => state.auth)
  const { events, metrics, selectedPipelineId, isLoading } = useAppSelector((state) => state.monitoring)
  const { pipelines } = useAppSelector((state) => state.pipelines)
  const [mounted, setMounted] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const rowsPerPage = 10
  const [retryingEventId, setRetryingEventId] = useState<string | null>(null)
  const [isRefreshing, setIsRefreshing] = useState(false)

  // Handle client-side mounting
  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push("/auth/login")
    }
  }, [isAuthenticated, authLoading, router])

  // Fetch data on mount - fetch all events by default (todayOnly: false to show all events including test records)
  useEffect(() => {
    if (isAuthenticated) {
      dispatch(fetchPipelines())
      dispatch(fetchReplicationEvents({ limit: 500, todayOnly: false }))
    }
  }, [dispatch, isAuthenticated])

  // Track last fetched pipeline ID to prevent unnecessary refetches
  const lastFetchedPipelineIdRef = useRef<string | number | null>(null)
  const isInitialMountRef = useRef(true)
  
  // Stabilize selectedPipelineId to prevent unnecessary re-renders
  const stableSelectedPipelineId = useMemo(() => {
    if (!selectedPipelineId) return null
    // Normalize to string to ensure consistent comparison
    return String(selectedPipelineId)
  }, [selectedPipelineId])
  
  // Fetch events and metrics when pipeline is selected
  useEffect(() => {
    if (!isAuthenticated) return
    
    // Normalize pipeline ID for comparison
    const normalizedId = stableSelectedPipelineId ? stableSelectedPipelineId : null
    
    // On initial mount, skip the ref check to allow first fetch
    if (isInitialMountRef.current) {
      isInitialMountRef.current = false
    } else {
      // Skip if we've already fetched for this pipeline ID
      if (lastFetchedPipelineIdRef.current === normalizedId) {
        return
      }
    }
    
    lastFetchedPipelineIdRef.current = normalizedId
    
    if (normalizedId) {
      // Fetch events and metrics for selected pipeline
      const pipelineId = !isNaN(Number(normalizedId)) ? Number(normalizedId) : normalizedId
      if (pipelineId && pipelineId !== 'null' && pipelineId !== 'undefined') {
        dispatch(fetchReplicationEvents({ pipelineId, limit: 500, todayOnly: false }))
        dispatch(fetchMonitoringMetrics({ pipelineId })).catch(err => {
          console.error("Error fetching metrics:", err)
        })
      }
    } else {
      // Fetch all events when "All Pipelines" is selected
      dispatch(fetchReplicationEvents({ limit: 500, todayOnly: false }))
    }
  }, [dispatch, isAuthenticated, stableSelectedPipelineId]) // Use stable memoized value

  // Auto-refresh events every 5 seconds to catch new events
  // Use ref to store the latest selectedPipelineId to avoid recreating interval
  const selectedPipelineIdRef = useRef<string | number | null>(null)
  
  // Update ref in useEffect to prevent render-time side effects
  useEffect(() => {
    selectedPipelineIdRef.current = stableSelectedPipelineId
  }, [stableSelectedPipelineId])
  
  useEffect(() => {
    if (!isAuthenticated) return

    const interval = setInterval(() => {
      // Always fetch all events (not just today) to ensure we see recent updates
      const currentPipelineId = selectedPipelineIdRef.current
      if (currentPipelineId) {
        const pipelineId = !isNaN(Number(currentPipelineId)) ? Number(currentPipelineId) : String(currentPipelineId)
        if (pipelineId && pipelineId !== 'null' && pipelineId !== 'undefined') {
          dispatch(fetchReplicationEvents({ pipelineId, limit: 1000, todayOnly: false }))
          dispatch(fetchMonitoringMetrics({ pipelineId })).catch(err => {
            console.error("Error fetching metrics:", err)
          })
        }
      } else {
        dispatch(fetchReplicationEvents({ limit: 1000, todayOnly: false }))
      }
    }, 5000) // Refresh every 5 seconds

    return () => clearInterval(interval)
  }, [dispatch, isAuthenticated]) // Remove selectedPipelineId from deps, use ref instead

  // Track previous pipeline IDs to prevent unnecessary re-subscriptions
  const prevPipelineIdsRef = useRef<string>('')

  // Subscribe to pipelines only when pipeline IDs actually change
  // Use a stable pipeline IDs string to prevent infinite loops
  // Calculate IDs string - will be compared in useEffect to detect actual changes
  const stablePipelineIds = useMemo(() => {
    const pipelinesArray = Array.isArray(pipelines) ? pipelines : []
    if (pipelinesArray.length === 0) return ''
    return pipelinesArray
      .filter(p => p.id)
      .map(p => String(p.id))
      .sort()
      .join(',')
  }, [pipelines]) // Depend on pipelines array - string comparison in useEffect prevents unnecessary subscriptions
  
  useEffect(() => {
    const pipelinesArray = Array.isArray(pipelines) ? pipelines : []
    if (!isAuthenticated || pipelinesArray.length === 0) {
      return
    }

    // Only subscribe if pipeline IDs have changed
    if (stablePipelineIds !== prevPipelineIdsRef.current) {
      const pipelineIds = pipelinesArray
        .filter(p => p.id)
        .map(p => {
          // Handle both numeric IDs and MongoDB ObjectId strings
          const id = !isNaN(Number(p.id)) ? Number(p.id) : String(p.id)
          return id
        })

      // Unsubscribe from old pipelines
      if (prevPipelineIdsRef.current) {
        const prevIds = prevPipelineIdsRef.current.split(',').filter(Boolean)
        prevIds.forEach(id => {
          const pipelineId = !isNaN(Number(id)) ? Number(id) : id
          if (!pipelineIds.includes(pipelineId)) {
            wsClient.unsubscribePipeline(pipelineId)
          }
        })
      }

      // Subscribe to new pipelines
      pipelineIds.forEach(pipelineId => {
        wsClient.subscribePipeline(pipelineId)
      })

      prevPipelineIdsRef.current = stablePipelineIds
    }

    return () => {
      // Cleanup subscriptions on unmount
      if (prevPipelineIdsRef.current) {
        const pipelineIds = prevPipelineIdsRef.current.split(',').filter(Boolean)
        pipelineIds.forEach(id => {
          const pipelineId = !isNaN(Number(id)) ? Number(id) : id
          wsClient.unsubscribePipeline(pipelineId)
        })
      }
    }
  }, [isAuthenticated, stablePipelineIds]) // Use stablePipelineIds instead of pipelines array

  // Filter events by selected pipeline - memoized to prevent unnecessary recalculations
  const filteredEvents = useMemo(() => {
    return selectedPipelineId
      ? events.filter(e => String(e.pipeline_id) === String(selectedPipelineId))
      : events
  }, [events, selectedPipelineId])

  // Debug logging (only in development) - throttled to prevent excessive logging
  const debugLogTimeoutRef = useRef<NodeJS.Timeout | null>(null)
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      // Throttle debug logging to prevent excessive console output
      if (debugLogTimeoutRef.current) {
        clearTimeout(debugLogTimeoutRef.current)
      }
      
      debugLogTimeoutRef.current = setTimeout(() => {
        // Calculate filtered events count inline to avoid dependency on filteredEvents
        const filteredCount = selectedPipelineId 
          ? events.filter(e => String(e.pipeline_id) === String(selectedPipelineId)).length
          : events.length
        
        console.log('[Monitoring Page] Events in Redux:', events.length)
        console.log('[Monitoring Page] Filtered events:', filteredCount)
        console.log('[Monitoring Page] Selected pipeline ID:', selectedPipelineId)
        if (events.length > 0) {
          console.log('[Monitoring Page] First event pipeline_id:', events[0].pipeline_id)
          console.log('[Monitoring Page] First event status:', events[0].status)
          
          // Show status breakdown
          const statusBreakdown = events.reduce((acc, e) => {
            acc[e.status] = (acc[e.status] || 0) + 1
            return acc
          }, {} as Record<string, number>)
          console.log('[Monitoring Page] Status breakdown:', statusBreakdown)
        }
      }, 1000) // Throttle to once per second
      
      return () => {
        if (debugLogTimeoutRef.current) {
          clearTimeout(debugLogTimeoutRef.current)
        }
      }
    }
    // Only depend on events and selectedPipelineId, not filteredEvents to avoid infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [events.length, selectedPipelineId])

  // Calculate metrics from events
  const eventStats = useMemo(() => {
    // Calculate average latency only from events that have been applied (have latency_ms)
    const eventsWithLatency = filteredEvents.filter(e => e.latency_ms != null && e.latency_ms !== undefined && e.latency_ms > 0)
    const avgLatency = eventsWithLatency.length > 0
      ? eventsWithLatency.reduce((sum, e) => sum + (e.latency_ms || 0), 0) / eventsWithLatency.length
      : null // Use null to indicate no latency data available
    
    // Improved status detection - check error_message and status together
    const isSuccess = (e: any) => {
      // Must be applied/success AND have no error_message
      // Also check that error_message is not just whitespace or common null values
      const hasError = e.error_message && 
        String(e.error_message).trim() !== '' && 
        String(e.error_message).toLowerCase() !== 'none' &&
        String(e.error_message).toLowerCase() !== 'null'
      return (e.status === 'applied' || e.status === 'success') && !hasError
    }
    
    const isFailed = (e: any) => {
      // Failed if status is failed/error OR has error_message
      // Also check that error_message is a valid error (not empty/null)
      const hasError = e.error_message && 
        String(e.error_message).trim() !== '' && 
        String(e.error_message).toLowerCase() !== 'none' &&
        String(e.error_message).toLowerCase() !== 'null'
      return e.status === 'failed' || e.status === 'error' || !!hasError
    }
    
    const stats = {
      total: filteredEvents.length,
      insert: filteredEvents.filter(e => e.event_type === 'insert' || e.event_type === 'INSERT').length,
      update: filteredEvents.filter(e => e.event_type === 'update' || e.event_type === 'UPDATE').length,
      delete: filteredEvents.filter(e => e.event_type === 'delete' || e.event_type === 'DELETE').length,
      success: filteredEvents.filter(isSuccess).length,
      failed: filteredEvents.filter(isFailed).length,
      captured: filteredEvents.filter(e => e.status === 'captured' && !e.error_message).length,
      pending: filteredEvents.filter(e => (e.status === 'captured' || e.status === 'pending') && !e.error_message).length,
      avgLatency: avgLatency, // null if no events have latency data
    }
    
    // Debug logging (only in development)
    if (process.env.NODE_ENV === 'development' && filteredEvents.length > 0) {
      const statusCounts = filteredEvents.reduce((acc, e) => {
        acc[e.status] = (acc[e.status] || 0) + 1
        return acc
      }, {} as Record<string, number>)
      
      // Check for events with error_message
      const eventsWithErrors = filteredEvents.filter(e => !!e.error_message)
      const eventsWithAppliedStatus = filteredEvents.filter(e => e.status === 'applied' || e.status === 'success')
      const appliedWithErrors = filteredEvents.filter(e => (e.status === 'applied' || e.status === 'success') && !!e.error_message)
      
      console.log('[Monitoring] Event status breakdown:', statusCounts)
      console.log('[Monitoring] Success count:', stats.success, 'Failed count:', stats.failed, 'Captured/Pending:', stats.captured)
      console.log('[Monitoring] Events with error_message:', eventsWithErrors.length)
      console.log('[Monitoring] Events with applied/success status:', eventsWithAppliedStatus.length)
      console.log('[Monitoring] Events with applied/success status BUT have error_message:', appliedWithErrors.length)
      console.log('[Monitoring] Sample event details:', filteredEvents.slice(0, 5).map(e => ({ 
        id: e.id, 
        status: e.status, 
        hasError: !!e.error_message,
        errorMessage: e.error_message ? e.error_message.substring(0, 50) : null
      })))
    }
    
    return stats
  }, [filteredEvents])

  // Pagination for Recent CDC Events - MEMOIZED to prevent unnecessary recalculations
  const totalPages = useMemo(() => Math.ceil(filteredEvents.length / rowsPerPage), [filteredEvents.length, rowsPerPage])
  const paginatedEvents = useMemo(() => {
    return filteredEvents.slice(
      (currentPage - 1) * rowsPerPage,
      currentPage * rowsPerPage
    )
  }, [filteredEvents, currentPage, rowsPerPage])

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1)
  }, [selectedPipelineId])

  // Prepare chart data from metrics or events - MEMOIZED to prevent infinite loops
  // Filter events inline to avoid dependency on filteredEvents (breaks circular dependency)
  const chartData = useMemo(() => {
    const eventsArray = Array.isArray(events) ? events : []
    const metricsArray = Array.isArray(metrics) ? metrics : []
    
    if (metricsArray.length > 0) {
      // Use metrics data - get last 24 hours
      const now = new Date()
      const last24Hours = metricsArray
        .filter(m => {
          try {
            const metricTime = new Date(m.timestamp)
            const hoursDiff = (now.getTime() - metricTime.getTime()) / (1000 * 60 * 60)
            return hoursDiff <= 24
          } catch (err) {
            return false
          }
        })
        .slice(-24)
      
      if (last24Hours.length > 0) {
        return last24Hours.map(m => ({
          time: new Date(m.timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
          events: m.total_events || 0,
          latency: m.avg_latency_ms || 0,
          errors: m.error_count || 0,
        }))
      }
    }
    
    // Use events data - create 24 hour buckets
    const eventsToUse = selectedPipelineId
      ? eventsArray.filter(e => String(e.pipeline_id) === String(selectedPipelineId))
      : eventsArray
    
    const now = new Date()
    return Array.from({ length: 24 }, (_, i) => {
      const hourStart = new Date(now.getTime() - (23 - i) * 60 * 60 * 1000)
      const hourEnd = new Date(now.getTime() - (22 - i) * 60 * 60 * 1000)
      
      const hourEvents = eventsToUse.filter(e => {
        try {
          const eventTime = new Date(e.created_at)
          return eventTime >= hourStart && eventTime < hourEnd
        } catch (err) {
          return false
        }
      })
      
      const eventsCount = hourEvents.length
      const latency = eventsCount > 0
        ? hourEvents.reduce((sum, e) => sum + (e.latency_ms || 0), 0) / eventsCount
        : 0
      const errorsCount = hourEvents.filter(e => e.status === 'failed' || e.status === 'error').length
      
      return {
        time: hourStart.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false }),
        events: eventsCount,
        latency: Math.round(latency),
        errors: errorsCount,
      }
    })
  }, [metrics, events, selectedPipelineId]) // Use full arrays for proper updates

  if (authLoading || !mounted) {
    return (
      <div className="flex items-center justify-center h-screen">
        <Loader2 className="w-6 h-6 animate-spin text-foreground-muted" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return null
  }

  return (
    <ProtectedPage path="/monitoring" requiredPermission="view_metrics">
      <div className="p-6 space-y-6" suppressHydrationWarning>
        <PageHeader
          title="Real-Time Monitoring"
        subtitle="Live CDC event capture and replication metrics"
        icon={Eye}
        action={
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/20 rounded-md">
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
              <span className="text-xs font-medium text-cyan-400">Auto Sync: ON</span>
            </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              onClick={async () => {
                setIsRefreshing(true)
                try {
                  // Refresh pipelines first
                  await dispatch(fetchPipelines())
                  
                  // Then refresh events and metrics
                  if (selectedPipelineId) {
                    const pipelineId = !isNaN(Number(selectedPipelineId)) ? Number(selectedPipelineId) : String(selectedPipelineId)
                    await Promise.all([
                      dispatch(fetchReplicationEvents({ pipelineId, limit: 500, todayOnly: false })),
                      dispatch(fetchMonitoringMetrics({ pipelineId }))
                    ])
                  } else {
                    await dispatch(fetchReplicationEvents({ limit: 500, todayOnly: false }))
                  }
                } catch (error) {
                  console.error("Failed to refresh data:", error)
                } finally {
                  // Keep animation for at least 500ms for better UX
                  setTimeout(() => setIsRefreshing(false), 500)
                }
              }}
              disabled={isRefreshing}
              className="bg-teal-500/10 border-teal-500/30 text-teal-400 hover:bg-teal-500/30 hover:border-teal-500/70 hover:text-teal-300 gap-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <RefreshCw className={`w-4 h-4 transition-transform ${isRefreshing ? 'animate-spin' : ''}`} />
              {isRefreshing ? 'Refreshing...' : 'Refresh'}
            </Button>
            <Select
              value={selectedPipelineId ? String(selectedPipelineId) : 'all'}
              onValueChange={(value) => {
                if (value === 'all') {
                  dispatch(setSelectedPipeline(null))
                } else {
                  // Handle both numeric IDs and MongoDB ObjectId strings
                  const pipelineId = !isNaN(Number(value)) ? Number(value) : value
                  dispatch(setSelectedPipeline(pipelineId))
                }
              }}
            >
              <SelectTrigger className="w-48 bg-surface border-border">
                <SelectValue placeholder="All Pipelines" />
              </SelectTrigger>
              <SelectContent className="bg-surface border-border">
                <SelectItem value="all">All Pipelines</SelectItem>
                {Array.isArray(pipelines) ? pipelines.map(p => (
                  <SelectItem key={p.id} value={String(p.id)}>
                    {p.name}
                  </SelectItem>
                )) : null}
              </SelectContent>
            </Select>
          </div>
        </div>
      }
      />

      {/* Stats Cards - Enhanced with Gradients */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <Card className="p-5 bg-gradient-to-br from-blue-500/10 to-blue-600/5 border-blue-500/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">Total Events</p>
              <p className="text-3xl font-extrabold bg-gradient-to-r from-blue-400 to-blue-600 bg-clip-text text-transparent">{eventStats.total}</p>
            </div>
            <Activity className="w-10 h-10 text-blue-400" />
          </div>
        </Card>
        <Card className="p-5 bg-gradient-to-br from-green-500/10 to-emerald-600/5 border-green-500/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">Successfully Applied</p>
              <p className="text-3xl font-extrabold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent">{eventStats.success}</p>
              <p className="text-xs text-foreground-muted mt-1">
                {eventStats.total > 0 ? ((eventStats.success / eventStats.total) * 100).toFixed(1) : 0}% success rate
              </p>
            </div>
            <CheckCircle className="w-10 h-10 text-green-400" />
          </div>
        </Card>
        <Card className="p-5 bg-gradient-to-br from-cyan-500/10 to-cyan-600/5 border-cyan-500/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">Captured/Pending</p>
              <p className="text-3xl font-extrabold bg-gradient-to-r from-cyan-400 to-cyan-600 bg-clip-text text-transparent">{eventStats.captured}</p>
              <p className="text-xs text-foreground-muted mt-1">Awaiting application</p>
            </div>
            <Activity className="w-10 h-10 text-cyan-400 animate-pulse" />
          </div>
        </Card>
        <Card className="p-5 bg-gradient-to-br from-purple-500/10 to-purple-600/5 border-purple-500/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">Avg Latency</p>
              {eventStats.avgLatency != null ? (
                <p className="text-3xl font-extrabold bg-gradient-to-r from-purple-400 to-purple-600 bg-clip-text text-transparent">{Math.round(eventStats.avgLatency)}ms</p>
              ) : (
                <p className="text-3xl font-extrabold text-foreground-muted">N/A</p>
              )}
              <p className="text-xs text-foreground-muted mt-1">
                {eventStats.avgLatency != null 
                  ? `${filteredEvents.filter(e => e.latency_ms != null && e.latency_ms > 0).length} events with latency`
                  : 'No events applied yet'}
              </p>
            </div>
            <Database className="w-10 h-10 text-purple-400" />
          </div>
        </Card>
        <Card className="p-5 bg-gradient-to-br from-red-500/10 to-red-600/5 border-red-500/20 shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">Failed Events</p>
              <p className="text-3xl font-extrabold bg-gradient-to-r from-red-400 to-red-600 bg-clip-text text-transparent">{eventStats.failed}</p>
            </div>
            <AlertCircle className="w-10 h-10 text-red-400" />
          </div>
        </Card>
      </div>

      {/* Event Type Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="card-heartbeat bg-surface border-border p-4">
          <p className="text-sm text-foreground-muted mb-2">Event Types</p>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-foreground">Insert</span>
              <Badge variant="outline" className="bg-info/20 text-info">{eventStats.insert}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-foreground">Update</span>
              <Badge variant="outline" className="bg-warning/20 text-warning">{eventStats.update}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-foreground">Delete</span>
              <Badge variant="outline" className="bg-error/20 text-error">{eventStats.delete}</Badge>
            </div>
          </div>
        </Card>
        <Card className="card-heartbeat bg-surface border-border p-4">
          <p className="text-sm text-foreground-muted mb-2">Status</p>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-foreground">Success</span>
              <Badge variant="outline" className="bg-success/20 text-success">{eventStats.success}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-foreground">Failed</span>
              <Badge variant="outline" className="bg-error/20 text-error">{eventStats.failed}</Badge>
            </div>
            <div className="flex justify-between">
              <span className="text-foreground">Pending</span>
              <Badge variant="outline" className="bg-warning/20 text-warning">
                {eventStats.total - eventStats.success - eventStats.failed}
              </Badge>
            </div>
          </div>
        </Card>
        <Card className="card-heartbeat bg-surface border-border p-4">
          <p className="text-sm text-foreground-muted mb-2">WebSocket Status</p>
          <div className="flex items-center gap-2" suppressHydrationWarning>
            {mounted && (
              <>
                <div className={`w-2 h-2 rounded-full ${wsClient.isConnected() ? 'bg-success' : 'bg-error'}`} />
                <span className="text-foreground">
                  {wsClient.isConnected() ? 'Connected' : 'Disconnected'}
                </span>
              </>
            )}
            {!mounted && (
              <>
                <div className="w-2 h-2 rounded-full bg-foreground-muted" />
                <span className="text-foreground-muted">Loading...</span>
              </>
            )}
          </div>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="card-heartbeat bg-surface border-border p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Events Over Time (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3448" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a1f3a",
                  border: "1px solid #2d3448",
                  borderRadius: "0.5rem",
                }}
              />
              <Line
                type="monotone"
                dataKey="events"
                stroke="#0ea5e9"
                strokeWidth={2}
                dot={{ fill: "#0ea5e9", r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>

        <Card className="card-heartbeat bg-surface border-border p-6">
          <h3 className="text-lg font-semibold text-foreground mb-4">Latency & Errors</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#2d3448" />
              <XAxis dataKey="time" stroke="#9ca3af" />
              <YAxis stroke="#9ca3af" />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1a1f3a",
                  border: "1px solid #2d3448",
                  borderRadius: "0.5rem",
                }}
              />
              <Bar dataKey="latency" fill="#06b6d4" radius={[8, 8, 0, 0]} />
              <Bar dataKey="errors" fill="#ef4444" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Events Table */}
      <Card className="card-heartbeat bg-surface border-border p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">Recent CDC Events</h3>
        {isLoading && filteredEvents.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-6 h-6 animate-spin text-foreground-muted" />
            <span className="ml-2 text-foreground-muted">Loading events...</span>
          </div>
        ) : filteredEvents.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-surface-hover">
                <tr>
                  <th className="px-4 py-3 text-left text-foreground-muted font-medium">Time</th>
                  <th className="px-4 py-3 text-left text-foreground-muted font-medium">Pipeline</th>
                  <th className="px-4 py-3 text-left text-foreground-muted font-medium">Event Type</th>
                  <th className="px-4 py-3 text-left text-foreground-muted font-medium">Table</th>
                  <th className="px-4 py-3 text-left text-foreground-muted font-medium">LSN/Offset</th>
                  <th className="px-4 py-3 text-left text-foreground-muted font-medium">Status</th>
                  <th className="px-4 py-3 text-left text-foreground-muted font-medium">Latency</th>
                  <th className="px-4 py-3 text-left text-foreground-muted font-medium">Error</th>
                </tr>
              </thead>
              <tbody>
                {paginatedEvents.map((event) => {
                  const pipelinesArray = Array.isArray(pipelines) ? pipelines : []
                  const pipeline = pipelinesArray.find(p => String(p.id) === String(event.pipeline_id))
                  
                  // Improved status detection - check error_message first
                  const hasError = !!event.error_message
                  const isFailed = event.status === 'failed' || event.status === 'error' || hasError
                  const isCaptured = event.status === 'captured' && !hasError
                  const isApplied = (event.status === 'applied' || event.status === 'success') && !hasError
                  
                  return (
                    <tr 
                      key={event.id} 
                      className={`border-b border-border hover:bg-surface-hover transition-colors ${
                        isFailed ? 'bg-red-500/5 border-red-500/20' : 
                        isCaptured ? 'bg-blue-500/5 border-blue-500/10' : 
                        ''
                      }`}
                    >
                      <td className="px-4 py-3 text-foreground text-xs">
                        <div className="flex items-center gap-2">
                          {isCaptured && (
                            <div className="relative">
                              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
                              <div className="absolute inset-0 w-2 h-2 bg-cyan-400/50 rounded-full animate-ping" />
                            </div>
                          )}
                          {formatDistanceToNow(new Date(event.created_at), { addSuffix: true })}
                        </div>
                      </td>
                      <td className="px-4 py-3 text-foreground text-xs">
                        {pipeline?.name || `Pipeline ${event.pipeline_id}`}
                      </td>
                      <td className="px-4 py-3">
                        <Badge
                          variant="outline"
                          className={
                            event.event_type === 'insert'
                              ? 'bg-green-500/20 text-green-400 border-green-500/30'
                              : event.event_type === 'update'
                                ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
                                : 'bg-amber-500/20 text-amber-400 border-amber-500/30'
                          }
                        >
                          {event.event_type.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="px-4 py-3 text-foreground text-xs font-medium">{event.table_name}</td>
                      <td className="px-4 py-3 text-foreground text-xs font-mono">
                        {event.source_lsn ? (
                          <span className="text-cyan-400" title="PostgreSQL LSN">
                            LSN: {event.source_lsn}
                          </span>
                        ) : event.source_scn ? (
                          <span className="text-blue-400" title="Oracle SCN">
                            SCN: {event.source_scn}
                          </span>
                        ) : event.source_binlog_file ? (
                          <span className="text-green-400" title="MySQL Binlog">
                            {event.source_binlog_file}:{event.source_binlog_position}
                          </span>
                        ) : event.sql_server_lsn ? (
                          <span className="text-purple-400" title="SQL Server LSN">
                            LSN: {event.sql_server_lsn}
                          </span>
                        ) : (
                          <span className="text-foreground-muted">N/A</span>
                        )}
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Badge
                            variant="outline"
                            className={
                              isApplied
                                ? 'bg-green-500/20 text-green-400 border-green-500/30 font-semibold'
                                : isFailed
                                  ? 'bg-red-500/20 text-red-400 border-red-500/30 font-semibold animate-pulse'
                                  : 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30 font-semibold'
                            }
                          >
                            {isApplied && <CheckCircle className="w-3 h-3 mr-1" />}
                            {isFailed && <AlertCircle className="w-3 h-3 mr-1" />}
                            {isCaptured && <Activity className="w-3 h-3 mr-1 animate-pulse" />}
                            {event.status}
                          </Badge>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-foreground text-xs">
                        {event.latency_ms ? (
                          <span className={event.latency_ms > 5000 ? 'text-warning' : 'text-foreground'}>
                            {Math.round(event.latency_ms)}ms
                          </span>
                        ) : 'N/A'}
                      </td>
                      <td className="px-4 py-3 text-xs max-w-xs">
                        {isFailed ? (
                          event.error_message ? (
                            <div className="flex items-center gap-2">
                            <div className="group relative flex-1">
                              <div className="flex items-center gap-1 text-red-400 cursor-help">
                                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                                <span className="truncate">Error</span>
                              </div>
                              <div className="absolute left-0 top-full mt-1 z-50 hidden group-hover:block">
                                <div className="bg-red-950/95 border border-red-500/50 rounded-lg p-3 shadow-xl max-w-md">
                                  <div className="text-red-200 font-semibold mb-1 text-xs">Replication Failed</div>
                                  <div className="text-red-300 text-xs whitespace-pre-wrap break-words">
                                    {event.error_message.length > 200 
                                      ? event.error_message.substring(0, 200) + '...' 
                                      : event.error_message}
                                  </div>
                                  <div className="text-red-400/70 text-xs mt-2">
                                    Table: {event.table_name} | Type: {event.event_type}
                                  </div>
                                </div>
                              </div>
                            </div>
                            <Button
                              variant="ghost"
                              size="sm"
                              className="h-7 px-2 text-red-400 hover:text-red-300 hover:bg-red-500/10"
                              onClick={async () => {
                                if (!event.id) return
                                setRetryingEventId(event.id)
                                try {
                                  await apiClient.retryFailedEvent(event.id)
                                  // Refresh events
                                  dispatch(fetchReplicationEvents({ 
                                    pipeline_id: selectedPipelineId || undefined,
                                    limit: 1000 
                                  }))
                                } catch (error: any) {
                                  alert(`Failed to retry event: ${error.message || 'Unknown error'}`)
                                } finally {
                                  setRetryingEventId(null)
                                }
                              }}
                              disabled={retryingEventId === event.id}
                              title="Retry this failed event"
                            >
                              {retryingEventId === event.id ? (
                                <Loader2 className="w-3 h-3 animate-spin" />
                              ) : (
                                <RotateCw className="w-3 h-3" />
                              )}
                            </Button>
                            </div>
                          ) : (
                            <div className="flex items-center gap-1 text-red-400">
                              <AlertCircle className="w-4 h-4" />
                              <span>Failed</span>
                            </div>
                          )
                        ) : isApplied && !event.error_message ? (
                          <div className="flex items-center gap-1 text-green-400">
                            <CheckCircle className="w-4 h-4" />
                            <span>Success</span>
                          </div>
                        ) : isCaptured && !event.error_message ? (
                          <div className="flex items-center gap-1 text-cyan-400">
                            <Activity className="w-4 h-4 animate-pulse" />
                            <span>Captured</span>
                          </div>
                        ) : event.error_message ? (
                          <div className="flex items-center gap-1 text-red-400">
                            <AlertCircle className="w-4 h-4" />
                            <span>Error</span>
                          </div>
                        ) : (
                          <span className="text-foreground-muted">-</span>
                        )}
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div className="mt-6 flex items-center justify-between border-t border-border pt-4">
                <div className="text-sm text-foreground-muted">
                  Showing {((currentPage - 1) * rowsPerPage) + 1} to {Math.min(currentPage * rowsPerPage, filteredEvents.length)} of {filteredEvents.length} events
                </div>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="bg-transparent border-border hover:bg-teal-500/10 hover:border-teal-500/50 hover:text-teal-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                  >
                    Previous
                  </Button>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                      let pageNum;
                      if (totalPages <= 5) {
                        pageNum = i + 1;
                      } else if (currentPage <= 3) {
                        pageNum = i + 1;
                      } else if (currentPage >= totalPages - 2) {
                        pageNum = totalPages - 4 + i;
                      } else {
                        pageNum = currentPage - 2 + i;
                      }
                      return (
                        <Button
                          key={pageNum}
                          variant="outline"
                          size="sm"
                          onClick={() => setCurrentPage(pageNum)}
                          className={`min-w-[2.5rem] transition-all duration-200 ${currentPage === pageNum
                              ? 'bg-teal-500/20 border-teal-500/50 text-teal-400 font-bold'
                              : 'bg-transparent border-border hover:bg-teal-500/10 hover:border-teal-500/50 hover:text-teal-400'
                            }`}
                        >
                          {pageNum}
                        </Button>
                      );
                    })}
                  </div>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                    disabled={currentPage === totalPages}
                    className="bg-transparent border-border hover:bg-teal-500/10 hover:border-teal-500/50 hover:text-teal-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
                  >
                    Next
                  </Button>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-foreground-muted">
            <p>No events found. Events will appear here as they are captured.</p>
          </div>
        )}
      </Card>
      </div>
    </ProtectedPage>
  )
}
