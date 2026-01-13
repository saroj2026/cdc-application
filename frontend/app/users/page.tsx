"use client"

import { useState, useEffect, useMemo, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { 
  Users, 
  Plus, 
  Edit2, 
  Trash2, 
  Search, 
  MoreVertical, 
  Shield, 
  ShieldCheck, 
  UserCog, 
  Eye, 
  Loader2,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Filter,
  Zap,
  Circle,
  Activity
} from "lucide-react"
import { PageHeader } from "@/components/ui/page-header"
import { UserModal } from "@/components/users/user-modal"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { fetchUsers, deleteUser } from "@/lib/store/slices/userSlice"
import { formatDistanceToNow } from "date-fns"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger, DropdownMenuSeparator } from "@/components/ui/dropdown-menu"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { hasPermission } from "@/lib/store/slices/permissionSlice"
import { AuditLogViewer } from "@/components/users/audit-log-viewer"
import { store } from "@/lib/store/store"
import { ProtectedPage } from "@/components/auth/ProtectedPage"

interface User {
  id: string
  email: string
  full_name: string
  role_name: string
  status?: string
  is_active: boolean
  is_superuser: boolean
  last_login?: string
  created_at: string
}

const ROLE_COLORS: Record<string, string> = {
  super_admin: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  org_admin: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  data_engineer: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
  operator: "bg-green-500/20 text-green-400 border-green-500/30",
  viewer: "bg-gray-500/20 text-gray-400 border-gray-500/30",
}

const STATUS_COLORS: Record<string, string> = {
  active: "bg-green-500/20 text-green-400 border-green-500/30",
  invited: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
  suspended: "bg-red-500/20 text-red-400 border-red-500/30",
  deactivated: "bg-gray-500/20 text-gray-400 border-gray-500/30",
}

const ROLE_ICONS: Record<string, any> = {
  super_admin: ShieldCheck,
  org_admin: Shield,
  data_engineer: UserCog,
  operator: Eye,
  viewer: Eye,
}

