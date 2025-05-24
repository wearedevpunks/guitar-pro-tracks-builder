import { cn } from "@/lib/utils";

interface MetalFormProps {
  children: React.ReactNode;
  className?: string;
  onSubmit?: (e: React.FormEvent) => void;
}

export function MetalForm({ children, className, onSubmit }: MetalFormProps) {
  return (
    <form 
      className={cn(
        "flex mx-auto px-4 bg-gradient-to-r from-black via-red-950/10 to-black pb-4 md:pb-6 gap-2 w-full md:max-w-3xl border-t border-red-900/30",
        className
      )}
      onSubmit={onSubmit}
    >
      {children}
    </form>
  );
}