"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { PageHeader } from "@/components/ui/page-header"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import { Calendar, ArrowLeft, Save, Loader2, Clock, Repeat } from "lucide-react"
import { useAppDispatch } from "@/lib/store/hooks"
import { useErrorToast } from "@/components/ui/error-toast"

export default function CreateSchedulePage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { showError, ErrorToastComponent } = useErrorToast()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    schedule_type: "time_based", // 'time_based', 'event_based'
    pipeline_id: "",
    cron_expression: "0 0 * * *", // Default: daily at midnight
    timezone: "UTC",
    enabled: true,
    retry_config: {
      max_retries: 3,
      retry_delay_seconds: 300,
    },
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      // TODO: Integrate with actual schedule creation API
      await new Promise(resolve => setTimeout(resolve, 1000))
      showError("Schedule created successfully!", "Success", "success")
      router.push("/etl/scheduler")
    } catch (error: any) {
      const errorMessage = error?.payload || error?.message || "Failed to create schedule"
      showError(errorMessage, "Creation Failed")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <ProtectedPage path="/etl/scheduler/create">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <PageHeader
            title="Create Schedule"
            subtitle="Schedule ETL pipeline executions"
            icon={Calendar}
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
              <Label htmlFor="name">Schedule Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Daily Data Sync"
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
                placeholder="Describe when and why this schedule runs..."
                rows={3}
                className="bg-background border-border"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <Label htmlFor="schedule_type">Schedule Type *</Label>
                <select
                  id="schedule_type"
                  value={formData.schedule_type}
                  onChange={(e) => setFormData({ ...formData, schedule_type: e.target.value })}
                  className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground"
                  required
                >
                  <option value="time_based">Time-Based (Cron)</option>
                  <option value="event_based">Event-Based</option>
                </select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="pipeline_id">ETL Pipeline *</Label>
                <Input
                  id="pipeline_id"
                  value={formData.pipeline_id}
                  onChange={(e) => setFormData({ ...formData, pipeline_id: e.target.value })}
                  placeholder="Pipeline ID or select from list"
                  required
                  className="bg-background border-border"
                />
                <p className="text-xs text-foreground-muted">Select the ETL pipeline to schedule</p>
              </div>
            </div>

            {formData.schedule_type === "time_based" && (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <Label htmlFor="cron_expression">Cron Expression *</Label>
                    <div className="flex items-center gap-2">
                      <Input
                        id="cron_expression"
                        value={formData.cron_expression}
                        onChange={(e) => setFormData({ ...formData, cron_expression: e.target.value })}
                        placeholder="0 0 * * *"
                        required
                        className="bg-background border-border font-mono"
                      />
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => setFormData({ ...formData, cron_expression: "0 0 * * *" })}
                        className="border-border text-foreground-muted hover:text-foreground"
                        title="Daily at midnight"
                      >
                        <Repeat className="w-4 h-4" />
                      </Button>
                    </div>
                    <p className="text-xs text-foreground-muted">
                      Format: minute hour day month day-of-week (e.g., "0 0 * * *" = daily at midnight)
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="timezone">Timezone *</Label>
                    <select
                      id="timezone"
                      value={formData.timezone}
                      onChange={(e) => setFormData({ ...formData, timezone: e.target.value })}
                      className="w-full px-3 py-2 bg-background border border-border rounded-md text-foreground"
                      required
                    >
                      <option value="UTC">UTC</option>
                      <option value="America/New_York">Eastern Time (ET)</option>
                      <option value="America/Chicago">Central Time (CT)</option>
                      <option value="America/Denver">Mountain Time (MT)</option>
                      <option value="America/Los_Angeles">Pacific Time (PT)</option>
                      <option value="Europe/London">London (GMT)</option>
                      <option value="Europe/Paris">Paris (CET)</option>
                      <option value="Asia/Tokyo">Tokyo (JST)</option>
                      <option value="Asia/Shanghai">Shanghai (CST)</option>
                    </select>
                  </div>
                </div>

                <div className="p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Clock className="w-5 h-5 text-blue-400 mt-0.5" />
                    <div className="flex-1">
                      <h4 className="text-sm font-semibold text-foreground mb-1">Cron Expression Examples</h4>
                      <ul className="text-xs text-foreground-muted space-y-1 font-mono">
                        <li><code className="bg-background px-1 py-0.5 rounded">0 0 * * *</code> - Daily at midnight</li>
                        <li><code className="bg-background px-1 py-0.5 rounded">0 */6 * * *</code> - Every 6 hours</li>
                        <li><code className="bg-background px-1 py-0.5 rounded">0 9 * * 1-5</code> - Weekdays at 9 AM</li>
                        <li><code className="bg-background px-1 py-0.5 rounded">0 0 1 * *</code> - First day of month at midnight</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </>
            )}

            {formData.schedule_type === "event_based" && (
              <div className="p-4 bg-purple-500/10 border border-purple-500/20 rounded-lg">
                <div className="flex items-start gap-3">
                  <Calendar className="w-5 h-5 text-purple-400 mt-0.5" />
                  <div className="flex-1">
                    <h4 className="text-sm font-semibold text-foreground mb-1">Event-Based Scheduling</h4>
                    <p className="text-xs text-foreground-muted">
                      Configure event triggers that will activate this schedule. This feature is coming soon.
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div className="border-t border-border pt-6">
              <h3 className="text-lg font-semibold text-foreground mb-4">Retry Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <Label htmlFor="max_retries">Max Retries</Label>
                  <Input
                    id="max_retries"
                    type="number"
                    min="0"
                    max="10"
                    value={formData.retry_config.max_retries}
                    onChange={(e) => setFormData({
                      ...formData,
                      retry_config: { ...formData.retry_config, max_retries: parseInt(e.target.value) || 0 }
                    })}
                    className="bg-background border-border"
                  />
                  <p className="text-xs text-foreground-muted">Number of retry attempts on failure</p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="retry_delay">Retry Delay (seconds)</Label>
                  <Input
                    id="retry_delay"
                    type="number"
                    min="0"
                    value={formData.retry_config.retry_delay_seconds}
                    onChange={(e) => setFormData({
                      ...formData,
                      retry_config: { ...formData.retry_config, retry_delay_seconds: parseInt(e.target.value) || 0 }
                    })}
                    className="bg-background border-border"
                  />
                  <p className="text-xs text-foreground-muted">Delay between retry attempts</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="enabled"
                checked={formData.enabled}
                onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                className="w-4 h-4 rounded border-border"
              />
              <Label htmlFor="enabled" className="cursor-pointer">
                Enable schedule immediately after creation
              </Label>
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
                disabled={isSubmitting || !formData.name || !formData.pipeline_id}
                className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Create Schedule
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

