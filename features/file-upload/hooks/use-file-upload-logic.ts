import { useRouter } from "next/navigation"
import { useFileUploadStore } from "@/stores/file-upload-store"

export function useFileUploadLogic() {
  const router = useRouter()
  const { uploadedFile } = useFileUploadStore()

  const handleFileSelect = (file: File) => {
    localStorage.setItem("uploadedFileName", file.name)
  }

  const handleContinue = () => {
    router.push("/track")
  }

  const handleStartWithoutFile = () => {
    router.push("/track")
  }

  return {
    uploadedFile,
    handleFileSelect,
    handleContinue,
    handleStartWithoutFile,
  }
}
