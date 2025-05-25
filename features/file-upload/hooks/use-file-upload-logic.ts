import { useState } from "react"
import { useRouter } from "next/navigation"
import { useFileUploadStore } from "@/stores/file-upload-store"
import { createNewSongSongsNewPost, type CreateSongResponse, apiClient } from "@/integrations/backend"

export function useFileUploadLogic() {
  const router = useRouter()
  const { uploadedFile } = useFileUploadStore()
  const [isUploading, setIsUploading] = useState(false)

  const handleFileSelect = async (file: File) => {
    localStorage.setItem("uploadedFileName", file.name)
  }

  const uploadFile = async (file: File): Promise<CreateSongResponse> => {
    const response = await createNewSongSongsNewPost({
      body: { file },
      client: apiClient
    })

    if (!response.data) {
      throw new Error(`Upload failed`)
    }

    return response.data
  }

  const handleContinue = async () => {
    if (!uploadedFile) return

    setIsUploading(true)
    try {
      const result = await uploadFile(uploadedFile)
      
      if (result.success && result.song_id) {
        // Store song info for the track page
        localStorage.setItem("currentSongId", result.song_id)
        localStorage.setItem("currentTabId", result.tab_id || "")
        router.push("/track")
      } else {
        console.error("Upload failed:", result.message)
        // Handle error - could show toast notification
      }
    } catch (error) {
      console.error("Upload error:", error)
      // Handle error - could show toast notification
    } finally {
      setIsUploading(false)
    }
  }

  const handleStartWithoutFile = () => {
    router.push("/track")
  }

  return {
    uploadedFile,
    isUploading,
    handleFileSelect,
    handleContinue,
    handleStartWithoutFile,
  }
}
