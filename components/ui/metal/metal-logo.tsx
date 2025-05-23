import { motion } from "framer-motion";
import { Guitar, Skull, Zap } from "lucide-react";

interface MetalLogoProps {
  size?: "sm" | "md" | "lg";
  delay?: number;
}

export function MetalLogo({ size = "lg", delay = 0.3 }: MetalLogoProps) {
  const sizeClasses = {
    sm: "w-12 h-12",
    md: "w-16 h-16", 
    lg: "w-20 h-20"
  };

  const iconSizes = {
    sm: { skull: "w-6 h-6", zap: "w-4 h-4" },
    md: { skull: "w-8 h-8", zap: "w-6 h-6" },
    lg: { skull: "w-10 h-10", zap: "w-8 h-8" }
  };

  return (
    <motion.div
      initial={{ scale: 0.5, rotate: -10 }}
      animate={{ scale: 1, rotate: 0 }}
      transition={{ delay, duration: 0.8, type: "spring", bounce: 0.4 }}
      className="flex items-center justify-center"
    >
      <div className="relative flame-glow">
        <Guitar className={`${sizeClasses[size]} text-red-500 distorted-hover`} />
        <Skull className={`${iconSizes[size].skull} text-orange-500 absolute -top-3 -right-3 animate-pulse`} />
        <Zap className={`${iconSizes[size].zap} text-yellow-400 absolute -bottom-2 -left-2 animate-bounce`} />
      </div>
    </motion.div>
  );
}