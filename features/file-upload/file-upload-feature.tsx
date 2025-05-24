import { useFileUploadLogic } from "./hooks/use-file-upload-logic";
import { FileUploadContainer } from "./components/file-upload-container";
import { FileDropZone } from "./components/file-drop-zone";
import { ContinueButton } from "./components/actions/continue-button";
import { StartFromScratch } from "./components/actions/start-from-scratch";

export function FileUploadFeature() {
  const {
    uploadedFile,
    handleFileSelect,
    handleContinue,
    handleStartWithoutFile,
  } = useFileUploadLogic();

  return (
    <FileUploadContainer>
      <FileDropZone onFileSelect={handleFileSelect} />

      {uploadedFile && (
        <ContinueButton onContinue={handleContinue} />
      )}

      <StartFromScratch onStart={handleStartWithoutFile} />
    </FileUploadContainer>
  );
}