import { ScrollArea } from "@/components/ui/scroll-area";
import MessageBubble, { ChatMessage } from "./MessageBubble";

interface ChatWindowProps {
  messages: ChatMessage[];
  onExplain?: (messageId: string) => void;
}

const ChatWindow = ({ messages, onExplain }: ChatWindowProps) => {
  return (
    <article aria-label="Conversation" className="h-full">
      <ScrollArea className="h-full pr-4">
        <div className="space-y-3">
          {messages.map((m) => (
            <MessageBubble key={m.id} message={m} onExplain={onExplain} />
          ))}
        </div>
      </ScrollArea>
    </article>
  );
};

export default ChatWindow;
