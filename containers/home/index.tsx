import { FileUploadFeature } from "@/features/file-upload/file-upload-feature"

export function HomePageContainer() {
  return (
    <div className="flex items-center justify-center w-full px-4">
      <FileUploadFeature />
    </div>
  )
}
