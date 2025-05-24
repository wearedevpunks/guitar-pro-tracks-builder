import { create } from 'zustand';
import { Message } from 'ai';

interface ChatState {
  chatId: string;
  messages: Message[];
  input: string;
  isLoading: boolean;
  setMessages: (messages: Message[]) => void;
  setInput: (input: string) => void;
  setIsLoading: (isLoading: boolean) => void;
  addMessage: (message: Message) => void;
  clearChat: () => void;
}

export const useChatStore = create<ChatState>((set) => ({
  chatId: "001",
  messages: [],
  input: "",
  isLoading: false,
  setMessages: (messages) => set({ messages }),
  setInput: (input) => set({ input }),
  setIsLoading: (isLoading) => set({ isLoading }),
  addMessage: (message) => set((state) => ({ 
    messages: [...state.messages, message] 
  })),
  clearChat: () => set({ messages: [], input: "" }),
}));