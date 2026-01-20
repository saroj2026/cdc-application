"use client"

import { useState, useEffect, useMemo } from "react"
import { PageHeader } from "@/components/ui/page-header"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import {
  GitGraph,
  Database,
  GitBranch,
  Code2,
  Sparkles,
  ArrowRight,
  Search,
  ZoomIn,
  ZoomOut,
  Maximize2,
  Filter,
  Layers,
  Network,
  Eye,
  RefreshCw,
  Loader2,
} from "lucide-react"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { fetchETLPipelines, fetchETLRuns } from "@/lib/store/slices/etlSlice"
import { motion, AnimatePresence } from "framer-motion"
import { cn } from "@/lib/utils"

interface LineageNode {
  id: string
  type: "source" | "transformation" | "target"
  name: string
  label: string
  icon: any
  x: number
  y: number
  color: string
  gradient: string
  fields?: string[]
  status?: string
}

interface LineageEdge {
  from: string
  to: string
  animated?: boolean
  color?: string
}

export default function DataLineagePage() {
  const dispatch = useAppDispatch()
  const { pipelines: etlPipelines, runs, isLoading } = useAppSelector((state) => state.etl)
  const [selectedPipeline, setSelectedPipeline] = useState<string>("all")
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [showFieldLevel, setShowFieldLevel] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")

  useEffect(() => {
    dispatch(fetchETLPipelines())
    dispatch(fetchETLRuns())
  }, [dispatch])

  // Generate lineage nodes and edges
  const { nodes, edges } = useMemo(() => {
    const pipeline = selectedPipeline === "all"
      ? etlPipelines[0]
      : etlPipelines.find(p => p.id === selectedPipeline)

    if (!pipeline) {
      return { nodes: [], edges: [] }
    }

    const nodeList: LineageNode[] = []
    const edgeList: LineageEdge[] = []

    // Source node
    const sourceNode: LineageNode = {
      id: `source-${pipeline.id}`,
      type: "source",
      name: pipeline.source_type || "Source",
      label: `${pipeline.source_type} Source`,
      icon: Database,
      x: 100,
      y: 300,
      color: "from-cyan-500 to-blue-500",
      gradient: "from-cyan-500/20 to-blue-500/20",
      fields: pipeline.source_config?.columns || ["id", "name", "created_at"],
      status: "active",
    }
    nodeList.push(sourceNode)

    // Transformation nodes (if any)
    if (pipeline.transformation_ids && pipeline.transformation_ids.length > 0) {
      pipeline.transformation_ids.forEach((transId, index) => {
        const transformNode: LineageNode = {
          id: `transform-${transId}`,
          type: "transformation",
          name: `Transformation ${index + 1}`,
          label: `ETL Transform ${index + 1}`,
          icon: Code2,
          x: 400 + (index * 300),
          y: 300,
          color: "from-purple-500 to-pink-500",
          gradient: "from-purple-500/20 to-pink-500/20",
          fields: ["id", "name", "status", "processed_at"],
          status: "active",
        }
        nodeList.push(transformNode)

        // Edge from previous node
        const previousNodeId = index === 0
          ? sourceNode.id
          : `transform-${pipeline.transformation_ids[index - 1]}`
        edgeList.push({
          from: previousNodeId,
          to: transformNode.id,
          animated: true,
          color: "stroke-purple-400",
        })
      })
    } else {
      // If no transformations, connect source directly to target
      edgeList.push({
        from: sourceNode.id,
        to: `target-${pipeline.id}`,
        animated: true,
        color: "stroke-cyan-400",
      })
    }

    // Target node
    const lastTransformIndex = pipeline.transformation_ids?.length || 0
    const targetNode: LineageNode = {
      id: `target-${pipeline.id}`,
      type: "target",
      name: pipeline.target_type || "Target",
      label: `${pipeline.target_type} Target`,
      icon: Database,
      x: 700 + (lastTransformIndex * 300),
      y: 300,
      color: "from-emerald-500 to-green-500",
      gradient: "from-emerald-500/20 to-green-500/20",
      fields: pipeline.target_config?.columns || ["id", "name", "created_at", "updated_at"],
      status: "active",
    }
    nodeList.push(targetNode)

    // Edge from last transformation to target
    if (pipeline.transformation_ids && pipeline.transformation_ids.length > 0) {
      const lastTransformId = `transform-${pipeline.transformation_ids[pipeline.transformation_ids.length - 1]}`
      edgeList.push({
        from: lastTransformId,
        to: targetNode.id,
        animated: true,
        color: "stroke-emerald-400",
      })
    }

    return { nodes: nodeList, edges: edgeList }
  }, [etlPipelines, selectedPipeline])

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.1, 2))
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.1, 0.5))
  const handleReset = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  return (
    <ProtectedPage path="/etl/lineage">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <PageHeader
            title="Data Lineage"
            subtitle="Visualize how data flows through your ETL pipelines"
            icon={GitGraph}
          />
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomOut}
              className="border-border text-foreground-muted hover:text-foreground"
            >
              <ZoomOut className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleReset}
              className="border-border text-foreground-muted hover:text-foreground"
            >
              <Maximize2 className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={handleZoomIn}
              className="border-border text-foreground-muted hover:text-foreground"
            >
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowFieldLevel(!showFieldLevel)}
              className={cn(
                "border-border text-foreground-muted hover:text-foreground",
                showFieldLevel && "bg-purple-500/10 border-purple-500/30 text-purple-400"
              )}
            >
              <Layers className="w-4 h-4 mr-2" />
              Fields
            </Button>
          </div>
        </div>

        {/* Filters */}
        <Card className="p-4 bg-surface border-border">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-foreground-muted" />
              <Input
                placeholder="Search pipelines..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 bg-background border-border"
              />
            </div>
            <select
              value={selectedPipeline}
              onChange={(e) => setSelectedPipeline(e.target.value)}
              className="px-3 py-2 bg-background border border-border rounded-md text-foreground text-sm min-w-[250px]"
            >
              <option value="all">All Pipelines</option>
              {etlPipelines
                .filter(p => !searchQuery || p.name.toLowerCase().includes(searchQuery.toLowerCase()))
                .map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
            </select>
          </div>
        </Card>

        {/* Lineage Visualization */}
        <Card className="p-6 bg-surface border-border shadow-lg overflow-hidden relative">
          {isLoading && nodes.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[600px]">
              <Loader2 className="w-8 h-8 animate-spin text-purple-400 mb-4" />
              <p className="text-foreground-muted">Loading lineage data...</p>
            </div>
          ) : nodes.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-[600px]">
              <GitGraph className="w-16 h-16 text-purple-400/50 mb-4" />
              <h3 className="text-xl font-bold text-foreground mb-2">No Lineage Data</h3>
              <p className="text-foreground-muted">Select a pipeline to view its data lineage</p>
            </div>
          ) : (
            <div
              className="relative w-full h-[600px] overflow-auto bg-gradient-to-br from-background via-background to-purple-950/10"
              style={{
                backgroundImage: `radial-gradient(circle at 2px 2px, rgba(139, 92, 246, 0.15) 1px, transparent 0)`,
                backgroundSize: "40px 40px",
              }}
            >
              <svg
                width="100%"
                height="100%"
                className="absolute inset-0"
                style={{
                  transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                  transformOrigin: "0 0",
                  transition: isDragging ? "none" : "transform 0.3s ease",
                }}
              >
                <defs>
                  {/* Gradient definitions */}
                  <linearGradient id="sourceGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#06b6d4" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#3b82f6" stopOpacity="0.3" />
                  </linearGradient>
                  <linearGradient id="transformGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#a855f7" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#ec4899" stopOpacity="0.3" />
                  </linearGradient>
                  <linearGradient id="targetGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor="#10b981" stopOpacity="0.3" />
                    <stop offset="100%" stopColor="#22c55e" stopOpacity="0.3" />
                  </linearGradient>
                  
                  {/* Animated marker for arrows */}
                  <marker
                    id="arrowhead"
                    markerWidth="10"
                    markerHeight="10"
                    refX="9"
                    refY="3"
                    orient="auto"
                  >
                    <polygon
                      points="0 0, 10 3, 0 6"
                      fill="rgb(168, 85, 247)"
                      className="animate-pulse"
                    />
                  </marker>

                  {/* Glow effect */}
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="3" result="coloredBlur" />
                    <feMerge>
                      <feMergeNode in="coloredBlur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>

                {/* Draw edges first (so they appear behind nodes) */}
                {edges.map((edge, index) => {
                  const fromNode = nodes.find(n => n.id === edge.from)
                  const toNode = nodes.find(n => n.id === edge.to)
                  if (!fromNode || !toNode) return null

                  const dx = toNode.x - fromNode.x
                  const dy = toNode.y - fromNode.y
                  const startX = fromNode.x + 80 // Node width offset
                  const startY = fromNode.y + 60 // Node height offset
                  const endX = toNode.x
                  const endY = toNode.y + 60

                  return (
                    <g key={`edge-${edge.from}-${edge.to}`}>
                      {/* Glow line */}
                      <line
                        x1={startX}
                        y1={startY}
                        x2={endX}
                        y2={endY}
                        stroke="url(#transformGradient)"
                        strokeWidth="4"
                        opacity="0.3"
                        filter="url(#glow)"
                      />
                      {/* Main line */}
                      <motion.line
                        x1={startX}
                        y1={startY}
                        x2={endX}
                        y2={endY}
                        stroke="rgb(168, 85, 247)"
                        strokeWidth="2"
                        markerEnd="url(#arrowhead)"
                        initial={{ pathLength: 0, opacity: 0 }}
                        animate={{ pathLength: 1, opacity: 1 }}
                        transition={{
                          duration: 2,
                          delay: index * 0.3,
                          ease: "easeInOut",
                        }}
                      />
                      {/* Animated flow particles */}
                      {edge.animated && (
                        <motion.circle
                          r="4"
                          fill="rgb(168, 85, 247)"
                          initial={{ cx: startX, cy: startY }}
                          animate={{
                            cx: [startX, endX],
                            cy: [startY, endY],
                          }}
                          transition={{
                            duration: 3,
                            repeat: Infinity,
                            ease: "linear",
                            delay: index * 0.5,
                          }}
                          filter="url(#glow)"
                        />
                      )}
                    </g>
                  )
                })}

                {/* Draw nodes */}
                {nodes.map((node, index) => {
                  const Icon = node.icon
                  const isSelected = selectedNode === node.id

                  return (
                    <g key={node.id}>
                      {/* Node shadow/glow */}
                      <motion.circle
                        cx={node.x + 80}
                        cy={node.y + 60}
                        r="85"
                        fill={`url(${node.type === 'source' ? '#sourceGradient' : node.type === 'transformation' ? '#transformGradient' : '#targetGradient'})`}
                        opacity="0.2"
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{ scale: 1, opacity: 0.2 }}
                        transition={{ duration: 0.5, delay: index * 0.2 }}
                        filter="url(#glow)"
                      />
                      {/* Node container */}
                      <motion.foreignObject
                        x={node.x}
                        y={node.y}
                        width="160"
                        height="120"
                        initial={{ scale: 0, opacity: 0 }}
                        animate={{
                          scale: isSelected ? 1.05 : 1,
                          opacity: 1,
                        }}
                        transition={{ duration: 0.5, delay: index * 0.2 }}
                      >
                        <div
                          className={cn(
                            "relative w-full h-full cursor-pointer group",
                            isSelected && "z-10"
                          )}
                          onClick={() => setSelectedNode(isSelected ? null : node.id)}
                        >
                          <motion.div
                            className={cn(
                              "w-full h-full rounded-xl border-2 p-4 backdrop-blur-sm",
                              "bg-gradient-to-br",
                              node.gradient,
                              "border-border shadow-lg",
                              isSelected && "border-purple-500 shadow-purple-500/50 shadow-2xl ring-2 ring-purple-500/30",
                              "hover:shadow-2xl transition-all duration-300"
                            )}
                            whileHover={{ y: -5 }}
                            animate={{
                              boxShadow: isSelected
                                ? "0 20px 25px -5px rgba(168, 85, 247, 0.3), 0 10px 10px -5px rgba(168, 85, 247, 0.2)"
                                : "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
                            }}
                          >
                            {/* Node icon */}
                            <div className={cn(
                              "w-12 h-12 rounded-lg flex items-center justify-center mb-3",
                              `bg-gradient-to-br ${node.color} shadow-lg`
                            )}>
                              <Icon className="w-6 h-6 text-white" />
                            </div>
                            
                            {/* Node label */}
                            <h4 className="text-sm font-bold text-foreground mb-1 line-clamp-1">
                              {node.label}
                            </h4>
                            <p className="text-xs text-foreground-muted line-clamp-1">
                              {node.name}
                            </p>

                            {/* Status badge */}
                            {node.status && (
                              <Badge
                                className={cn(
                                  "absolute top-2 right-2 text-xs",
                                  node.status === "active"
                                    ? "bg-green-500/20 text-green-400 border-green-500/30"
                                    : "bg-gray-500/20 text-gray-400 border-gray-500/30"
                                )}
                              >
                                {node.status}
                              </Badge>
                            )}

                            {/* Pulse animation for active nodes */}
                            {node.status === "active" && (
                              <motion.div
                                className="absolute inset-0 rounded-xl border-2 border-purple-400"
                                animate={{
                                  opacity: [0.5, 1, 0.5],
                                  scale: [1, 1.05, 1],
                                }}
                                transition={{
                                  duration: 2,
                                  repeat: Infinity,
                                  ease: "easeInOut",
                                }}
                              />
                            )}
                          </motion.div>
                        </div>
                      </motion.foreignObject>

                      {/* Field labels (if field level view is enabled) */}
                      {showFieldLevel && node.fields && (
                        <g>
                          {node.fields.slice(0, 5).map((field, fieldIndex) => (
                            <motion.text
                              key={field}
                              x={node.x + 80}
                              y={node.y + 140 + (fieldIndex * 20)}
                              textAnchor="middle"
                              className="text-xs fill-foreground-muted font-mono"
                              initial={{ opacity: 0, y: node.y + 130 }}
                              animate={{ opacity: 1, y: node.y + 140 + (fieldIndex * 20) }}
                              transition={{ delay: index * 0.2 + fieldIndex * 0.1 }}
                            >
                              {field}
                            </motion.text>
                          ))}
                        </g>
                      )}
                    </g>
                  )
                })}
              </svg>
            </div>
          )}

          {/* Node Details Panel */}
          <AnimatePresence>
            {selectedNode && (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                className="absolute bottom-6 left-6 right-6 z-50"
              >
                <Card className="p-6 bg-surface/95 backdrop-blur-lg border-border shadow-2xl">
                  {(() => {
                    const node = nodes.find(n => n.id === selectedNode)
                    if (!node) return null

                    return (
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className={cn(
                              "w-10 h-10 rounded-lg flex items-center justify-center",
                              `bg-gradient-to-br ${node.color} shadow-lg`
                            )}>
                              <node.icon className="w-5 h-5 text-white" />
                            </div>
                            <div>
                              <h4 className="text-lg font-bold text-foreground">{node.label}</h4>
                              <p className="text-sm text-foreground-muted">{node.name}</p>
                            </div>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => setSelectedNode(null)}
                            className="text-foreground-muted hover:text-foreground"
                          >
                            ✕
                          </Button>
                        </div>

                        {node.fields && node.fields.length > 0 && (
                          <div>
                            <h5 className="text-sm font-semibold text-foreground-muted mb-2 uppercase">
                              Fields ({node.fields.length})
                            </h5>
                            <div className="flex flex-wrap gap-2">
                              {node.fields.map((field) => (
                                <Badge
                                  key={field}
                                  variant="outline"
                                  className="text-xs font-mono bg-background/50"
                                >
                                  {field}
                                </Badge>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="flex items-center gap-2">
                          <Badge
                            className={cn(
                              "capitalize",
                              node.status === "active"
                                ? "bg-green-500/20 text-green-400 border-green-500/30"
                                : "bg-gray-500/20 text-gray-400 border-gray-500/30"
                            )}
                          >
                            {node.status || "Unknown"}
                          </Badge>
                          <Badge variant="outline" className="text-xs">
                            {node.type}
                          </Badge>
                        </div>
                      </div>
                    )
                  })()}
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </Card>

        {/* Legend */}
        <Card className="p-4 bg-surface border-border">
          <div className="flex flex-wrap items-center gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-gradient-to-br from-cyan-500 to-blue-500" />
              <span className="text-foreground-muted">Source</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-gradient-to-br from-purple-500 to-pink-500" />
              <span className="text-foreground-muted">Transformation</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-4 h-4 rounded bg-gradient-to-br from-emerald-500 to-green-500" />
              <span className="text-foreground-muted">Target</span>
            </div>
            <div className="flex items-center gap-2">
              <motion.div
                className="w-8 h-0.5 bg-purple-400"
                animate={{
                  backgroundPosition: ["0% 50%", "100% 50%"],
                }}
                transition={{
                  duration: 2,
                  repeat: Infinity,
                  ease: "linear",
                }}
              />
              <span className="text-foreground-muted">Data Flow</span>
            </div>
          </div>
        </Card>
      </div>
    </ProtectedPage>
  )
}
