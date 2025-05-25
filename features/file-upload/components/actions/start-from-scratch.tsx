import { MetalButton } from "@/components/ui/metal/metal-button"

interface StartFromScratchProps {
  onStart: () => void
}

export function StartFromScratch({ onStart }: StartFromScratchProps) {
  return (
    <div className="mt-8 text-center">
      <p className="text-sm text-orange-300 mb-4 font-bold">
        ⚡ OR FORGE FROM THE FLAMES ⚡
      </p>
      <MetalButton variant="secondary" size="lg" onClick={onStart}>
        🏗️ BUILD FROM SCRATCH 🏗️
      </MetalButton>
    </div>
  )
}
