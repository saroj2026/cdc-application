"use client"

import { useState, useEffect, useMemo, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Plus, Edit2, Trash2, TestTube, CheckCircle, AlertCircle, Loader2, AlertTriangle, Database, Search, ChevronLeft, ChevronRight } from "lucide-react"
import { PageHeader } from "@/components/ui/page-header"
import { ConnectionModal } from "@/components/connections/connection-modal"
import { ProtectedPage } from "@/components/auth/ProtectedPage"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import {
  fetchConnections,
  createConnection,
  updateConnection,
  deleteConnection,
  testConnection,
  setSelectedConnection,
} from "@/lib/store/slices/connectionSlice"
import { formatDistanceToNow } from "date-fns"
import { getDatabaseByConnectionType } from "@/lib/database-icons"
import { getDatabaseColor } from "@/lib/database-colors"
import { DatabaseLogo } from "@/lib/database-logo-loader"

export default function ConnectionsPage() {
  const dispatch = useAppDispatch()
  const { connections, isLoading, error } = useAppSelector((state) => state.connections)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingConnection, setEditingConnection] = useState<number | null>(null)
  const [testingConnectionId, setTestingConnectionId] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [connectionToDelete, setConnectionToDelete] = useState<{ id: number; name: string } | null>(null)
  const [currentPage, setCurrentPage] = useState(1)
  const connectionsPerPage = 10

  const hasFetchedRef = useRef(false)
  useEffect(() => {
    // Prevent multiple simultaneous calls
    if (hasFetchedRef.current || isLoading) return
    hasFetchedRef.current = true

    dispatch(fetchConnections())
  }, [dispatch, isLoading])

  // Filter connections based on search query
  const filteredConnections = useMemo(() => {
    // Ensure connections is an array
    const connectionsArray = Array.isArray(connections) ? connections : []
    
    if (!searchQuery.trim()) {
      return connectionsArray
    }
    
    const query = searchQuery.toLowerCase().trim()
    return connectionsArray.filter(connection => {
      const dbInfo = getDatabaseByConnectionType(connection.connection_type)
      const dbName = dbInfo?.displayName || connection.connection_type
      
      return (
        connection.name?.toLowerCase().includes(query) ||
        connection.connection_type?.toLowerCase().includes(query) ||
        dbName?.toLowerCase().includes(query) ||
        connection.host?.toLowerCase().includes(query) ||
        connection.database?.toLowerCase().includes(query)
      )
    })
  }, [connections, searchQuery])

  // Pagination logic
  const totalPages = Math.ceil(filteredConnections.length / connectionsPerPage)
  const startIndex = (currentPage - 1) * connectionsPerPage
  const endIndex = startIndex + connectionsPerPage
  const paginatedConnections = filteredConnections.slice(startIndex, endIndex)

  // Reset to page 1 when search changes
  useEffect(() => {
    setCurrentPage(1)
  }, [searchQuery, filteredConnections.length])

  const handleAddConnection = async (connectionData: any) => {
    console.log("[handleAddConnection] Received data:", connectionData)

    try {
      // Validate required fields with detailed error messages
      if (!connectionData || typeof connectionData !== 'object') {
        alert("Invalid connection data")
        return
      }

      if (!connectionData.name || !String(connectionData.name).trim()) {
        alert("Connection name is required")
        return
      }
      // Note: type/role removed - will be selected at pipeline creation
      // For now, default to 'source' if not provided (for backward compatibility)
      const defaultRole = "source"
      if (!connectionData.engine || !String(connectionData.engine).trim()) {
        alert("Database engine is required")
        return
      }
      if (!connectionData.host || !String(connectionData.host).trim()) {
        alert("Host is required")
        return
      }
      if (!connectionData.database || !String(connectionData.database).trim()) {
        alert("Database name is required")
        return
      }
      if (!connectionData.username || !String(connectionData.username).trim()) {
        alert("Username is required")
        return
      }
      if (!connectionData.password || !String(connectionData.password)) {
        alert("Password is required")
        return
      }

      // Map engine to database_type (support all database types)
      const databaseTypeMap: Record<string, string> = {
        "mysql": "mysql",
        "mariadb": "mysql",
        "postgresql": "postgresql",
        "postgres": "postgresql",
        "mongodb": "mongodb",
        "mssql": "sqlserver",
        "sqlserver": "sqlserver",
        "azuresql": "sqlserver",
        "oracle": "oracle",
        "as400": "as400",
        "aws_s3": "aws_s3",
        "snowflake": "snowflake",
        "s3": "s3",
        // Add all other database types - use engine value as database_type
      }

      const engineValue = String(connectionData?.engine || "").toLowerCase().trim()
      if (!engineValue) {
        alert("Database engine is required")
        return
      }
      
      const mappedDatabaseType = databaseTypeMap[engineValue] || engineValue

      // Accept any database type (backend will validate)
      if (!mappedDatabaseType || !mappedDatabaseType.trim()) {
        alert(`Invalid database engine: ${engineValue}`)
        return
      }

      // Default to 'source' role (can be changed at pipeline creation)
      const mappedRole = "source"

      // Build payload with all required fields - ensure name and database_type are always present
      // Extract and validate all fields before building payload
      const nameValue = String(connectionData?.name || "").trim()
      
      // CRITICAL: If name is missing or empty, show error immediately
      if (!nameValue || nameValue.length === 0) {
        console.error("[handleAddConnection] Name is missing or empty!", {
          connectionData,
          nameValue,
          hasName: !!connectionData?.name,
          nameType: typeof connectionData?.name
        })
        alert("Connection name is required and cannot be empty")
        return
      }
      
      const databaseTypeValue = String(mappedDatabaseType || "").trim()
      
      // CRITICAL: If database_type is missing or empty, show error immediately
      if (!databaseTypeValue || databaseTypeValue.length === 0) {
        console.error("[handleAddConnection] Database type is missing or empty!", {
          connectionData,
          engineValue,
          mappedDatabaseType,
          databaseTypeValue
        })
        alert("Database type is required and cannot be empty")
        return
      }
      const hostValue = String(connectionData?.host || "").trim()
      const databaseValue = String(connectionData?.database || "").trim()
      const usernameValue = String(connectionData?.username || "").trim()
      const passwordValue = String(connectionData?.password || "")
      const portValue = parseInt(String(connectionData?.port || "3306")) || 3306

      // Final validation before building payload (name and database_type already validated above)
      if (!hostValue) {
        alert("Host is required")
        return
      }
      if (!databaseValue) {
        alert("Database name is required")
        return
      }
      if (!usernameValue) {
        alert("Username is required")
        return
      }
      if (!passwordValue) {
        alert("Password is required")
        return
      }

      // Build payload with validated values - ensure all required fields are present
      // DO NOT use any conditional logic that might exclude required fields
      const payload: any = {
        name: nameValue,  // Required: connection name (already validated above)
        database_type: databaseTypeValue,  // Required: database type (already validated above)
        connection_type: mappedRole,  // Optional: role (source/target), defaults to "source"
        host: hostValue,
        port: portValue,
        database: databaseValue,
        username: usernameValue,
        password: passwordValue,
        ssl_enabled: Boolean(connectionData?.ssl_enabled || false),
      }
      
      // CRITICAL: Double-check that required fields are present (defensive programming)
      if (!payload.name || typeof payload.name !== 'string' || payload.name.trim().length === 0) {
        console.error("[handleAddConnection] CRITICAL ERROR: name is missing after payload construction!", payload)
        alert("Internal error: Connection name is missing. Please check console.")
        return
      }
      if (!payload.database_type || typeof payload.database_type !== 'string' || payload.database_type.trim().length === 0) {
        console.error("[handleAddConnection] CRITICAL ERROR: database_type is missing after payload construction!", payload)
        alert("Internal error: Database type is missing. Please check console.")
        return
      }

      // Add optional fields
      if (connectionData?.description) {
        payload.description = String(connectionData.description).trim()
      }
      if (connectionData?.schema_name) {
        payload.schema_name = String(connectionData.schema_name).trim()
      }
      // Role defaults to 'source' (can be changed at pipeline creation)

      // Final safety check - ensure payload has required fields
      if (!payload.name || !payload.database_type) {
        console.error("[handleAddConnection] CRITICAL: Payload missing required fields!", {
          payload,
          hasName: !!payload.name,
          hasDatabaseType: !!payload.database_type,
          connectionData
        })
        alert("Internal error: Missing required fields. Please check console for details.")
        return
      }

      // Final verification: Serialize and check the payload one more time
      const payloadString = JSON.stringify(payload)
      const payloadParsed = JSON.parse(payloadString)
      
      if (!payloadParsed.name || !payloadParsed.database_type) {
        console.error("[handleAddConnection] CRITICAL: Payload missing fields after serialization!", {
          originalPayload: payload,
          serializedPayload: payloadParsed,
          payloadString: payloadString.substring(0, 200)
        })
        alert("Internal error: Payload validation failed. Please check console.")
        return
      }

      console.log("[handleAddConnection] Payload being sent:", { ...payload, password: "***" })
      console.log("[handleAddConnection] Payload keys:", Object.keys(payload))
      console.log("[handleAddConnection] Payload JSON:", payloadString.substring(0, 300))
      console.log("[handleAddConnection] Required fields check:", {
        hasName: !!payload.name && payload.name.trim().length > 0,
        hasDatabaseType: !!payload.database_type && payload.database_type.trim().length > 0,
        hasConnectionType: !!payload.connection_type,
        hasPassword: !!payload.password,
        payloadName: payload.name,
        payloadDatabaseType: payload.database_type,
        nameType: typeof payload.name,
        databaseTypeType: typeof payload.database_type
      })

      // Ensure we're sending the correct payload structure
      const finalPayload = {
        name: String(payload.name).trim(),
        database_type: String(payload.database_type).trim(),
        connection_type: String(payload.connection_type || "source").trim(),
        host: String(payload.host).trim(),
        port: Number(payload.port),
        database: String(payload.database).trim(),
        username: String(payload.username).trim(),
        password: String(payload.password),
        ssl_enabled: Boolean(payload.ssl_enabled),
        ...(payload.description && { description: String(payload.description).trim() }),
        ...(payload.schema_name && { schema_name: String(payload.schema_name).trim() }),
      }

      console.log("[handleAddConnection] Final payload being sent:", { ...finalPayload, password: "***" })

      await dispatch(createConnection(finalPayload)).unwrap()
      setIsModalOpen(false)
      setEditingConnection(null)
    } catch (err) {
      console.error("[handleAddConnection] Failed to create connection:", err)
      // Error is already handled by Redux slice and displayed in the UI
    }
  }

  const handleUpdateConnection = async (connectionData: any) => {
    if (!editingConnection) return
    try {
      // Map engine to database_type (same as handleAddConnection)
      const databaseTypeMap: Record<string, string> = {
        "mysql": "mysql", "mariadb": "mysql", "postgresql": "postgresql", "postgres": "postgresql",
        "mongodb": "mongodb", "mssql": "sqlserver", "sqlserver": "sqlserver", "azuresql": "sqlserver",
        "oracle": "oracle", "as400": "as400", "aws_s3": "aws_s3", "snowflake": "snowflake", "s3": "s3",
      }
      
      const engineValue = String(connectionData?.engine || "").toLowerCase().trim()
      const mappedDatabaseType = databaseTypeMap[engineValue] || engineValue
      
      await dispatch(updateConnection({
        id: editingConnection,
        data: {
          name: connectionData.name,
          database_type: mappedDatabaseType,  // Required by backend
          connection_type: "source",  // Default role
          description: connectionData.description || "",
          host: connectionData.host,
          port: parseInt(connectionData.port) || 3306,
          database: connectionData.database,
          username: connectionData.username,
          password: connectionData.password,
          ssl_enabled: connectionData.ssl_enabled || false,
        }
      })).unwrap()
      setIsModalOpen(false)
      setEditingConnection(null)
    } catch (err) {
      console.error("Failed to update connection:", err)
    }
  }

  const handleDeleteClick = (id: number, name: string) => {
    setConnectionToDelete({ id, name })
    setDeleteConfirmOpen(true)
  }

  const handleDeleteConnection = async () => {
    if (!connectionToDelete) return

    try {
      await dispatch(deleteConnection(connectionToDelete.id)).unwrap()
      setDeleteConfirmOpen(false)
      setConnectionToDelete(null)
    } catch (err) {
      console.error("Failed to delete connection:", err)
      alert("Failed to delete connection. Please try again.")
    }
  }

  const handleTestConnection = async (id: number) => {
    setTestingConnectionId(id)
    try {
      console.log('[handleTestConnection] Testing connection:', id, typeof id)
      const result = await dispatch(testConnection(id)).unwrap()
      console.log('[handleTestConnection] Test result:', result)
      
      // Small delay to ensure backend has committed the status update
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Refresh connections to update test status from backend
      await dispatch(fetchConnections())
      
      // Show success message if available
      if (result?.message) {
        alert(`Connection test successful: ${result.message}`)
      } else {
        alert('Connection test successful!')
      }
    } catch (err: any) {
      console.error("Connection test failed:", err)
      // Small delay to ensure backend has committed the status update
      await new Promise(resolve => setTimeout(resolve, 1000))
      // Refresh connections to update test status (even on failure)
      await dispatch(fetchConnections())
      // Show user-friendly error message
      const errorMessage = typeof err === 'string' ? err : err?.message || 'Connection test failed. Please check your connection settings and try again.'
      alert(`Connection test failed:\n\n${errorMessage}`)
    } finally {
      setTestingConnectionId(null)
    }
  }

  return (
    <ProtectedPage path="/connections" requiredPermission="create_connection">
      <div className="p-6 space-y-6">
        <PageHeader
          title="Database Connections"
        subtitle={`${connections.length} connection${connections.length !== 1 ? 's' : ''} configured`}
        icon={Database}
        action={
          <Button
            onClick={() => {
              setEditingConnection(null)
              setIsModalOpen(true)
            }}
            className="bg-primary hover:bg-primary/90 text-foreground gap-2"
          >
            <Plus className="w-4 h-4" />
            New Connection
          </Button>
        }
      />

      {/* Search Box */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-foreground-muted" />
        <Input
          type="text"
          placeholder="Search connections by name, database type, host, or database name..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10 bg-surface border-border focus:border-primary"
        />
      </div>

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-error/10 border border-error/30 rounded-lg">
          <p className="text-sm text-error">
            {error}
          </p>
        </div>
      )}

      {/* Loading State */}
      {isLoading && connections.length === 0 && (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-foreground-muted" />
          <span className="ml-2 text-foreground-muted">Loading connections...</span>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredConnections.length === 0 && (
        <div className="text-center py-12">
          <p className="text-foreground-muted mb-4">
            {searchQuery.trim()
              ? `No connections found matching "${searchQuery}"`
              : connections.length === 0
                ? 'No connections found'
                : 'No connections match your search'}
          </p>
          {connections.length === 0 && (
            <Button
              onClick={() => {
                setEditingConnection(null)
                setIsModalOpen(true)
              }}
              className="bg-primary hover:bg-primary/90 text-foreground gap-2"
            >
              <Plus className="w-4 h-4" />
              Create First Connection
            </Button>
          )}
          {searchQuery.trim() && connections.length > 0 && (
            <Button
              onClick={() => setSearchQuery("")}
              variant="outline"
              className="border-border hover:bg-surface-hover"
            >
              Clear Search
            </Button>
          )}
        </div>
      )}

      {/* Connection Cards Grid */}
      {paginatedConnections.length > 0 && (
        <>
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 2xl:grid-cols-6 gap-4">
            {paginatedConnections.map((connection) => {
            const isConnected = connection.last_test_status === "success"
            const isTesting = testingConnectionId === connection.id
            // Use database_type if available, otherwise fall back to connection_type
            const dbType = (connection as any).database_type || connection.connection_type
            const dbInfo = getDatabaseByConnectionType(dbType)
            const dbColor = getDatabaseColor(dbType)

            return (
              <Card 
                key={connection.id} 
                className="group relative overflow-hidden border-2 hover:scale-[1.02] transition-all duration-300 bg-gradient-to-br from-white/5 to-white/0 backdrop-blur-sm"
                style={{
                  background: `linear-gradient(135deg, ${dbColor.primary}08 0%, ${dbColor.secondary}05 100%)`,
                  borderColor: `${dbColor.primary}30`,
                  boxShadow: `0 4px 6px -1px ${dbColor.primary}10, 0 2px 4px -1px ${dbColor.primary}05`
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = `0 20px 25px -5px ${dbColor.primary}20, 0 10px 10px -5px ${dbColor.primary}10`
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = `0 4px 6px -1px ${dbColor.primary}10, 0 2px 4px -1px ${dbColor.primary}05`
                }}
              >
                {/* Animated Connection Indicator - Top Right */}
                {isConnected && (
                  <div className="absolute top-3 right-3 z-10">
                    <div className="relative">
                      <div className="w-2.5 h-2.5 bg-success rounded-full animate-pulse shadow-lg shadow-success/50"></div>
                      <div className="absolute inset-0 w-2.5 h-2.5 bg-success rounded-full animate-ping opacity-60"></div>
                    </div>
                  </div>
                )}

                {/* Database Color Accent Bar */}
                <div 
                  className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r"
                  style={{
                    background: `linear-gradient(90deg, ${dbColor.primary}, ${dbColor.secondary})`
                  }}
                />

                {/* Header with Database Icon */}
                <div className="p-4 pb-3">
                  <div className="flex items-start gap-3 mb-3">
                    {/* Database Icon with Brand Color */}
                    <div 
                      className="w-16 h-16 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg bg-white/10"
                      style={{
                        background: `linear-gradient(135deg, ${dbColor.primary}15, ${dbColor.secondary}10)`
                      }}
                    >
                      <DatabaseLogo 
                        connectionType={dbType}
                        databaseId={dbInfo?.id}
                        databaseName={connection.name}
                        displayName={dbInfo?.displayName}
                        size={40}
                        className="w-10 h-10"
                      />
                    </div>
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-bold text-foreground truncate group-hover:opacity-80 transition-opacity mb-1">
                        {connection.name}
                      </h3>
                      <p className="text-xs text-foreground-muted truncate">
                        {dbInfo?.displayName || connection.connection_type.toUpperCase()}
                      </p>
                    </div>
                  </div>

                  {/* Connection Status */}
                  <div className="mb-3">
                    {isConnected ? (
                      <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-success/10 border border-success/30 rounded-md text-xs">
                        <div className="w-2 h-2 bg-success rounded-full animate-pulse"></div>
                        <span className="font-medium text-success">Connected</span>
                      </div>
                    ) : connection.last_test_status === "failed" ? (
                      <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-error/10 border border-error/30 rounded-md text-xs">
                        <AlertCircle className="w-3 h-3 text-error" />
                        <span className="font-medium text-error">Failed</span>
                      </div>
                    ) : (
                      <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-warning/10 border border-warning/30 rounded-md text-xs">
                        <AlertCircle className="w-3 h-3 text-warning" />
                        <span className="font-medium text-warning">Not Tested</span>
                      </div>
                    )}
                    {isTesting && (
                      <div className="inline-flex items-center gap-1.5 px-2 py-1 bg-primary/10 border border-primary/30 rounded-md text-xs ml-2">
                        <Loader2 className="w-3 h-3 text-primary animate-spin" />
                        <span className="font-medium text-primary">Testing</span>
                      </div>
                    )}
                  </div>

                  {/* Database Info */}
                  <div className="space-y-1.5 mb-3 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-foreground-muted">Host:</span>
                      <span className="text-foreground font-medium truncate ml-2 max-w-[120px]" title={connection.host}>
                        {connection.host}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-foreground-muted">Database:</span>
                      <span className="text-foreground font-medium truncate ml-2 max-w-[120px]" title={connection.database}>
                        {connection.database}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-foreground-muted">User:</span>
                      <span className="text-foreground font-medium truncate ml-2 max-w-[120px]" title={connection.username}>
                        {connection.username}
                      </span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 pt-3 border-t border-border/50">
                    <Button
                      variant="outline"
                      size="sm"
                      className="flex-1 h-8 text-xs bg-transparent border-border hover:bg-surface-hover"
                      style={{
                        borderColor: `${dbColor.primary}40`,
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = dbColor.primary
                        e.currentTarget.style.backgroundColor = `${dbColor.primary}10`
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = `${dbColor.primary}40`
                        e.currentTarget.style.backgroundColor = 'transparent'
                      }}
                      onClick={() => handleTestConnection(connection.id)}
                      disabled={isLoading || testingConnectionId !== null}
                    >
                      <TestTube className="w-3 h-3 mr-1" />
                      Test
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8 w-8 p-0 bg-transparent border-border hover:bg-surface-hover"
                      style={{
                        borderColor: `${dbColor.primary}40`,
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.borderColor = dbColor.primary
                        e.currentTarget.style.backgroundColor = `${dbColor.primary}10`
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.borderColor = `${dbColor.primary}40`
                        e.currentTarget.style.backgroundColor = 'transparent'
                      }}
                      onClick={() => {
                        setEditingConnection(connection.id)
                        setIsModalOpen(true)
                      }}
                      title="Edit"
                    >
                      <Edit2 className="w-3.5 h-3.5" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      className="h-8 w-8 p-0 bg-transparent border-error/30 hover:bg-error/10 text-error hover:text-error"
                      onClick={() => handleDeleteClick(connection.id, connection.name)}
                      disabled={isLoading}
                      title="Delete"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </Button>
                  </div>
                </div>
              </Card>
            )
          })}
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between pt-6 border-t border-border">
              <div className="text-sm text-foreground-muted">
                Showing <span className="font-semibold text-foreground">{startIndex + 1}</span> to{" "}
                <span className="font-semibold text-foreground">
                  {Math.min(endIndex, filteredConnections.length)}
                </span>{" "}
                of <span className="font-semibold text-foreground">{filteredConnections.length}</span> connections
              </div>
              
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="border-border hover:bg-surface-hover disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Previous
                </Button>
                
                <div className="flex items-center gap-1">
                  {Array.from({ length: totalPages }, (_, i) => i + 1).map((page) => {
                    // Show first page, last page, current page, and pages around current
                    if (
                      page === 1 ||
                      page === totalPages ||
                      (page >= currentPage - 1 && page <= currentPage + 1)
                    ) {
                      return (
                        <Button
                          key={page}
                          variant={currentPage === page ? "default" : "outline"}
                          size="sm"
                          onClick={() => setCurrentPage(page)}
                          className={`min-w-[40px] ${
                            currentPage === page
                              ? "bg-primary text-white"
                              : "border-border hover:bg-surface-hover"
                          }`}
                        >
                          {page}
                        </Button>
                      )
                    } else if (
                      page === currentPage - 2 ||
                      page === currentPage + 2
                    ) {
                      return (
                        <span key={page} className="px-2 text-foreground-muted">
                          ...
                        </span>
                      )
                    }
                    return null
                  })}
                </div>
                
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="border-border hover:bg-surface-hover disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                  <ChevronRight className="w-4 h-4 ml-1" />
                </Button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Connection Modal */}
      <ConnectionModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false)
          setEditingConnection(null)
        }}
        onSave={editingConnection ? handleUpdateConnection : handleAddConnection}
        editingConnection={editingConnection ? connections.find(c => c.id === editingConnection) || null : null}
      />

      {/* Delete Confirmation Modal */}
      <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <DialogContent className="bg-surface border-border max-w-md">
          <DialogHeader>
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-error/10 rounded-full">
                <AlertTriangle className="w-6 h-6 text-error" />
              </div>
              <DialogTitle className="text-foreground text-xl">Delete Connection</DialogTitle>
            </div>
            <DialogDescription className="text-foreground-muted pt-2">
              Are you sure you want to delete this connection? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <div className="p-4 bg-surface-hover rounded-lg border border-border">
              <p className="text-sm text-foreground-muted mb-1">Connection Name:</p>
              <p className="text-lg font-semibold text-foreground">
                {connectionToDelete?.name || "Unknown"}
              </p>
            </div>
            <div className="mt-4 p-3 bg-warning/10 border border-warning/30 rounded-lg">
              <p className="text-sm text-warning flex items-start gap-2">
                <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>
                  <strong>Warning:</strong> Deleting this connection will also remove any pipelines
                  that use it. Make sure no active pipelines depend on this connection.
                </span>
              </p>
            </div>
          </div>

          <DialogFooter className="gap-2">
            <Button
              variant="outline"
              onClick={() => {
                setDeleteConfirmOpen(false)
                setConnectionToDelete(null)
              }}
              className="bg-transparent border-border hover:bg-surface-hover"
            >
              Cancel
            </Button>
            <Button
              onClick={handleDeleteConnection}
              className="bg-error hover:bg-error/90 text-white"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="w-4 h-4 mr-2" />
                  Delete Connection
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      </div>
    </ProtectedPage>
  )
}
