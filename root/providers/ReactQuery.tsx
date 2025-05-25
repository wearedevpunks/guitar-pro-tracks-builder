"use client"

import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Default query timeout
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
    mutations: {
      // Default mutation timeout - 10 minutes for long operations like video export
      networkMode: 'online',
    },
  },
})

export const ReactQueryProvider = ({
  children,
}: {
  children: React.ReactNode
}) => {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  )
}
