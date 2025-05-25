"use client"

import { initBackendClient } from "@/integrations/backend"
import { useEffect } from "react"

export const BackendProvider = ({
  children,
}: {
  children: React.ReactNode
}) => {
  useEffect(() => {
    initBackendClient()
  }, [])

  return <>{children}</>
}
