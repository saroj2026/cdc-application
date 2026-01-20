"use client"

import { ProtectedPage } from "@/components/auth/ProtectedPage"

export default function ETLLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // ETL layout now uses the main application sidebar
  // No separate sidebar needed - all ETL menu items are in the main sidebar under OPERATIONS section
  return (
    <ProtectedPage>
      <div className="w-full">
        {children}
      </div>
    </ProtectedPage>
  )
}

