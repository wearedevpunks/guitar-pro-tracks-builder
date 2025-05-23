import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface MetalTitleProps {
  children: React.ReactNode;
  className?: string;
  delay?: number;
}

export function MetalTitle({ children, className, delay = 0.5 }: MetalTitleProps) {
  return (
    <motion.h1
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ delay, duration: 0.8 }}
      className={cn(
        "text-5xl md:text-7xl font-black metal-gradient bg-clip-text text-transparent mb-6 metal-text tracking-wider",
        className
      )}
      style={{ fontFamily: 'Impact, Arial Black, sans-serif' }}
    >
      {children}
    </motion.h1>
  );
}