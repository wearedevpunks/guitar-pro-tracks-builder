// Custom backend integration exports
export * from "./api"

// Re-export the configured client with proper base URL
import { createClient, createConfig } from "@hey-api/client-fetch"
import type { ClientOptions } from "./api/types.gen"

export const apiClient = createClient(
  createConfig<ClientOptions>({
    baseUrl: "/api",
  })
)
