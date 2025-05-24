import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface FileUploadContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function FileUploadContainer({ children, className }: FileUploadContainerProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.2, duration: 0.8 }}
      className={cn("w-full max-w-lg relative z-10", className)}
    >
      {children}
    </motion.div>
  );
}