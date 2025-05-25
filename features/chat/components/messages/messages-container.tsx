import { forwardRef } from "react"
import { cn } from "@/lib/utils"

interface MessagesContainerProps {
  children: React.ReactNode
  className?: string
}

export const MessagesContainer = forwardRef<
  HTMLDivElement,
  MessagesContainerProps
>(({ children, className }, ref) => {
  return (
    <div
      ref={ref}
      className={cn(
        "flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll pt-4",
        className
      )}
    >
      {children}
    </div>
  )
})

MessagesContainer.displayName = "MessagesContainer"
