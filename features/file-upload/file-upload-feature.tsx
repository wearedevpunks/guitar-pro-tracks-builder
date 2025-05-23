import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { useFileUploadStore } from "@/stores/file-upload-store";
import { FileDropZone } from "./components/file-drop-zone";
import { MetalButton } from "@/components/ui/metal/metal-button";

export function FileUploadFeature() {
  const router = useRouter();
  const { uploadedFile } = useFileUploadStore();

  const handleFileSelect = (file: File) => {
    localStorage.setItem('uploadedFileName', file.name);
  };

  const handleContinue = () => {
    router.push('/track');
  };

  const handleStartWithoutFile = () => {
    router.push('/track');
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.2, duration: 0.8 }}
      className="w-full max-w-lg relative z-10"
    >
      <FileDropZone onFileSelect={handleFileSelect} />

      {uploadedFile && (
        <div className="mt-6 text-center">
          <MetalButton
            variant="primary"
            size="lg"
            onClick={handleContinue}
            className="w-full"
          >
            🔥 UNLEASH THE FURY 🔥
          </MetalButton>
        </div>
      )}

      <div className="mt-8 text-center">
        <p className="text-sm text-orange-300 mb-4 font-bold">
          ⚡ OR FORGE FROM THE FLAMES ⚡
        </p>
        <MetalButton 
          variant="secondary"
          size="lg"
          onClick={handleStartWithoutFile}
        >
          🏗️ BUILD FROM SCRATCH 🏗️
        </MetalButton>
      </div>
    </motion.div>
  );
}