import { useFileUploadStore } from "@/stores/file-upload-store";

interface FileDropZoneProps {
  onFileSelect: (file: File) => void;
}

export function FileDropZone({ onFileSelect }: FileDropZoneProps) {
  const { uploadedFile, setUploadedFile } = useFileUploadStore();

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      const file = files[0];
      if (file.name.endsWith('.gp') || file.name.endsWith('.gpx') || file.name.endsWith('.gp5') || file.name.endsWith('.gp4')) {
        setUploadedFile(file);
        onFileSelect(file);
      }
    }
  };

  return (
    <div className="space-y-4">
      <input
        type="file"
        accept=".gp,.gpx,.gp5,.gp4"
        onChange={handleFileInput}
        className="block w-full text-sm text-gray-500
          file:mr-4 file:py-2 file:px-4
          file:rounded-full file:border-0
          file:text-sm file:font-semibold
          file:bg-blue-50 file:text-blue-700
          hover:file:bg-blue-100"
      />
      
      {uploadedFile && (
        <div className="text-green-600 text-sm">
          ✓ {uploadedFile.name}
        </div>
      )}
    </div>
  );
}