export default function UsersPage() {
  const dispatch = useAppDispatch()
  const { user: currentUser } = useAppSelector((state) => state.auth)
  const { users, isLoading, error: usersError } = useAppSelector((state) => state.users)
  
  // Use state to prevent hydration mismatch
  const [mounted, setMounted] = useState(false)
  const [canCreateUser, setCanCreateUser] = useState(false)
  const [canManageRoles, setCanManageRoles] = useState(false)
  const [canViewAuditLogs, setCanViewAuditLogs] = useState(false)
  
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [editingUser, setEditingUser] = useState<User | null>(null)
  const [deleteConfirmOpen, setDeleteConfirmOpen] = useState(false)
  const [userToDelete, setUserToDelete] = useState<User | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [roleFilter, setRoleFilter] = useState<string>("all")
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [currentPage, setCurrentPage] = useState(1)
  const [activeTab, setActiveTab] = useState<"users" | "audit">("users")
  const usersPerPage = 8

  const hasFetchedRef = useRef(false)

  // Set permissions on client side only
  useEffect(() => {
    setMounted(true)
    const state = store.getState()
    setCanCreateUser(hasPermission("create_user")(state))
    setCanManageRoles(hasPermission("manage_roles")(state))
    setCanViewAuditLogs(hasPermission("view_audit_logs")(state))
  }, [])

  useEffect(() => {
    if (hasFetchedRef.current || isLoading) return
    hasFetchedRef.current = true
    dispatch(fetchUsers())
  }, [dispatch, isLoading])

  // Filter users
  const filteredUsers = useMemo(() => {
    let filtered = Array.isArray(users) ? users : []
    
    // Search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(u =>
        u.email?.toLowerCase().includes(query) ||
        u.full_name?.toLowerCase().includes(query) ||
        u.role_name?.toLowerCase().includes(query)
      )
    }
    
    // Role filter
    if (roleFilter !== "all") {
      filtered = filtered.filter(u => u.role_name === roleFilter)
    }
    
    // Status filter
    if (statusFilter !== "all") {
      if (statusFilter === "active") {
        filtered = filtered.filter(u => u.is_active && (!u.status || u.status === "active"))
      } else {
        filtered = filtered.filter(u => u.status === statusFilter)
      }
    }
    
    return filtered
  }, [users, searchQuery, roleFilter, statusFilter])

  // Pagination
  const totalPages = Math.ceil(filteredUsers.length / usersPerPage)
  const startIndex = (currentPage - 1) * usersPerPage
  const endIndex = startIndex + usersPerPage
  const paginatedUsers = filteredUsers.slice(startIndex, endIndex)

  useEffect(() => {
    setCurrentPage(1)
  }, [searchQuery, roleFilter, statusFilter])

  const handleCreateUser = () => {
    setEditingUser(null)
    setIsModalOpen(true)
  }

  const handleEditUser = (user: User) => {
    setEditingUser(user)
    setIsModalOpen(true)
  }

  const handleDeleteUser = (user: User) => {
    setUserToDelete(user)
    setDeleteConfirmOpen(true)
  }

  const confirmDelete = async () => {
    if (!userToDelete) return
    
    try {
      await dispatch(deleteUser(userToDelete.id)).unwrap()
      setDeleteConfirmOpen(false)
      setUserToDelete(null)
    } catch (err: any) {
      alert(err.message || "Failed to delete user")
    }
  }

  const handleSaveUser = async () => {
    await dispatch(fetchUsers())
    setIsModalOpen(false)
    setEditingUser(null)
  }

  const getRoleDisplayName = (role: string) => {
    return role.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')
  }

  const getStatusDisplayName = (status?: string, isActive?: boolean) => {
    if (!status && isActive) return "Active"
    if (!status) return "Inactive"
    return status.charAt(0).toUpperCase() + status.slice(1)
  }

  const getStatusIcon = (status?: string, isActive?: boolean) => {
    if (!status && isActive) return CheckCircle
    if (status === "active" || (!status && isActive)) return CheckCircle
    if (status === "invited") return Clock
    if (status === "suspended") return XCircle
    return AlertCircle
  }

  // Prevent hydration mismatch by not rendering action until mounted
  if (!mounted) {
    return (
      <div className="p-6 space-y-6">
        <PageHeader
          title="User Management"
          subtitle="Manage users, roles, and permissions for your CDC replication platform"
          icon={Users}
        />
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-foreground-muted" />
        </div>
      </div>
    )
  }

  return (
    <ProtectedPage path="/users" requiredPermission="create_user">
      <div className="p-6 space-y-6">
      <PageHeader
        title="User Management"
        subtitle="Manage users, roles, and permissions for your CDC replication platform"
        icon={Users}
        action={
          canCreateUser ? (
            <Button onClick={handleCreateUser} className="bg-primary hover:bg-primary/90 text-foreground gap-2">
              <Plus className="w-4 h-4" />
              New User
            </Button>
          ) : undefined
        }
      />

      {/* Error Message */}
      {usersError && (
        <div className="p-4 bg-error/10 border border-error/30 rounded-lg">
          <p className="text-sm text-error">{usersError}</p>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as "users" | "audit")}>
        <TabsList>
          <TabsTrigger value="users">Users</TabsTrigger>
          {canViewAuditLogs && <TabsTrigger value="audit">Audit Logs</TabsTrigger>}
        </TabsList>

        <TabsContent value="users" className="space-y-6">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1 relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-foreground-muted" />
                  <Input
                    placeholder="Search users by name, email, or role..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                  />
                </div>
                <Select value={roleFilter} onValueChange={setRoleFilter}>
                  <SelectTrigger className="w-[180px]">
                    <Filter className="w-4 h-4 mr-2" />
                    <SelectValue placeholder="All Roles" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Roles</SelectItem>
                    <SelectItem value="super_admin">Super Admin</SelectItem>
                    <SelectItem value="org_admin">Org Admin</SelectItem>
                    <SelectItem value="data_engineer">Data Engineer</SelectItem>
                    <SelectItem value="operator">Operator</SelectItem>
                    <SelectItem value="viewer">Viewer</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="All Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="invited">Invited</SelectItem>
                    <SelectItem value="suspended">Suspended</SelectItem>
                    <SelectItem value="deactivated">Deactivated</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Users List */}
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-6 h-6 animate-spin text-foreground-muted" />
              <span className="ml-2 text-foreground-muted">Loading users...</span>
            </div>
          ) : paginatedUsers.length === 0 ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Users className="w-16 h-16 mx-auto mb-4 opacity-20 text-foreground-muted" />
                <p className="text-foreground-muted mb-4">
                  {searchQuery || roleFilter !== "all" || statusFilter !== "all"
                    ? "No users match your filters"
                    : "No users found"}
                </p>
                {canCreateUser && !searchQuery && roleFilter === "all" && statusFilter === "all" && (
                  <Button onClick={handleCreateUser} className="bg-primary hover:bg-primary/90 text-foreground gap-2">
                    <Plus className="w-4 h-4" />
                    Create First User
                  </Button>
                )}
              </CardContent>
            </Card>
          ) : (
            <>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {paginatedUsers.map((user) => {
                  const RoleIcon = ROLE_ICONS[user.role_name] || Users
                  const StatusIcon = getStatusIcon(user.status, user.is_active)
                  const statusDisplay = getStatusDisplayName(user.status, user.is_active)
                  const statusColor = STATUS_COLORS[user.status || (user.is_active ? "active" : "inactive")] || STATUS_COLORS.active
                  const isActive = user.is_active && (!user.status || user.status === "active")

                  return (
                    <Card 
                      key={user.id} 
                      className="group relative overflow-hidden hover:border-primary/50 transition-all duration-300 hover:shadow-xl hover:shadow-primary/20 hover:scale-[1.02] bg-gradient-to-br from-surface/50 to-surface border-border/50"
                    >
                      {/* Animated background gradient */}
                      <div className="absolute inset-0 bg-gradient-to-br from-primary/0 via-primary/0 to-primary/0 group-hover:from-primary/5 group-hover:via-primary/5 group-hover:to-primary/5 transition-all duration-500" />
                      
                      {/* Active status indicator - Top Right */}
                      {isActive && (
                        <div className="absolute top-3 right-3 z-10">
                          <div className="relative">
                            <Circle className="w-2.5 h-2.5 fill-green-400 text-green-400 animate-pulse" />
                            <div className="absolute inset-0 w-2.5 h-2.5 bg-green-400 rounded-full animate-ping opacity-75" />
                          </div>
                        </div>
                      )}

                      <CardContent className="pt-6 pb-4 relative z-10 flex flex-col items-center text-center">
                        {/* Centered Avatar */}
                        <div className="relative mb-4">
                          <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary via-primary/80 to-primary/60 flex items-center justify-center text-white font-bold text-2xl shadow-lg shadow-primary/30 group-hover:shadow-primary/50 transition-all duration-300 group-hover:scale-110 group-hover:rotate-3">
                            {user.full_name?.charAt(0).toUpperCase() || user.email?.charAt(0).toUpperCase() || "U"}
                          </div>
                          {/* Pulsing ring for active users */}
                          {isActive && (
                            <div className="absolute -inset-2 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 opacity-20 animate-pulse blur-md" />
                          )}
                          {/* Status dot */}
                          <div className={`absolute -bottom-1 -right-1 w-5 h-5 rounded-full border-3 border-surface ${
                            isActive ? 'bg-green-400 animate-pulse' : 
                            user.status === 'invited' ? 'bg-yellow-400' :
                            user.status === 'suspended' ? 'bg-red-400' : 'bg-gray-400'
                          }`}>
                            {isActive && (
                              <div className="absolute inset-0 w-5 h-5 bg-green-400 rounded-full animate-ping opacity-75" />
                            )}
                          </div>
                        </div>
                        
                        {/* User Name */}
                        <div className="mb-2">
                          <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors duration-200 truncate w-full">
                            {user.full_name || user.email}
                          </h3>
                          {user.is_superuser && (
                            <Badge variant="outline" className="mt-1 bg-purple-500/20 text-purple-400 border-purple-500/30 text-xs">
                              <ShieldCheck className="w-3 h-3 mr-1" />
                              Super Admin
                            </Badge>
                          )}
                        </div>

                        {/* Email */}
                        <p className="text-sm text-foreground-muted mb-3 truncate w-full px-2">
                          {user.email}
                        </p>

                        {/* Role and Status Badges */}
                        <div className="flex flex-col items-center gap-2 mb-4 w-full">
                          <Badge 
                            variant="outline" 
                            className={`${ROLE_COLORS[user.role_name] || ROLE_COLORS.viewer} transition-all duration-200 group-hover:scale-105 text-xs`}
                          >
                            <RoleIcon className="w-3 h-3 mr-1" />
                            {getRoleDisplayName(user.role_name)}
                          </Badge>
                          <Badge 
                            variant="outline" 
                            className={`${statusColor} transition-all duration-200 group-hover:scale-105 text-xs`}
                          >
                            <StatusIcon className={`w-3 h-3 mr-1 ${isActive ? 'animate-pulse' : ''}`} />
                            {statusDisplay}
                          </Badge>
                          {user.last_login && (
                            <span className="text-xs text-foreground-muted flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {formatDistanceToNow(new Date(user.last_login), { addSuffix: true })}
                            </span>
                          )}
                        </div>

                        {/* Action Buttons - Edit and Delete */}
                        <div className="flex items-center justify-center gap-2 mt-auto pt-3 border-t border-border/50 w-full">
                          {canManageRoles && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleEditUser(user)}
                              className="flex-1 hover:bg-primary/10 hover:text-primary transition-colors"
                            >
                              <Edit2 className="w-4 h-4 mr-1" />
                              Edit
                            </Button>
                          )}
                          {canManageRoles && user.id !== currentUser?.id && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleDeleteUser(user)}
                              className="flex-1 hover:bg-red-500/10 hover:text-red-400 text-destructive transition-colors"
                            >
                              <Trash2 className="w-4 h-4 mr-1" />
                              Delete
                            </Button>
                          )}
                        </div>
                      </CardContent>
                    </Card>
                  )
                })}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between">
                  <p className="text-sm text-foreground-muted">
                    Showing {startIndex + 1} to {Math.min(endIndex, filteredUsers.length)} of {filteredUsers.length} users
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                    >
                      Previous
                    </Button>
                    <span className="text-sm text-foreground-muted">
                      Page {currentPage} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </TabsContent>

        {canViewAuditLogs && (
          <TabsContent value="audit">
            <AuditLogViewer />
          </TabsContent>
        )}
      </Tabs>

      {/* User Modal */}
      {canCreateUser || canManageRoles ? (
        <UserModal
          isOpen={isModalOpen}
          onClose={() => {
            setIsModalOpen(false)
            setEditingUser(null)
          }}
          onSave={handleSaveUser}
          editingUser={editingUser}
        />
      ) : null}

      {/* Delete Confirmation */}
      <Dialog open={deleteConfirmOpen} onOpenChange={setDeleteConfirmOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete User</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete {userToDelete?.full_name || userToDelete?.email}? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteConfirmOpen(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={confirmDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
      </div>
    </ProtectedPage>
  )
}
