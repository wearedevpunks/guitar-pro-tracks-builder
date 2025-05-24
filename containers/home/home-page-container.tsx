import { MetalBackground } from "@/components/ui/metal/metal-background";
import { HeroSection } from "./components/hero-section";
import { FileUploadFeature } from "@/features/file-upload/file-upload-feature";

export function HomePageContainer() {
  return (
    <div className="flex flex-col items-center justify-center min-h-[calc(100vh-100px)] px-4 relative overflow-hidden">
      <MetalBackground />
      <HeroSection />
      <FileUploadFeature />
    </div>
  );
}