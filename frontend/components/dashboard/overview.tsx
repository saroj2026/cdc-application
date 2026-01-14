"use client"

import { useState, useEffect, useMemo, useRef } from "react"
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts"
import { Card } from "@/components/ui/card"
import { Activity, Database, AlertCircle, CheckCircle, Loader2 } from "lucide-react"
import { useAppSelector, useAppDispatch } from "@/lib/store/hooks"
import { fetchReplicationEvents, fetchMonitoringMetrics, addReplicationEvent, addMonitoringMetric } from "@/lib/store/slices/monitoringSlice"
import { fetchPipelines } from "@/lib/store/slices/pipelineSlice"
import { wsClient } from "@/lib/websocket/client"
import { formatDistanceToNow } from "date-fns"
import { ApplicationLogs } from "./application-logs"

export function DashboardOverview() {
  const dispatch = useAppDispatch()
  const { events, metrics, isLoading } = useAppSelector((state) => state.monitoring)
  const { pipelines } = useAppSelector((state) => state.pipelines)

  const [chartData, setChartData] = useState<any[]>([])
  const [dashboardMetrics, setDashboardMetrics] = useState({
    activePipelines: 0,
    totalTables: 0,
    errorRate: 0,
    dataQuality: 0,
  })
  const [backendStats, setBackendStats] = useState<any>(null)

  // Request notification permission
  useEffect(() => {
    if (typeof window !== 'undefined' && 'Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission()
    }
  }, [])

  // Fetch initial data (only once on mount) - fetch 7 days of events
  const hasFetchedRef = useRef(false)
  useEffect(() => {
    if (hasFetchedRef.current) return
    hasFetchedRef.current = true

    dispatch(fetchPipelines())
    // Fetch 7 days of events for the charts
    const sevenDaysAgo = new Date()
    sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
    dispatch(fetchReplicationEvents({ 
      limit: 10000, 
      todayOnly: false,
      startDate: sevenDaysAgo.toISOString()
    }))
    
    // Fetch dashboard stats from backend
    import("@/lib/api/client").then(({ apiClient }) => {
      apiClient.getDashboardStats()
        .then(stats => {
          setBackendStats(stats)
        })
        .catch(err => {
          console.error("Error fetching dashboard stats:", err)
        })
    })
  }, [dispatch])

  // Auto-refresh events every 30 seconds to show 7 days of events
  useEffect(() => {
    const interval = setInterval(() => {
      const sevenDaysAgo = new Date()
      sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7)
      dispatch(fetchReplicationEvents({ 
        limit: 10000, 
        todayOnly: false,
        startDate: sevenDaysAgo.toISOString()
      }))
    }, 30000) // Refresh every 30 seconds

    return () => clearInterval(interval)
  }, [dispatch])

  // Track previous pipeline IDs to prevent unnecessary re-subscriptions
  const prevPipelineIdsRef = useRef<string>('')

  // Subscribe to pipelines for real-time updates (only when pipeline IDs change)
  useEffect(() => {
    const pipelinesArray = Array.isArray(pipelines) ? pipelines : []
    if (pipelinesArray.length === 0) {
      return
    }

    const currentPipelineIds = pipelinesArray
      .filter(p => p.id)
      .map(p => String(p.id))
      .sort()
      .join(',')

    // Only subscribe if pipeline IDs have changed
    if (currentPipelineIds !== prevPipelineIdsRef.current) {
      // Convert pipeline IDs properly - handle both numeric and MongoDB ObjectId strings
      const pipelineIds = pipelinesArray
        .filter(p => p.id)
        .map(p => {
          const idStr = String(p.id)
          const numId = Number(p.id)
          // Use number if valid, otherwise use string (for MongoDB ObjectIds)
          return !isNaN(numId) && isFinite(numId) ? numId : idStr
        })
        .filter(id => id && id !== 'NaN' && id !== 'undefined') // Filter out invalid IDs

      // Unsubscribe from old pipelines
      if (prevPipelineIdsRef.current) {
        const prevIds = prevPipelineIdsRef.current.split(',').filter(Boolean)
        prevIds.forEach(id => {
          // Try to convert to number, but keep as string if it's an ObjectId
          const numId = Number(id)
          const pipelineId = !isNaN(numId) && isFinite(numId) ? numId : id
          if (!pipelineIds.includes(pipelineId)) {
            wsClient.unsubscribePipeline(pipelineId)
          }
        })
      }

      // Subscribe to new pipelines
      pipelineIds.forEach(pipelineId => {
        wsClient.subscribePipeline(pipelineId)
      })

      prevPipelineIdsRef.current = currentPipelineIds
    }

    return () => {
      // Cleanup subscriptions on unmount
      if (prevPipelineIdsRef.current) {
        const pipelineIds = prevPipelineIdsRef.current.split(',').filter(Boolean)
        pipelineIds.forEach(id => {
          // Try to convert to number, but keep as string if it's an ObjectId
          const numId = Number(id)
          const pipelineId = !isNaN(numId) && isFinite(numId) ? numId : id
          wsClient.unsubscribePipeline(pipelineId)
        })
      }
    }
  }, [pipelines]) // Keep pipelines dependency but use ref to prevent loops

  // Calculate dashboard metrics - memoized to prevent infinite loops
  // Use backend stats if available, otherwise calculate from frontend data
  const dashboardMetricsMemo = useMemo(() => {
    // If we have backend stats, use them (more accurate)
    if (backendStats) {
      const totalEvents = backendStats.total_events || 0
      const failedEvents = backendStats.failed_events || 0
      const successEvents = backendStats.success_events || 0
      const errorRate = totalEvents > 0 ? (failedEvents / totalEvents) * 100 : 0
      const dataQuality = totalEvents > 0 ? (successEvents / totalEvents) * 100 : 100
      
      // Calculate total tables from pipelines
      const pipelinesArray = Array.isArray(pipelines) ? pipelines : []
      const totalTables = pipelinesArray.reduce((sum, p) => {
        const sourceTables = Array.isArray(p.source_tables) ? p.source_tables.length : 0
        return sum + sourceTables
      }, 0)
      
      return {
        activePipelines: backendStats.active_pipelines || 0,
        totalTables: totalTables,
        errorRate: errorRate,
        dataQuality: dataQuality,
      }
    }
    
    // Fallback to frontend calculation if backend stats not available
    const pipelinesArray = Array.isArray(pipelines) ? pipelines : []
    const eventsArray = Array.isArray(events) ? events : []
    
    // Calculate active pipelines
    const activePipelines = pipelinesArray.filter(p => p.status === 'active' || p.status === 'running').length

    // Calculate total tables
    const totalTables = pipelinesArray.reduce((sum, p) => {
      const sourceTables = Array.isArray(p.source_tables) ? p.source_tables.length : 0
      return sum + sourceTables
    }, 0)

    // Calculate error rate
    const totalEvents = eventsArray.length
    const errorEvents = eventsArray.filter(e => e.status === 'failed' || e.status === 'error').length
    const errorRate = totalEvents > 0 ? (errorEvents / totalEvents) * 100 : 0

    // Calculate data quality (success rate)
    const successEvents = eventsArray.filter(e => e.status === 'applied' || e.status === 'success').length
    const dataQuality = totalEvents > 0 ? (successEvents / totalEvents) * 100 : 100

    return {
      activePipelines,
      totalTables,
      errorRate,
      dataQuality,
    }
  }, [pipelines, events, backendStats]) // Include backendStats in dependencies
  
  // Update dashboard metrics only when memoized value changes
  useEffect(() => {
    setDashboardMetrics(dashboardMetricsMemo)
  }, [dashboardMetricsMemo])

  // Process metrics for charts (last 7 days, grouped by day)
  // Memoize chart data calculation to prevent infinite loops
  const chartDataMemo = useMemo(() => {
    const eventsArray = Array.isArray(events) ? events : []
    const metricsArray = Array.isArray(metrics) ? metrics : []
    
    // Always create 7 days of data buckets to ensure all days are represented
    const now = new Date()
    const days = Array.from({ length: 7 }, (_, i) => {
      const day = new Date(now.getTime() - (6 - i) * 24 * 60 * 60 * 1000)
      day.setHours(0, 0, 0, 0)
      return day
    })

    if (metricsArray.length > 0) {
      // Use metrics data for charts (last 7 days)
      return days.map((day, idx) => {
        const dayDate = day.toISOString().split('T')[0] // YYYY-MM-DD format
        
        // Find metrics for this day
        const dayMetrics = metricsArray.filter(m => {
          try {
            const metricDate = new Date(m.timestamp)
            metricDate.setHours(0, 0, 0, 0)
            return metricDate.getTime() === day.getTime()
          } catch (err) {
            return false
          }
        })

        // Aggregate metrics for the day
        const totalEvents = dayMetrics.reduce((sum, m) => sum + (m.total_events || 0), 0)
        const totalErrors = dayMetrics.reduce((sum, m) => sum + (m.error_count || 0), 0)
        const totalSynced = totalEvents - totalErrors

        // Format date as "Mon DD" or "Today"
        const dayStr = idx === 6 ? 'Today' : day.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' })

        return {
          time: dayStr,
          replicated: totalEvents,
          synced: totalSynced,
          errors: totalErrors,
          date: dayDate,
          dateObj: day // Keep for sorting
        }
      }).sort((a, b) => a.dateObj.getTime() - b.dateObj.getTime())
        .map(({ dateObj, ...rest }) => rest) // Remove dateObj before returning
    } else {
      // If no metrics, create chart data from events (7 days, grouped by day)
      return days.map((day, idx) => {
        const dayStart = new Date(day)
        dayStart.setHours(0, 0, 0, 0)
        const dayEnd = new Date(day)
        dayEnd.setHours(23, 59, 59, 999)

        const dayEvents = eventsArray.filter(e => {
          try {
            const eventTime = new Date(e.created_at || e.source_commit_time || Date.now())
            return eventTime >= dayStart && eventTime <= dayEnd
          } catch (err) {
            return false
          }
        })

        const replicated = dayEvents.length
        const synced = dayEvents.filter(e => e.status === 'applied' || e.status === 'success').length
        const errors = dayEvents.filter(e => e.status === 'failed' || e.status === 'error').length

        // Format date as "Mon DD" or "Today"
        const dayStr = idx === 6 ? 'Today' : day.toLocaleDateString('en-US', { weekday: 'short', day: 'numeric' })

        return { 
          time: dayStr, 
          replicated, 
          synced, 
          errors, 
          date: day.toISOString().split('T')[0],
          dateObj: day // Keep for sorting
        }
      }).sort((a, b) => a.dateObj.getTime() - b.dateObj.getTime())
        .map(({ dateObj, ...rest }) => rest) // Remove dateObj before returning
    }
  }, [metrics.length, events.length]) // Use lengths instead of full arrays
  
  // Update chart data only when memoized value changes
  useEffect(() => {
    setChartData(chartDataMemo)
  }, [chartDataMemo])

  // Get recent pipeline activity from events
  const recentActivity = useMemo(() => {
    const eventsArray = Array.isArray(events) ? events : []
    const pipelinesArray = Array.isArray(pipelines) ? pipelines : []
    
    if (eventsArray.length === 0) {
      return []
    }
    
    // Sort events by created_at (most recent first) and take the most recent ones
    const sortedEvents = [...eventsArray]
      .filter(e => e && (e.created_at || e.source_commit_time)) // Only events with dates
      .sort((a, b) => {
        try {
          const dateA = new Date(a.created_at || a.source_commit_time || 0).getTime()
          const dateB = new Date(b.created_at || b.source_commit_time || 0).getTime()
          return dateB - dateA // Most recent first
        } catch (err) {
          return 0
        }
      })
    
    if (sortedEvents.length === 0) {
      return []
    }
    
    const recentEvents = sortedEvents.slice(0, 30) // Get more events to ensure we have unique pipelines
    const activityMap = new Map()

    recentEvents.forEach(event => {
      if (!event) return
      
      // Get pipeline ID - try multiple fields
      const pipelineId = event.pipeline_id || event.pipelineId || null
      if (!pipelineId) {
        // Skip events without pipeline_id
        return
      }
      
      // Try to find pipeline by matching ID (handle both string and number)
      let pipeline = null
      let pipelineKey = String(pipelineId)
      
      if (pipelinesArray.length > 0) {
        pipeline = pipelinesArray.find(p => {
          const pId = String(p.id)
          const eId = String(pipelineId)
          // Try exact match
          if (pId === eId) return true
          // Try numeric conversion
          const pNum = Number(pId)
          const eNum = Number(eId)
          if (!isNaN(pNum) && !isNaN(eNum) && pNum === eNum) return true
          // Try UUID comparison
          return false
        })
        
        if (pipeline) {
          pipelineKey = String(pipeline.id)
        }
      }
      
      // Only add if we haven't seen this pipeline yet, or if this event is more recent
      if (!activityMap.has(pipelineKey)) {
        try {
          const eventDate = new Date(event.created_at || event.source_commit_time || Date.now())
          const isValidDate = !isNaN(eventDate.getTime())
          
          if (!isValidDate) {
            console.warn('Skipping event with invalid date:', event)
            return
          }
          
          // Determine status
          const status = event.status === 'applied' || event.status === 'success' ? 'success' :
            event.status === 'failed' || event.status === 'error' ? 'error' : 
            event.status === 'captured' || event.status === 'pending' ? 'warning' : 'warning'
          
          activityMap.set(pipelineKey, {
            pipeline: pipeline ? (pipeline.name || `Pipeline ${pipelineKey}`) : `Pipeline ${pipelineKey}`,
            status: status,
            time: formatDistanceToNow(eventDate, { addSuffix: true }),
            timestamp: eventDate.getTime(), // Store timestamp for sorting
          })
        } catch (err) {
          console.warn('Error processing event for activity:', err, event)
        }
      }
    })

    // Convert to array, sort by timestamp (most recent first), and take top 5
    const activities = Array.from(activityMap.values())
      .filter(a => a && a.timestamp) // Only valid activities
      .sort((a, b) => (b.timestamp || 0) - (a.timestamp || 0))
      .slice(0, 5)
      .map(({ timestamp, ...rest }) => rest) // Remove timestamp before returning
    
    return activities
  }, [events, pipelines])

  // Ensure pipelines is an array for metricsDisplay
  const pipelinesArrayForMetrics = Array.isArray(pipelines) ? pipelines : []

  const metricsDisplay = [
    {
      label: "Active Pipelines",
      value: dashboardMetrics.activePipelines.toString(),
      change: `${pipelinesArrayForMetrics.filter(p => p.status === 'active').length} active`,
      icon: Activity,
      gradient: "from-cyan-500/10 to-blue-600/5",
      borderColor: "border-cyan-500/20",
      iconBg: "bg-cyan-500/20",
      iconColor: "text-cyan-400",
      textGradient: "from-cyan-400 to-blue-500",
    },
    {
      label: "Total Tables",
      value: dashboardMetrics.totalTables.toString(),
      change: backendStats ? `${backendStats.total_connections || 0} connections` : `${events.length} events today`,
      icon: Database,
      gradient: "from-emerald-500/10 to-green-600/5",
      borderColor: "border-emerald-500/20",
      iconBg: "bg-emerald-500/20",
      iconColor: "text-emerald-400",
      textGradient: "from-emerald-400 to-green-500",
    },
    {
      label: "Error Rate",
      value: dashboardMetrics.errorRate.toFixed(1) + "%",
      change: `${events.filter(e => e.status === 'failed').length} errors`,
      icon: AlertCircle,
      gradient: "from-amber-500/10 to-orange-600/5",
      borderColor: "border-amber-500/20",
      iconBg: "bg-amber-500/20",
      iconColor: "text-amber-400",
      textGradient: "from-amber-400 to-orange-500",
    },
    {
      label: "Data Quality",
      value: (dashboardMetrics.dataQuality % 1 === 0 
        ? dashboardMetrics.dataQuality.toFixed(0) 
        : dashboardMetrics.dataQuality.toFixed(1)) + "%",
      change: `${events.filter(e => e.status === 'applied').length} successful`,
      icon: CheckCircle,
      gradient: "from-green-500/10 to-emerald-600/5",
      borderColor: "border-green-500/20",
      iconBg: "bg-green-500/20",
      iconColor: "text-green-400",
      textGradient: "from-green-400 to-emerald-500",
    },
  ]

  return (
    <div className="space-y-6">
      {/* Metrics Grid - Enhanced with gradients and animations */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {metricsDisplay.map((metric) => {
          const Icon = metric.icon
          return (
            <Card
              key={metric.label}
              className={`p-6 bg-gradient-to-br ${metric.gradient} ${metric.borderColor} shadow-lg hover:shadow-2xl transition-all duration-300 hover:scale-105 group`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">{metric.label}</p>
                  <p className={`text-4xl font-extrabold bg-gradient-to-r ${metric.textGradient} bg-clip-text text-transparent mb-1`}>
                    {metric.value}
                  </p>
                  <p className="text-xs font-medium text-foreground-muted/80">{metric.change}</p>
                </div>
                <div className={`p-4 ${metric.iconBg} rounded-xl group-hover:scale-110 transition-transform duration-300`}>
                  <Icon className={`w-8 h-8 ${metric.iconColor}`} />
                </div>
              </div>
            </Card>
          )
        })}
      </div>

      {/* Charts - Enhanced visibility and styling */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6 bg-surface border-border shadow-xl">
          <h3 className="text-xl font-bold text-foreground mb-6 flex items-center gap-2">
            <Activity className="w-6 h-6 text-cyan-400" />
            Replication Events (7d)
          </h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <LineChart 
                data={chartData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(100, 116, 139, 0.15)" />
                <XAxis
                  dataKey="time"
                  stroke="rgb(148, 163, 184)"
                  tick={{ fill: 'rgb(148, 163, 184)', fontSize: 12, fontWeight: '600' }}
                  label={{ value: 'Time', position: 'insideBottom', offset: -5, fill: 'rgb(148, 163, 184)', fontSize: 13, fontWeight: '600' }}
                />
                <YAxis
                  stroke="rgb(148, 163, 184)"
                  tick={{ fill: 'rgb(148, 163, 184)', fontSize: 12, fontWeight: '600' }}
                  label={{ value: 'Events', angle: -90, position: 'insideLeft', fill: 'rgb(148, 163, 184)', fontSize: 13, fontWeight: '600' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(15, 23, 42, 0.95)",
                    border: "1px solid rgb(6, 182, 212)",
                    borderRadius: "12px",
                    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.3)",
                    padding: "12px"
                  }}
                  labelStyle={{ color: 'rgb(6, 182, 212)', fontWeight: 'bold', fontSize: '14px', marginBottom: '8px' }}
                  itemStyle={{ color: 'rgb(148, 163, 184)', fontSize: '13px', padding: '4px 0' }}
                  formatter={(value: any, name: string) => [value, name]}
                />
                <Legend 
                  wrapperStyle={{ paddingTop: "20px" }}
                  iconType="line"
                />
                <Line
                  type="monotone"
                  dataKey="replicated"
                  stroke="rgb(6, 182, 212)"
                  strokeWidth={3}
                  dot={{ fill: "rgb(6, 182, 212)", r: 5, strokeWidth: 2, stroke: "rgb(8, 145, 178)" }}
                  activeDot={{ r: 7, fill: "rgb(14, 165, 233)" }}
                  name="Replicated"
                />
                <Line
                  type="monotone"
                  dataKey="synced"
                  stroke="rgb(34, 211, 238)"
                  strokeWidth={3}
                  dot={{ fill: "rgb(34, 211, 238)", r: 5, strokeWidth: 2, stroke: "rgb(6, 182, 212)" }}
                  activeDot={{ r: 7, fill: "rgb(103, 232, 249)" }}
                  name="Synced"
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[320px] flex flex-col items-center justify-center text-foreground-muted">
              <Activity className="w-16 h-16 mb-4 opacity-20" />
              <p className="text-base font-medium">No data available</p>
              <p className="text-sm mt-2">Events will appear here as they are captured</p>
            </div>
          )}
        </Card>

        <Card className="p-6 bg-surface border-border shadow-xl">
          <h3 className="text-xl font-bold text-foreground mb-6 flex items-center gap-2">
            <AlertCircle className="w-6 h-6 text-red-400" />
            Error Distribution
          </h3>
          {chartData.length > 0 ? (
            <ResponsiveContainer width="100%" height={320}>
              <BarChart 
                data={chartData}
                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
              >
                <defs>
                  <linearGradient id="errorGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="rgb(239, 68, 68)" stopOpacity={0.9} />
                    <stop offset="100%" stopColor="rgb(220, 38, 38)" stopOpacity={0.7} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(100, 116, 139, 0.15)" />
                <XAxis
                  dataKey="time"
                  stroke="rgb(148, 163, 184)"
                  tick={{ fill: 'rgb(148, 163, 184)', fontSize: 12, fontWeight: '600' }}
                  label={{ value: 'Time', position: 'insideBottom', offset: -5, fill: 'rgb(148, 163, 184)', fontSize: 13, fontWeight: '600' }}
                />
                <YAxis
                  stroke="rgb(148, 163, 184)"
                  tick={{ fill: 'rgb(148, 163, 184)', fontSize: 12, fontWeight: '600' }}
                  label={{ value: 'Errors', angle: -90, position: 'insideLeft', fill: 'rgb(148, 163, 184)', fontSize: 13, fontWeight: '600' }}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(15, 23, 42, 0.95)",
                    border: "1px solid rgb(239, 68, 68)",
                    borderRadius: "12px",
                    boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.3)",
                    padding: "12px"
                  }}
                  labelStyle={{ color: 'rgb(239, 68, 68)', fontWeight: 'bold', fontSize: '14px', marginBottom: '8px' }}
                  itemStyle={{ color: 'rgb(148, 163, 184)', fontSize: '13px', padding: '4px 0' }}
                  formatter={(value: any, name: string) => [value, name || 'Errors']}
                />
                <Bar
                  dataKey="errors"
                  fill="url(#errorGradient)"
                  radius={[10, 10, 0, 0]}
                  name="Errors"
                />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-[320px] flex flex-col items-center justify-center text-foreground-muted">
              <AlertCircle className="w-16 h-16 mb-4 opacity-20" />
              <p className="text-base font-medium">No error data available</p>
              <p className="text-sm mt-2">Errors will appear here when they occur</p>
            </div>
          )}
        </Card>
      </div>

      {/* Recent Activity - Enhanced */}
      <Card className="p-6 bg-surface border-border shadow-xl">
        <h3 className="text-xl font-bold text-foreground mb-6 flex items-center gap-2">
          <Database className="w-6 h-6 text-emerald-400" />
          Recent Pipeline Activity
        </h3>
        {isLoading && events.length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
            <span className="ml-3 text-foreground-muted font-medium">Loading activity...</span>
          </div>
        ) : recentActivity.length > 0 ? (
          <div className="space-y-3">
            {recentActivity.map((activity, idx) => (
              <div
                key={idx}
                className="flex items-center justify-between py-3 px-4 rounded-lg border border-border/50 hover:bg-surface-hover/30 hover:border-border transition-all duration-200 group"
              >
                <div className="flex items-center gap-4">
                  <div
                    className={`w-3 h-3 rounded-full shadow-lg ${activity.status === "success" ? "bg-green-400 shadow-green-400/50" :
                        activity.status === "error" ? "bg-red-400 shadow-red-400/50" :
                          "bg-amber-400 shadow-amber-400/50"
                      } group-hover:scale-125 transition-transform duration-200`}
                  />
                  <span className="font-semibold text-foreground text-base">{activity.pipeline}</span>
                </div>
                <span className="text-sm font-medium text-foreground-muted">{activity.time}</span>
              </div>
            ))}
          </div>
        ) : events.length > 0 ? (
          <div className="text-center py-12 text-foreground-muted">
            <Database className="w-16 h-16 mx-auto mb-4 opacity-20" />
            <p className="text-base font-medium">No pipeline activity found</p>
            <p className="text-sm mt-2">
              Found {events.length} event{events.length !== 1 ? 's' : ''} but unable to match with pipelines.
            </p>
            <p className="text-xs mt-2 text-foreground-muted/70">
              Make sure events have valid pipeline_id and created_at fields.
            </p>
          </div>
        ) : (
          <div className="text-center py-12 text-foreground-muted">
            <Database className="w-16 h-16 mx-auto mb-4 opacity-20" />
            <p className="text-base font-medium">No recent activity</p>
            <p className="text-sm mt-2">Events will appear here as pipelines process data.</p>
            <p className="text-xs mt-2 text-foreground-muted/70">
              Make sure pipelines are running and generating events.
            </p>
          </div>
        )}
      </Card>

      {/* Application Logs Section */}
      <ApplicationLogs />
    </div>
  )
}
