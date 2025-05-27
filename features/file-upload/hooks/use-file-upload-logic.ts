import { useRouter } from "next/navigation"
import { toast } from "sonner"
import { useMutation } from "@tanstack/react-query"
import { useFileUploadStore } from "@/stores/file-upload-store"
import { songCreate, SongGetResponse } from "@/integrations/backend/api"

export function useFileUploadLogic() {
  const router = useRouter()
  const { uploadedFile } = useFileUploadStore()

  const uploadMutation = useMutation({
    mutationFn: async (file: File): Promise<SongGetResponse> => {
      const response = await songCreate({
        body: { file },
      })

      if (!response.data) {
        throw new Error(`Upload failed`)
      }

      return response.data
    },
    onSuccess: (result) => {
      if (result.success && result.song_id) {
        toast.success("Song uploaded successfully!")
        router.push(`/song/${result.song_id}`)
      } else {
        toast.error(result.message || "Upload failed. Please try again.")
      }
    },
    onError: (error) => {
      console.error("Upload error:", error)
      toast.error("Upload failed. Please check your file and try again.")
    },
  })

  const handleFileSelect = async (file: File) => {
    localStorage.setItem("uploadedFileName", file.name)
  }

  const handleContinue = () => {
    if (!uploadedFile) return
    uploadMutation.mutate(uploadedFile)
  }

  return {
    uploadedFile,
    isUploading: uploadMutation.isPending,
    handleFileSelect,
    handleContinue,
  }
}
