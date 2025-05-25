import { forwardRef } from "react"

export const ScrollAnchor = forwardRef<HTMLDivElement>((props, ref) => {
  return (
    <div ref={ref} className="shrink-0 min-w-[24px] min-h-[24px]" {...props} />
  )
})

ScrollAnchor.displayName = "ScrollAnchor"
