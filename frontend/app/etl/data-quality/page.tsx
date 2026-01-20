"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { PageHeader } from "@/components/ui/page-header"
import {
  Shield,
  CheckCircle,
  AlertCircle,
  TrendingUp,
  Database,
  RefreshCw,
  Download,
  Settings,
  X,
} from "lucide-react"
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"

export default function DataQualityPage() {
  const [selectedAsset, setSelectedAsset] = useState<string | null>("fact_sales")
  const [healthData, setHealthData] = useState<any>({
    overallScore: 94,
    totalRows: 1280000,
    anomalies: 42,
    accuracy: 98,
    completeness: 92,
    consistency: 100,
    timeliness: 88,
    lastScanned: "2024-01-19T14:32:00Z",
    validationRules: [
      {
        name: "Check for Null IDs",
        category: "Completeness",
        columns: "order_id, customer_id",
        lastRun: "2024-01-19T14:32:00Z",
        status: "passed",
      },
      {
        name: "Value Range Validation",
        category: "Accuracy",
        columns: "sale_amount (0 - 50k)",
        lastRun: "2024-01-19T14:32:00Z",
        status: "failed",
      },
      {
        name: "Unique Constraint",
        category: "Consistency",
        columns: "transaction_hash",
        lastRun: "2024-01-19T14:31:00Z",
        status: "passed",
      },
      {
        name: "Timestamp Freshness",
        category: "Timeliness",
        columns: "created_at (< 15m lag)",
        lastRun: "2024-01-19T14:30:00Z",
        status: "warning",
      },
    ],
    distribution: {
      column: "price_usd",
      bins: [
        { range: "0-100", count: 450000, outliers: false },
        { range: "100-500", count: 620000, outliers: false },
        { range: "500-1000", count: 180000, outliers: false },
        { range: "1000+", count: 30000, outliers: true },
      ],
      outlierCount: 54,
    },
  })

  const distributionData = healthData.distribution.bins.map((bin: any) => ({
    range: bin.range,
    count: bin.count,
    fill: bin.outliers ? "#ef4444" : "#22c55e",
  }))

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "passed":
        return <CheckCircle className="w-4 h-4 text-green-400" />
      case "failed":
        return <X className="w-4 h-4 text-red-400" />
      case "warning":
        return <AlertCircle className="w-4 h-4 text-yellow-400" />
      default:
        return null
    }
  }

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "passed":
        return <Badge className="bg-green-500/20 text-green-400 border-green-500/30">PASSED</Badge>
      case "failed":
        return <Badge className="bg-red-500/20 text-red-400 border-red-500/30">FAILED</Badge>
      case "warning":
        return <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">WARNING</Badge>
      default:
        return null
    }
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <PageHeader
          title="Data Quality"
          subtitle="Monitor and validate data quality across your assets"
          icon={Shield}
        />
        <div className="flex items-center gap-3">
          <Button variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh Report
          </Button>
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export PDF
          </Button>
          <Button variant="outline">
            <Settings className="w-4 h-4 mr-2" />
            Configure Rules
          </Button>
        </div>
      </div>

      {/* Asset Selector */}
      <Card className="p-4">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-foreground-muted">Asset:</span>
          <select
            value={selectedAsset || ""}
            onChange={(e) => setSelectedAsset(e.target.value)}
            className="bg-surface border border-border rounded-lg px-4 py-2 text-foreground"
          >
            <option value="fact_sales">fact_sales</option>
            <option value="dim_customers">dim_customers</option>
            <option value="fact_orders">fact_orders</option>
          </select>
          <span className="text-sm text-foreground-muted">
            Last scanned: {new Date(healthData.lastScanned).toLocaleString()}
          </span>
        </div>
      </Card>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="p-6 bg-gradient-to-br from-green-500/10 to-emerald-500/5 border-green-500/20">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">
                Overall Quality Score
              </p>
              <p className="text-5xl font-extrabold bg-gradient-to-r from-green-400 to-emerald-500 bg-clip-text text-transparent mb-2">
                {healthData.overallScore}%
              </p>
              <p className="text-xs font-medium text-green-400 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                +2.1% vs last week
              </p>
            </div>
            <Shield className="w-12 h-12 text-green-400/50" />
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-cyan-500/10 to-blue-500/5 border-cyan-500/20">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">
                Total Rows Scanned
              </p>
              <p className="text-5xl font-extrabold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent mb-2">
                {(healthData.totalRows / 1000000).toFixed(2)}M
              </p>
              <p className="text-xs font-medium text-cyan-400 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                Stable growth trend
              </p>
            </div>
            <Database className="w-12 h-12 text-cyan-400/50" />
          </div>
        </Card>

        <Card className="p-6 bg-gradient-to-br from-red-500/10 to-orange-500/5 border-red-500/20">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <p className="text-sm font-semibold text-foreground-muted uppercase tracking-wide mb-2">
                Anomalies Detected
              </p>
              <p className="text-5xl font-extrabold bg-gradient-to-r from-red-400 to-orange-500 bg-clip-text text-transparent mb-2">
                {healthData.anomalies}
              </p>
              <p className="text-xs font-medium text-red-400 flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                +12% needs attention
              </p>
            </div>
            <AlertCircle className="w-12 h-12 text-red-400/50" />
          </div>
        </Card>
      </div>

      {/* Health Dimensions */}
      <Card className="p-6">
        <h3 className="text-xl font-bold text-foreground mb-6">Health Dimensions</h3>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-foreground">Accuracy</span>
              <span className="text-sm font-bold text-green-400">{healthData.accuracy}%</span>
            </div>
            <Progress value={healthData.accuracy} className="h-2" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-foreground">Completeness</span>
              <span className="text-sm font-bold text-green-400">{healthData.completeness}%</span>
            </div>
            <Progress value={healthData.completeness} className="h-2" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-foreground">Consistency</span>
              <span className="text-sm font-bold text-green-400">{healthData.consistency}%</span>
            </div>
            <Progress value={healthData.consistency} className="h-2" />
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-foreground">Timeliness</span>
              <span className="text-sm font-bold text-yellow-400">{healthData.timeliness}%</span>
            </div>
            <Progress value={healthData.timeliness} className="h-2" />
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribution */}
        <Card className="p-6">
          <h3 className="text-xl font-bold text-foreground mb-6">Distribution</h3>
          <div className="mb-4">
            <span className="text-sm text-foreground-muted">Column: {healthData.distribution.column}</span>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart 
              data={distributionData}
              margin={{ top: 5, right: 20, left: 70, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(100, 116, 139, 0.15)" />
              <XAxis 
                dataKey="range" 
                stroke="rgb(148, 163, 184)"
                tick={{ fill: 'rgb(148, 163, 184)', fontSize: 12 }}
              />
              <YAxis 
                stroke="rgb(148, 163, 184)"
                tick={{ fill: 'rgb(148, 163, 184)', fontSize: 12 }}
                width={65}
                domain={[0, 'dataMax']}
                tickFormatter={(value) => {
                  // Format large numbers with K/M suffix but keep smaller ones full
                  if (value >= 1000000) {
                    return `${(value / 1000000).toFixed(1)}M`
                  } else if (value >= 1000) {
                    return `${(value / 1000).toFixed(0)}K`
                  }
                  return value.toLocaleString()
                }}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "rgba(15, 23, 42, 0.95)",
                  border: "1px solid rgb(168, 85, 247)",
                  borderRadius: "8px",
                  color: "rgb(226, 232, 240)",
                }}
                formatter={(value: number) => [value.toLocaleString(), 'Count']}
                labelFormatter={(label) => `Range: ${label}`}
              />
              <Bar dataKey="count" fill="#8884d8" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
          {healthData.distribution.outlierCount > 0 && (
            <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
              <p className="text-sm text-red-400">
                {healthData.distribution.outlierCount} values identified as statistical outliers (&gt; 3σ from mean).
              </p>
            </div>
          )}
        </Card>

        {/* Validation Rules */}
        <Card className="p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-foreground">Validation Rules</h3>
            <div className="flex items-center gap-2">
              <Badge className="bg-green-500/20 text-green-400 border-green-500/30">
                {healthData.validationRules.filter((r: any) => r.status === "passed").length} Passed
              </Badge>
              <Badge className="bg-red-500/20 text-red-400 border-red-500/30">
                {healthData.validationRules.filter((r: any) => r.status === "failed").length} Failed
              </Badge>
            </div>
          </div>
          <div className="space-y-3 max-h-[400px] overflow-y-auto">
            {healthData.validationRules.map((rule: any, index: number) => (
              <div
                key={index}
                className="p-4 bg-surface rounded-lg border border-border hover:border-purple-500/30 transition-colors"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {getStatusIcon(rule.status)}
                    <span className="font-medium text-foreground">{rule.name}</span>
                  </div>
                  {getStatusBadge(rule.status)}
                </div>
                <div className="text-sm text-foreground-muted mb-2">
                  (col: {rule.columns})
                </div>
                <div className="flex items-center justify-between text-xs text-foreground-muted">
                  <span>Category: {rule.category}</span>
                  <span>Last Run: {new Date(rule.lastRun).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
          <Button variant="outline" className="w-full mt-4">
            View All 48 Validation Rules
          </Button>
        </Card>
      </div>
    </div>
  )
}

