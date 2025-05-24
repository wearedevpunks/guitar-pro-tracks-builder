import { useChat } from "ai/react";
import { toast } from "sonner";
import { useChatStore } from "@/stores/chat-store";
import { useEffect } from "react";

export function useChatLogic() {
  const { chatId, setMessages: setStoreMessages, setIsLoading: setStoreIsLoading } = useChatStore();

  const chatApi = useChat({
    maxSteps: 4,
    onError: (error) => {
      if (error.message.includes("Too many requests")) {
        toast.error(
          "🔥 Too many brutal requests! Cool down your axe and try again later. 🎸",
        );
      }
    },
  });

  // Sync with store
  useEffect(() => {
    setStoreMessages(chatApi.messages);
    setStoreIsLoading(chatApi.isLoading);
  }, [chatApi.messages, chatApi.isLoading, setStoreMessages, setStoreIsLoading]);

  return {
    chatId,
    ...chatApi,
  };
}