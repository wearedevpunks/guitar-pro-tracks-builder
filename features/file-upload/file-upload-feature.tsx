"use client"

import { useFileUploadLogic } from "./hooks/use-file-upload-logic"
import { FileDropZone } from "./components/file-drop-zone"

export function FileUploadFeature() {
  const { uploadedFile, handleFileSelect, handleContinue } =
    useFileUploadLogic()

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full max-w-2xl mx-auto space-y-6">
      <FileDropZone onFileSelect={handleFileSelect} />

      <div className="space-y-4">
        <div>
          <p className="text-lg font-medium text-gray-900">
            Drop your Guitar Pro file here
          </p>
          <p className="text-sm text-gray-500 mt-1">or click to browse files</p>
          <p className="text-xs text-gray-400 mt-2">
            Supports .gp, .gpx, .gp5, .gp4 files
          </p>
        </div>
      </div>

      {uploadedFile && (
        <button
          onClick={handleContinue}
          className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Continue with file
        </button>
      )}
    </div>
  )
}
