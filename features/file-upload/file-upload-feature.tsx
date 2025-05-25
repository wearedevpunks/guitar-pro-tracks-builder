"use client"

import { useFileUploadLogic } from "./hooks/use-file-upload-logic"
import { FileDropZone } from "./components/file-drop-zone"

export function FileUploadFeature() {
  const { uploadedFile, isUploading, handleFileSelect, handleContinue } =
    useFileUploadLogic()

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full max-w-[400px] mx-auto space-y-6 my-6">
      <FileDropZone onFileSelect={handleFileSelect} />

      {uploadedFile && (
        <button
          onClick={handleContinue}
          disabled={isUploading}
          className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isUploading ? "Uploading..." : "Continue with file"}
        </button>
      )}
    </div>
  )
}
