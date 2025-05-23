import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { forwardRef } from "react";

interface MetalButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "outline";
  size?: "sm" | "md" | "lg";
  children: React.ReactNode;
}

export const MetalButton = forwardRef<HTMLButtonElement, MetalButtonProps>(
  ({ variant = "primary", size = "md", className, children, ...props }, ref) => {
    const variants = {
      primary: "bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-700 hover:to-orange-700 text-white font-bold skull-shadow",
      secondary: "bg-gradient-to-r from-orange-600 to-yellow-600 hover:from-orange-700 hover:to-yellow-700 text-black font-black skull-shadow distorted-hover",
      outline: "border-red-500 text-red-300 hover:bg-red-950 hover:text-red-200 font-bold skull-shadow"
    };

    const sizes = {
      sm: "py-2 px-4 text-sm",
      md: "py-3 px-6 text-base",
      lg: "py-3 px-8 text-lg"
    };

    return (
      <Button
        ref={ref}
        className={cn(
          variants[variant],
          sizes[size],
          className
        )}
        {...props}
      >
        {children}
      </Button>
    );
  }
);

MetalButton.displayName = "MetalButton";