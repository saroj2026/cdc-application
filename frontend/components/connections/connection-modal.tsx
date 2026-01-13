"use client"

import { useState, useEffect } from "react"
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { AlertCircle, CheckCircle, ChevronLeft } from "lucide-react"
import { DatabaseSelector } from "./database-selector"
import { DatabaseInfo, getDatabaseByConnectionType } from "@/lib/database-icons"
import { DatabaseLogo } from "@/lib/database-logo-loader"

interface ConnectionModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (data: any) => void
  editingConnection?: any | null
}

export function ConnectionModal({ isOpen, onClose, onSave, editingConnection }: ConnectionModalProps) {
  const [step, setStep] = useState<"select" | "configure">("select")
  const [selectedDatabase, setSelectedDatabase] = useState<DatabaseInfo | null>(null)
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    engine: "",
    host: "",
    port: "",
    database: "",
    username: "",
    password: "",
    ssl_enabled: false,
  })
  const [testStatus, setTestStatus] = useState<"idle" | "testing" | "success" | "error">("idle")
  const [testMessage, setTestMessage] = useState("")

  // Load editing connection data
  useEffect(() => {
    if (editingConnection) {
      const dbInfo = getDatabaseByConnectionType(editingConnection.connection_type)
      setSelectedDatabase(dbInfo || null)
      setStep("configure")
      setFormData({
        name: editingConnection.name || "",
        description: editingConnection.description || "",
        engine: editingConnection.connection_type || "",
        host: editingConnection.host || "",
        port: String(editingConnection.port || ""),
        database: editingConnection.database || "",
        username: editingConnection.username || "",
        password: "", // Don't pre-fill password
        ssl_enabled: editingConnection.ssl_enabled || false,
      })
    } else {
      // Reset form when creating new
      setStep("select")
      setSelectedDatabase(null)
      setFormData({
        name: "",
        description: "",
        engine: "",
        host: "",
        port: "",
        database: "",
        username: "",
        password: "",
        ssl_enabled: false,
      })
    }
    setTestStatus("idle")
    setTestMessage("")
  }, [editingConnection, isOpen])

  // Handle database selection
  const handleDatabaseSelect = (database: DatabaseInfo) => {
    setSelectedDatabase(database)
    setFormData(prev => ({
      ...prev,
      engine: database.connectionType,
      port: String(database.defaultPort || ""),
    }))
    setStep("configure")
  }

  // Go back to database selection
  const handleBack = () => {
    setStep("select")
    setSelectedDatabase(null)
    setFormData({
      name: "",
      description: "",
      engine: "",
      host: "",
      port: "",
      database: "",
      username: "",
      password: "",
      ssl_enabled: false,
    })
    setTestStatus("idle")
    setTestMessage("")
  }

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }))
    setTestStatus("idle")
  }

  const handleTestConnection = async () => {
    // Validate required fields
    const missingFields = []
    if (!formData.host || !formData.host.trim()) missingFields.push("Host")
    if (!formData.port || !formData.port.trim() || isNaN(parseInt(formData.port))) missingFields.push("Port")
    if (!formData.database || !formData.database.trim()) missingFields.push("Database")
    if (!formData.username || !formData.username.trim()) missingFields.push("Username")
    if (!formData.password || formData.password.trim() === "") missingFields.push("Password")
    
    if (missingFields.length > 0) {
      setTestStatus("error")
      setTestMessage(`Please fill in: ${missingFields.join(", ")}`)
      return
    }

    setTestStatus("testing")
    setTestMessage("")
    
    try {
      const testData = {
        connection_type: formData.engine,
        host: formData.host.trim(),
        port: parseInt(formData.port) || (selectedDatabase?.defaultPort || 3306),
        database: formData.database.trim(),
        username: formData.username.trim(),
        password: formData.password,
        ssl_enabled: formData.ssl_enabled || false,
      }

      // If editing, use the connection ID endpoint, otherwise use test endpoint
      const endpoint = editingConnection 
        ? `/api/v1/connections/${editingConnection.id}/test`
        : `/api/v1/connections/test`

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(testData),
      })

      const result = await response.json()

      if (response.ok && (result.success || result.status === 'success')) {
        setTestStatus("success")
        setTestMessage(result.message || "Connection successful")
      } else {
        setTestStatus("error")
        // Extract error message safely
        let errorMsg = "Connection failed"
        if (result.detail) {
          if (typeof result.detail === 'string') {
            errorMsg = result.detail
          } else if (Array.isArray(result.detail)) {
            errorMsg = result.detail.map((err: any) => {
              const field = err.loc?.join('.') || 'field'
              return `${field}: ${err.msg || 'Invalid value'}`
            }).join(', ')
          } else if (typeof result.detail === 'object') {
            errorMsg = result.detail.message || result.detail.msg || JSON.stringify(result.detail)
          }
        } else if (result.message) {
          errorMsg = result.message
        }
        setTestMessage(errorMsg)
      }
    } catch (error: any) {
      setTestStatus("error")
      setTestMessage(error.message || "Failed to test connection")
    }
  }

  const handleSave = () => {
    // Validate required fields
    if (!formData.name || !formData.name.trim()) {
      alert("Connection name is required")
      return
    }
    if (!formData.engine) {
      alert("Database engine is required")
      return
    }
    if (!formData.host || !formData.host.trim()) {
      alert("Host is required")
      return
    }
    if (!formData.database || !formData.database.trim()) {
      alert("Database name is required")
      return
    }
    if (!formData.username || !formData.username.trim()) {
      alert("Username is required")
      return
    }
    if (!formData.password) {
      alert("Password is required")
      return
    }
    
    // Ensure port is valid
    const port = parseInt(formData.port) || (selectedDatabase?.defaultPort || 3306)
    if (port < 1 || port > 65535) {
      alert("Port must be between 1 and 65535")
      return
    }

    // Build data to save (no type/role - will be selected at pipeline creation)
    const dataToSave = {
      name: formData.name.trim(),
      description: formData.description?.trim() || "",
      engine: formData.engine, // Will be mapped to 'connection_type' in handleAddConnection
      host: formData.host.trim(),
      database: formData.database.trim(),
      username: formData.username.trim(),
      password: formData.password,
      port: String(port),
      ssl_enabled: formData.ssl_enabled || false,
    }
    
    console.log("Saving connection data:", { ...dataToSave, password: "***" })
    onSave(dataToSave)
  }

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className={`${step === "select" ? "max-w-6xl" : "max-w-md"} bg-surface border-border max-h-[90vh] flex flex-col p-0`}>
        {step === "select" ? (
          <>
            <DialogHeader className="px-6 pt-6 pb-4 flex-shrink-0">
              <DialogTitle className="text-foreground">
                Add New Service
              </DialogTitle>
              <DialogDescription className="text-foreground-muted">
                Select a database service to configure
              </DialogDescription>
            </DialogHeader>
            <div className="flex-1 overflow-y-auto px-6 py-6">
              <DatabaseSelector
                onSelect={handleDatabaseSelect}
                onCancel={onClose}
              />
            </div>
          </>
        ) : (
          <>
            <DialogHeader className="px-6 pt-6 pb-4 flex-shrink-0">
              <div className="flex items-center gap-3 mb-2">
                {!editingConnection && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleBack}
                    className="p-1 h-8 w-8"
                  >
                    <ChevronLeft className="w-4 h-4" />
                  </Button>
                )}
                <div className="flex-1">
                  <DialogTitle className="text-foreground">
                    {editingConnection ? "Edit Connection" : "Configure Service"}
                  </DialogTitle>
                  <DialogDescription className="text-foreground-muted">
                    {editingConnection
                      ? "Update database connection details"
                      : selectedDatabase
                        ? `Configure ${selectedDatabase.displayName} connection`
                        : "Configure database connection"}
                  </DialogDescription>
                </div>
              </div>
              
              {/* Progress Bar */}
              <div className="flex items-center gap-2 mt-4">
                <div className="flex-1 h-2 bg-surface-hover rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-2/4 transition-all duration-300"></div>
                </div>
                <span className="text-xs text-foreground-muted">Step 2 of 2</span>
              </div>
            </DialogHeader>

            <div className="flex-1 overflow-y-auto px-6 pb-4">
          <Tabs defaultValue="basic" className="w-full">
          <TabsList className="grid w-full grid-cols-2 bg-surface-hover">
            <TabsTrigger value="basic">Basic</TabsTrigger>
            <TabsTrigger value="advanced">Advanced</TabsTrigger>
          </TabsList>

          <TabsContent value="basic" className="space-y-4 mt-4">
            {/* Connection Name */}
            <div>
              <Label className="text-foreground">Connection Name *</Label>
              <Input
                placeholder="e.g., Production MySQL"
                value={formData.name}
                onChange={(e) => handleInputChange("name", e.target.value)}
                className="mt-1"
                required
              />
            </div>

            {/* Description */}
            <div>
              <Label className="text-foreground">Description</Label>
              <Input
                placeholder="Optional description"
                value={formData.description}
                onChange={(e) => handleInputChange("description", e.target.value)}
                className="mt-1"
              />
            </div>

            {/* Selected Database Info */}
            {selectedDatabase && (
              <div className="mb-4 p-3 bg-surface-hover rounded-lg border border-border">
                <div className="flex items-center gap-3">
                  <div className="w-14 h-14 rounded-lg bg-gradient-to-br from-primary/20 to-primary/10 flex items-center justify-center">
                    <DatabaseLogo 
                      connectionType={selectedDatabase.connectionType}
                      databaseId={selectedDatabase.id}
                      displayName={selectedDatabase.displayName}
                      size={32}
                      className="w-8 h-8"
                    />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">{selectedDatabase.displayName}</p>
                    <p className="text-xs text-foreground-muted">Connection Type: {selectedDatabase.connectionType}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Host */}
            <div>
              <Label className="text-foreground">Host</Label>
              <Input
                placeholder="localhost or IP address"
                value={formData.host}
                onChange={(e) => handleInputChange("host", e.target.value)}
                className="mt-1"
              />
            </div>

            {/* Port and Database */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label className="text-foreground">Port</Label>
                <Input
                  type="number"
                  placeholder={selectedDatabase?.defaultPort ? String(selectedDatabase.defaultPort) : "3306"}
                  value={formData.port}
                  onChange={(e) => handleInputChange("port", e.target.value)}
                  className="mt-1"
                />
              </div>
              <div>
                <Label className="text-foreground">
                  {formData.engine === "oracle" ? "Database/Service Name" : "Database"}
                </Label>
                <Input
                  placeholder={formData.engine === "oracle" ? "XE, ORCL, PDB1, etc." : "database name"}
                  value={formData.database}
                  onChange={(e) => handleInputChange("database", e.target.value)}
                  className="mt-1"
                />
                {formData.engine === "oracle" && (
                  <p className="text-xs text-foreground-muted mt-1.5 px-1">
                    <span className="font-medium text-warning">⚠️ Important:</span> For Oracle, enter the <span className="font-medium">Service Name or SID</span> (e.g., XE, ORCL, PDB1), <span className="font-medium">NOT your username</span>. Common service names: XE (Express), ORCL (Standard), PDB1/PDB2 (Pluggable DBs).
                  </p>
                )}
              </div>
            </div>

            {/* Username */}
            <div>
              <Label className="text-foreground">Username</Label>
              <Input
                placeholder="database user"
                value={formData.username}
                onChange={(e) => handleInputChange("username", e.target.value)}
                className="mt-1"
              />
            </div>

            {/* Password */}
            <div>
              <Label className="text-foreground">Password</Label>
              <Input
                type="password"
                placeholder="••••••••"
                value={formData.password}
                onChange={(e) => handleInputChange("password", e.target.value)}
                className="mt-1"
              />
            </div>
          </TabsContent>

          <TabsContent value="advanced" className="space-y-4 mt-4">
            <div>
              <Label className="text-foreground flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.ssl_enabled}
                  onChange={(e) => handleInputChange("ssl_enabled", e.target.checked)}
                  className="w-4 h-4"
                />
                Enable SSL/TLS
              </Label>
            </div>
          </TabsContent>
          </Tabs>

          {/* Test Status */}
          {testStatus !== "idle" && (
            <div
              className={`flex gap-2 p-3 rounded-lg border mt-4 ${
                testStatus === "success"
                  ? "bg-success/10 border-success/30"
                  : testStatus === "error"
                    ? "bg-error/10 border-error/30"
                    : "bg-info/10 border-info/30"
              }`}
            >
              {testStatus === "success" && (
                <>
                  <CheckCircle className="w-4 h-4 text-success flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm text-success font-medium">Connection successful!</p>
                    {testMessage && <p className="text-xs text-success/80 mt-1">{testMessage}</p>}
                  </div>
                </>
              )}
              {testStatus === "error" && (
                <>
                  <AlertCircle className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm text-error font-medium">Connection failed</p>
                    {testMessage && <p className="text-xs text-error/80 mt-1">{testMessage}</p>}
                  </div>
                </>
              )}
              {testStatus === "testing" && (
                <>
                  <div className="w-4 h-4 rounded-full border-2 border-info border-t-transparent animate-spin flex-shrink-0"></div>
                  <p className="text-sm text-info">Testing connection...</p>
                </>
              )}
            </div>
          )}
        </div>

            {/* Action Buttons - Fixed at bottom */}
            <div className="flex gap-3 justify-end px-6 py-4 border-t border-border bg-surface flex-shrink-0">
              <Button
                variant="outline"
                onClick={() => handleTestConnection()}
                className="bg-transparent border-border hover:bg-surface-hover"
                disabled={testStatus === "testing"}
              >
                {testStatus === "testing" ? "Testing..." : "Test Connection"}
              </Button>
              <Button variant="outline" onClick={onClose} className="bg-transparent border-border hover:bg-surface-hover">
                Cancel
              </Button>
              <Button 
                onClick={handleSave} 
                className="bg-primary hover:bg-primary/90 text-foreground"
                disabled={testStatus === "testing"}
              >
                Save Connection
              </Button>
            </div>
          </>
        )}
      </DialogContent>
    </Dialog>
  )
}
