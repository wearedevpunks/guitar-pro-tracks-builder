import { useFileUploadStore } from "@/stores/file-upload-store"

interface FileDropZoneProps {
  onFileSelect: (file: File) => void
}

export function FileDropZone({ onFileSelect }: FileDropZoneProps) {
  const { uploadedFile, setUploadedFile } = useFileUploadStore()

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files
    if (files && files.length > 0) {
      const file = files[0]
      if (
        file.name.endsWith(".gp") ||
        file.name.endsWith(".gpx") ||
        file.name.endsWith(".gp5") ||
        file.name.endsWith(".gp4")
      ) {
        setUploadedFile(file)
        onFileSelect(file)
      }
    }
  }

  return (
    <div className="w-full">
      <div className="relative border-2 border-dashed border-gray-300 rounded-lg p-12 text-center hover:border-gray-400 transition-colors bg-gray-50/50">
        <div className="space-y-4 text-center">
          <div>
            <p className="text-lg font-medium text-gray-800">
              Drop your Guitar Pro file here
            </p>
            <p className="text-xs text-gray-600 mt-2">
              Supports .gp, .gpx, .gp5, .gp4 files
            </p>
          </div>
        </div>

        <input
          type="file"
          accept=".gp,.gpx,.gp5,.gp4"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
      </div>

      {uploadedFile && (
        <div className="mt-4 p-3 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center text-green-700">
            <svg
              className="w-5 h-5 mr-2"
              fill="currentColor"
              viewBox="0 0 20 20"
            >
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
            <span className="font-medium">{uploadedFile.name}</span>
          </div>
        </div>
      )}
    </div>
  )
}
