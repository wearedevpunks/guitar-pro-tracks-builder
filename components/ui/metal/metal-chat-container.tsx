import { cn } from "@/lib/utils";

interface MetalChatContainerProps {
  children: React.ReactNode;
  className?: string;
}

export function MetalChatContainer({ children, className }: MetalChatContainerProps) {
  return (
    <div className={cn(
      "flex flex-col min-w-0 h-[calc(100dvh-52px)] bg-gradient-to-b from-black via-red-950/5 to-black",
      className
    )}>
      {children}
    </div>
  );
}