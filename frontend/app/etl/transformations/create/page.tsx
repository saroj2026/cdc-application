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
import { Code2, ArrowLeft, Save, Loader2 } from "lucide-react"
import { useAppDispatch } from "@/lib/store/hooks"
import { createETLTransformation } from "@/lib/store/slices/etlSlice"
import { useErrorToast } from "@/components/ui/error-toast"

export default function CreateTransformationPage() {
  const router = useRouter()
  const dispatch = useAppDispatch()
  const { showError, ErrorToastComponent } = useErrorToast()
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    sql_query: "-- Write your SQL transformation here\nSELECT * FROM input_table WHERE status = 'active';",
    is_reusable: true,
    tags: [] as string[],
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)

    try {
      await dispatch(createETLTransformation(formData)).unwrap()
      showError("Transformation created successfully!", "Success", "success")
      router.push("/etl/transformations")
    } catch (error: any) {
      const errorMessage = error?.payload || error?.message || "Failed to create transformation"
      showError(errorMessage, "Creation Failed")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <ProtectedPage path="/etl/transformations/create">
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <PageHeader
            title="Create Transformation"
            subtitle="Define a reusable SQL transformation"
            icon={Code2}
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
              <Label htmlFor="name">Transformation Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Filter Active Records"
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
                placeholder="Describe what this transformation does..."
                rows={3}
                className="bg-background border-border"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="sql_query">SQL Query *</Label>
              <Textarea
                id="sql_query"
                value={formData.sql_query}
                onChange={(e) => setFormData({ ...formData, sql_query: e.target.value })}
                placeholder="SELECT * FROM input_table WHERE condition = 'value';"
                rows={15}
                className="font-mono text-sm bg-background border-border"
                required
              />
              <p className="text-xs text-foreground-muted">
                Write your SQL transformation query. Use 'input_table' as the placeholder for the input data.
              </p>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="is_reusable"
                checked={formData.is_reusable}
                onChange={(e) => setFormData({ ...formData, is_reusable: e.target.checked })}
                className="w-4 h-4 rounded border-border"
              />
              <Label htmlFor="is_reusable" className="cursor-pointer">
                Make this transformation reusable across pipelines
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
                disabled={isSubmitting || !formData.name || !formData.sql_query}
                className="bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white"
              >
                {isSubmitting ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Create Transformation
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

