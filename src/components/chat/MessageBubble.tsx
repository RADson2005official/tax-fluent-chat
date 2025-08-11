import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Lightbulb } from "lucide-react";
import { ReactNode } from "react";

export type ChatMessage = {
  id: string;
  role: "user" | "ai";
  content: ReactNode;
  explainable?: boolean;
};

interface MessageBubbleProps {
  message: ChatMessage;
  onExplain?: (id: string) => void;
}

const MessageBubble = ({ message, onExplain }: MessageBubbleProps) => {
  const isUser = message.role === "user";
  return (
    <div className={cn("flex w-full", isUser ? "justify-end" : "justify-start")}> 
      <Card
        className={cn(
          "max-w-[85%] md:max-w-[70%] px-4 py-3 border transition-shadow",
          isUser
            ? "bg-primary text-primary-foreground shadow-sm"
            : "bg-muted text-foreground"
        )}
      >
        <div className="text-sm leading-relaxed">{message.content}</div>
        {message.explainable && !isUser && (
          <div className="mt-2 flex justify-end">
            <Button size="sm" variant="glow" onClick={() => onExplain?.(message.id)}>
              <Lightbulb className="mr-2" /> Explain
            </Button>
          </div>
        )}
      </Card>
    </div>
  );
};

export default MessageBubble;
