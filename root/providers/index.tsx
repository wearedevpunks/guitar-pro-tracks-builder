import { initBackendClient } from "@/integrations/backend"
import { BackendProvider } from "./BackendProvider"
import { ReactQueryProvider } from "./ReactQuery"

initBackendClient()

export const RootProvider = ({ children }: { children: React.ReactNode }) => {
  return (
    <ReactQueryProvider>
      <BackendProvider>{children}</BackendProvider>
    </ReactQueryProvider>
  )
}
