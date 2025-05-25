import { Message } from "ai"
import { PreviewMessage, ThinkingMessage } from "@/components/message"

interface MessagesListProps {
  messages: Message[]
  chatId: string
  isLoading: boolean
}

export function MessagesList({
  messages,
  chatId,
  isLoading,
}: MessagesListProps) {
  const showThinking =
    isLoading &&
    messages.length > 0 &&
    messages[messages.length - 1].role === "user"

  return (
    <>
      {messages.map((message, index) => (
        <PreviewMessage
          key={message.id}
          chatId={chatId}
          message={message}
          isLoading={isLoading && messages.length - 1 === index}
        />
      ))}

      {showThinking && <ThinkingMessage />}
    </>
  )
}
