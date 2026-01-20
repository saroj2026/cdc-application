"use client"

import { PageHeader } from "@/components/ui/page-header"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Plus, Clock } from "lucide-react"
import { useRouter } from "next/navigation"

export default function SchedulerPage() {
  const router = useRouter()
  
  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <PageHeader
          title="Scheduler"
          subtitle="Schedule ETL pipelines with time-based or event-based triggers"
          icon={Clock}
        />
        <Button onClick={() => router.push("/etl/scheduler/create")}>
          <Plus className="w-4 h-4 mr-2" />
          New Schedule
        </Button>
      </div>

      <Card className="p-12 text-center">
        <Clock className="w-16 h-16 mx-auto mb-4 text-purple-400/50" />
        <h3 className="text-xl font-bold text-foreground mb-2">Pipeline Scheduler</h3>
        <p className="text-foreground-muted mb-6">Schedule your ETL pipelines to run automatically</p>
        <Button onClick={() => router.push("/etl/scheduler/create")}>
          <Plus className="w-4 h-4 mr-2" />
          Create Schedule
        </Button>
      </Card>
    </div>
  )
}

