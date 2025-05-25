import { Message } from "ai"
import { MultimodalInput } from "@/components/multimodal-input"
import { MetalForm } from "@/components/ui/metal/metal-form"

interface ChatInputAreaProps {
  chatId: string
  input: string
  setInput: (input: string) => void
  handleSubmit: (e: React.FormEvent<HTMLFormElement>) => void
  isLoading: boolean
  stop: () => void
  messages: Message[]
  setMessages: (messages: Message[]) => void
  append: (message: any) => void
}

export function ChatInputArea(props: ChatInputAreaProps) {
  return (
    <MetalForm>
      <MultimodalInput {...props} />
    </MetalForm>
  )
}
