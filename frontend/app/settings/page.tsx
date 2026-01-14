"use client"

import { useState, useEffect } from "react"
import { useAppDispatch, useAppSelector } from "@/lib/store/hooks"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { apiClient } from "@/lib/api/client"
import { Settings, User, Mail, Lock, Key, Send, X, CheckCircle, AlertCircle, RefreshCw } from "lucide-react"
import { PageHeader } from "@/components/ui/page-header"
import { useToast } from "@/components/ui/use-toast"
import { getCurrentUser } from "@/lib/store/slices/authSlice"
import { ProtectedPage } from "@/components/auth/ProtectedPage"

interface UserData {
  id: string
  email: string
  full_name: string
  is_active: boolean
  is_superuser: boolean
}

export default function SettingsPage() {
  const dispatch = useAppDispatch()
  const { user: currentUser } = useAppSelector((state) => state.auth)
  const { toast } = useToast()
  const [users, setUsers] = useState<UserData[]>([])
  const [loading, setLoading] = useState(true)
  const [mounted, setMounted] = useState(false)
  const [selectedUser, setSelectedUser] = useState<UserData | null>(null)
  const [showChangePasswordDialog, setShowChangePasswordDialog] = useState(false)
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [sendEmail, setSendEmail] = useState(true)
  const [changingPassword, setChangingPassword] = useState(false)
  const [passwordChangeSuccess, setPasswordChangeSuccess] = useState(false)
  const [generatedPassword, setGeneratedPassword] = useState("")

  // Handle client-side mounting to prevent hydration errors
  useEffect(() => {
    setMounted(true)
  }, [])

  useEffect(() => {
    // Ensure current user is loaded - always refetch to get latest data
    const loadUserData = async () => {
      if (mounted) {
        try {
          // Always refetch to ensure we have the latest user data (especially is_superuser)
          // Use safe unwrap - don't throw if it fails, just log
          const result = await dispatch(getCurrentUser())
          if (getCurrentUser.fulfilled.match(result)) {
            const userData = result.payload
            console.log('[Settings] Loaded user data:', {
              email: userData?.email,
              is_superuser: userData?.is_superuser,
              full_user: userData
            })
          } else if (getCurrentUser.rejected.match(result)) {
            // Error occurred but don't throw - use cached user if available
            console.error('[Settings] Failed to load current user (non-blocking):', result.error)
          }
        } catch (error: any) {
          // Don't show alert - just log and use cached user if available
          console.error('[Settings] Failed to load current user:', error)
          console.error('[Settings] Error details:', {
            message: error?.message,
            response: error?.response?.data,
            status: error?.response?.status
          })

          // Don't clear localStorage immediately - keep cached user if available
          // Only clear if it's an authentication error (401/403)
          if (error?.response?.status === 401 || error?.response?.status === 403) {
            console.warn('[Settings] Authentication error, clearing cached data')
            if (typeof window !== 'undefined') {
              localStorage.removeItem('user')
              localStorage.removeItem('access_token')
            }
          } else {
            // For other errors (network, server), keep cached user data
            console.log('[Settings] Keeping cached user data for non-auth errors')
          }
        }
      }
    }
    // Only load once on mount, not on every currentUser change to avoid infinite loops
    if (mounted && !currentUser) {
      loadUserData()
    }
  }, [mounted, dispatch]) // Removed currentUser from dependencies to prevent infinite loops

  useEffect(() => {
    // Only load users if we're admin
    if (mounted && currentUser?.is_superuser) {
      loadUsers()
    }
  }, [currentUser?.is_superuser, mounted]) // Only depend on is_superuser, not entire currentUser object

  const loadUsers = async () => {
    try {
      setLoading(true)
      const usersData = await apiClient.getUsers(0, 1000) // Increase limit to get all users
      setUsers(usersData || [])
    } catch (error: any) {
      console.error("Failed to load users:", error)
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to load users. Please try again.",
        variant: "destructive"
      })
      setUsers([]) // Set empty array on error
    } finally {
      setLoading(false)
    }
  }

  const handleChangePassword = (user: UserData) => {
    setSelectedUser(user)
    setNewPassword("")
    setConfirmPassword("")
    setSendEmail(true)
    setPasswordChangeSuccess(false)
    setGeneratedPassword("")
    setShowChangePasswordDialog(true)
  }

  const generateRandomPassword = () => {
    const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*"
    let password = ""
    for (let i = 0; i < 12; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length))
    }
    setNewPassword(password)
    setConfirmPassword(password)
  }

  const handleSubmitPasswordChange = async () => {
    if (!selectedUser) return

    if (!newPassword) {
      toast({
        title: "Validation Error",
        description: "Please enter a new password or generate one",
        variant: "destructive"
      })
      return
    }

    if (newPassword.length < 6) {
      toast({
        title: "Validation Error",
        description: "Password must be at least 6 characters",
        variant: "destructive"
      })
      return
    }

    if (newPassword !== confirmPassword) {
      toast({
        title: "Validation Error",
        description: "Passwords do not match",
        variant: "destructive"
      })
      return
    }

    setChangingPassword(true)
    setPasswordChangeSuccess(false)
    setGeneratedPassword("")

    try {
      const response = await apiClient.adminChangePassword(
        selectedUser.id,
        newPassword,
        sendEmail
      )

      setPasswordChangeSuccess(true)
      setGeneratedPassword(response.new_password || "")

      toast({
        title: "Success",
        description: sendEmail
          ? `Password changed successfully! An email has been sent to ${selectedUser.email}`
          : "Password changed successfully!",
      })

      // Reset form after 3 seconds
      setTimeout(() => {
        setShowChangePasswordDialog(false)
        setSelectedUser(null)
        setNewPassword("")
        setConfirmPassword("")
        setPasswordChangeSuccess(false)
        setGeneratedPassword("")
      }, 3000)
    } catch (error: any) {
      console.error("Failed to change password:", error)
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to change password. Please try again.",
        variant: "destructive"
      })
    } finally {
      setChangingPassword(false)
    }
  }

  // Check if current user is admin
  const isAdmin = currentUser?.is_superuser

  // Prevent hydration mismatch by showing loading state during SSR
  if (!mounted) {
    return (
      <div className="p-6">
        <Card className="p-6">
          <div className="flex items-center gap-3">
            <p>Loading...</p>
          </div>
        </Card>
      </div>
    )
  }

  if (!currentUser) {
    return (
      <div className="p-6">
        <Card className="p-6">
          <div className="flex items-center gap-3">
            <p>Loading user information...</p>
          </div>
        </Card>
      </div>
    )
  }

  if (!isAdmin) {
    return (
      <div className="p-6">
        <Card className="p-6">
          <div className="flex items-center gap-3 text-error">
            <AlertCircle className="w-5 h-5" />
            <div>
              <p className="font-semibold">Access denied. Only administrators can access this page.</p>
              <p className="text-sm text-foreground-muted mt-1">
                Current user: {currentUser.email} | is_superuser: {String(currentUser.is_superuser)}
              </p>
              <p className="text-xs text-foreground-muted mt-1">
                If you believe you should have admin access, please contact your administrator or check that your account was created with the admin role.
              </p>
            </div>
          </div>
        </Card>
      </div>
    )
  }

  return (
    <ProtectedPage path="/settings" requiredPermission="manage_roles">
      <div className="p-6 space-y-6">
        <PageHeader
          title="Settings"
        subtitle="Manage users and passwords"
        icon={Settings}
      />

      {/* Users Management Card - Enhanced */}
      <Card className="p-6 bg-gradient-to-br from-purple-500/5 to-blue-500/5 border-purple-500/20 shadow-xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
              <User className="w-6 h-6 text-purple-400" />
              User Management
            </h2>
            <p className="text-sm text-foreground-muted mt-1">Manage user accounts and passwords</p>
          </div>
          <Button
            onClick={loadUsers}
            variant="outline"
            size="sm"
            disabled={loading}
            className="bg-transparent border-border hover:bg-purple-500/10 hover:border-purple-500/50 hover:text-purple-400 gap-2 transition-all duration-200"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </div>

        {loading ? (
          <div className="text-center py-8">
            <p className="text-foreground-muted">Loading users...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-foreground-muted">No users found</p>
          </div>
        ) : (
          <div className="space-y-3">
            {users.map((user) => (
              <div
                key={user.id}
                className="flex items-center justify-between p-4 bg-gradient-to-br from-surface-hover to-surface rounded-lg border border-border hover:border-purple-500/30 transition-all duration-300 hover:shadow-md"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="w-5 h-5 text-primary" />
                  </div>
                  <div>
                    <p className="font-medium text-foreground">{user.full_name || user.email}</p>
                    <div className="flex items-center gap-2 text-xs text-foreground-muted">
                      <Mail className="w-3 h-3" />
                      <span>{user.email}</span>
                      {user.is_superuser && (
                        <span className="px-2 py-0.5 bg-primary/10 text-primary rounded text-xs font-medium">
                          Admin
                        </span>
                      )}
                      {!user.is_active && (
                        <span className="px-2 py-0.5 bg-error/10 text-error rounded text-xs font-medium">
                          Inactive
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                <Button
                  onClick={() => handleChangePassword(user)}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <Key className="w-4 h-4" />
                  Change Password
                </Button>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Change Password Dialog */}
      <Dialog open={showChangePasswordDialog} onOpenChange={setShowChangePasswordDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Lock className="w-5 h-5 text-primary" />
              Change Password
            </DialogTitle>
            <DialogDescription>
              Change password for {selectedUser?.email}
            </DialogDescription>
          </DialogHeader>

          {passwordChangeSuccess ? (
            <div className="space-y-4">
              <div className="p-4 bg-teal-400/10 border border-teal-400/30 rounded-lg">
                <div className="flex items-center gap-2 text-teal-400 mb-2">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-medium">Password changed successfully!</span>
                </div>
                {generatedPassword && !sendEmail && (
                  <div className="mt-3 p-3 bg-surface rounded border border-border">
                    <p className="text-xs text-foreground-muted mb-1">New Password:</p>
                    <p className="font-mono text-sm font-medium text-foreground break-all">
                      {generatedPassword}
                    </p>
                    <p className="text-xs text-foreground-muted mt-2">
                      Please copy this password and send it to the user securely.
                    </p>
                  </div>
                )}
                {sendEmail && (
                  <p className="text-sm text-foreground-muted mt-2">
                    An email has been sent to {selectedUser?.email} with the new password.
                  </p>
                )}
              </div>
              <Button
                onClick={() => {
                  setShowChangePasswordDialog(false)
                  setSelectedUser(null)
                  setNewPassword("")
                  setConfirmPassword("")
                  setPasswordChangeSuccess(false)
                  setGeneratedPassword("")
                }}
                className="w-full"
              >
                Close
              </Button>
            </div>
          ) : (
            <form onSubmit={(e) => { e.preventDefault(); handleSubmitPasswordChange(); }} className="space-y-4">
              <div className="space-y-2">
                <Label>New Password</Label>
                <div className="flex gap-2">
                  <Input
                    type="password"
                    placeholder="Enter new password or generate one"
                    value={newPassword}
                    onChange={(e) => setNewPassword(e.target.value)}
                    className="flex-1"
                    required
                    minLength={6}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={generateRandomPassword}
                    className="flex items-center gap-2"
                  >
                    <Key className="w-4 h-4" />
                    Generate
                  </Button>
                </div>
              </div>

              <div className="space-y-2">
                <Label>Confirm Password</Label>
                <Input
                  type="password"
                  placeholder="Confirm new password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={6}
                />
                {newPassword && confirmPassword && newPassword !== confirmPassword && (
                  <p className="text-xs text-error">Passwords do not match</p>
                )}
              </div>

              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="sendEmail"
                  checked={sendEmail}
                  onChange={(e) => setSendEmail(e.target.checked)}
                  className="w-4 h-4 rounded border-border"
                />
                <Label htmlFor="sendEmail" className="flex items-center gap-2 cursor-pointer">
                  <Send className="w-4 h-4" />
                  Send password to user via email
                </Label>
              </div>

              {!sendEmail && (
                <div className="p-3 bg-warning/10 border border-warning/30 rounded-lg">
                  <p className="text-xs text-warning">
                    ⚠️ The password will be shown here. Make sure to copy it and send it to the user securely.
                  </p>
                </div>
              )}

              <div className="flex gap-2">
                <Button
                  type="button"
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setShowChangePasswordDialog(false)
                    setSelectedUser(null)
                    setNewPassword("")
                    setConfirmPassword("")
                  }}
                  disabled={changingPassword}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  className="flex-1 bg-gradient-to-r from-teal-500 to-teal-600 hover:from-teal-600 hover:to-teal-700 text-white"
                  disabled={changingPassword || !newPassword || !confirmPassword || newPassword !== confirmPassword}
                >
                  {changingPassword ? (
                    <span className="flex items-center gap-2">
                      <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Changing...
                    </span>
                  ) : (
                    "Change Password"
                  )}
                </Button>
              </div>
            </form>
          )}
        </DialogContent>
      </Dialog>
      </div>
    </ProtectedPage>
  )
}
