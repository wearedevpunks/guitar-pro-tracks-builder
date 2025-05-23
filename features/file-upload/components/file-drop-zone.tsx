import { motion } from "framer-motion";
import { Upload, Flame } from "lucide-react";
import { useFileUploadStore } from "@/stores/file-upload-store";
import { MetalButton } from "@/components/ui/metal/metal-button";

interface FileDropZoneProps {
  onFileSelect: (file: File) => void;
}

export function FileDropZone({ onFileSelect }: FileDropZoneProps) {
  const { isDragging, uploadedFile, setIsDragging, setUploadedFile } = useFileUploadStore();

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.gp') || file.name.endsWith('.gpx') || file.name.endsWith('.gp5') || file.name.endsWith('.gp4')) {
        setUploadedFile(file);
        onFileSelect(file);
      }
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setUploadedFile(files[0]);
      onFileSelect(files[0]);
    }
  };

  return (
    <div
      className={`
        metal-border rounded-xl p-8 text-center transition-all duration-300 skull-shadow distorted-hover
        ${isDragging 
          ? 'border-red-500 bg-red-950/30 scale-105' 
          : 'hover:bg-red-950/10'
        }
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      <motion.div
        animate={{ rotate: isDragging ? 360 : 0 }}
        transition={{ duration: 0.5 }}
      >
        <Upload className="w-16 h-16 mx-auto mb-4 text-red-400 flame-glow" />
      </motion.div>
      
      {uploadedFile ? (
        <div className="space-y-4">
          <div className="text-orange-400 font-bold text-lg flex items-center justify-center gap-2">
            <Flame className="w-5 h-5" />
            ✓ {uploadedFile.name}
            <Flame className="w-5 h-5" />
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div>
            <h3 className="font-black text-xl mb-3 text-red-300">🎸 LOAD YOUR ARSENAL 🎸</h3>
            <p className="text-sm text-orange-200 font-medium">
              Drop your .gp, .gpx, .gp5, or .gp4 files into the pit!
            </p>
          </div>
          
          <input
            type="file"
            accept=".gp,.gpx,.gp5,.gp4"
            onChange={handleFileInput}
            className="hidden"
            id="file-input"
          />
          
          <MetalButton
            variant="outline"
            onClick={() => document.getElementById('file-input')?.click()}
            className="w-full"
          >
            🔥 CHOOSE YOUR WEAPON 🔥
          </MetalButton>
        </div>
      )}
    </div>
  );
}