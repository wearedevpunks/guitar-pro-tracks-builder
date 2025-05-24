import { useFileUploadLogic } from "./hooks/use-file-upload-logic";
import { FileDropZone } from "./components/file-drop-zone";

export function FileUploadFeature() {
  const {
    uploadedFile,
    handleFileSelect,
    handleContinue,
    handleStartWithoutFile,
  } = useFileUploadLogic();

  return (
    <div className="w-full max-w-lg space-y-4">
      <FileDropZone onFileSelect={handleFileSelect} />

      {uploadedFile && (
        <button
          onClick={handleContinue}
          className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Continue with file
        </button>
      )}

      <button
        onClick={handleStartWithoutFile}
        className="w-full px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
      >
        Start without file
      </button>
    </div>
  );
}