import { client } from "./api/client.gen"

export const initBackendClient = () => {
  client.setConfig({
    baseUrl: "/api",
  })
}
