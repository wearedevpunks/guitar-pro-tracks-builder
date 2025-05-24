import { MetalChatContainer } from "@/components/ui/metal/metal-chat-container";
import { MetalForm } from "@/components/ui/metal/metal-form";
import { ChatFeature } from "@/features/chat/chat-feature";

export function TrackPageContainer() {
  return (
    <MetalChatContainer>
      <ChatFeature />
    </MetalChatContainer>
  );
}