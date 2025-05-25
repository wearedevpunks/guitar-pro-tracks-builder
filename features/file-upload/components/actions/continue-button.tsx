import { MetalButton } from "@/components/ui/metal/metal-button"

interface ContinueButtonProps {
  onContinue: () => void
  disabled?: boolean
}

export function ContinueButton({ onContinue, disabled }: ContinueButtonProps) {
  return (
    <div className="mt-6 text-center">
      <MetalButton
        variant="primary"
        size="lg"
        onClick={onContinue}
        disabled={disabled}
        className="w-full"
      >
        🔥 UNLEASH THE FURY 🔥
      </MetalButton>
    </div>
  )
}
