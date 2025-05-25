import { Message } from "ai"
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom"
import { MetalOverview } from "./metal-overview"
import { MessagesContainer } from "./messages/messages-container"
import { MessagesList } from "./messages/messages-list"
import { ScrollAnchor } from "./messages/scroll-anchor"

interface MessagesAreaProps {
  messages: Message[]
  chatId: string
  isLoading: boolean
}

export function MessagesArea({
  messages,
  chatId,
  isLoading,
}: MessagesAreaProps) {
  const [messagesContainerRef, messagesEndRef] =
    useScrollToBottom<HTMLDivElement>()

  return (
    <MessagesContainer ref={messagesContainerRef}>
      {messages.length === 0 && <MetalOverview />}

      <MessagesList messages={messages} chatId={chatId} isLoading={isLoading} />

      <ScrollAnchor ref={messagesEndRef} />
    </MessagesContainer>
  )
}
