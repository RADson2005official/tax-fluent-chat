import { useState, useRef, KeyboardEvent } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { Mic, Send, Paperclip } from "lucide-react";
import { cn } from "@/lib/utils";

interface InputBarProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  suggestions?: string[];
  mode?: "Novice" | "Expert" | "Accessibility";
}

const InputBar = ({ onSend, disabled, suggestions = [], mode = "Novice" }: InputBarProps) => {
  const [value, setValue] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    const v = value.trim();
    if (!v) return;
    onSend(v);
    setValue("");
  };

  const onKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full">
      <div className="flex items-center gap-2">
        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="soft" size="icon" aria-label="Attach file">
                <Paperclip />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Attach documents</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <Input
          ref={inputRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder={
            mode === "Novice"
              ? "Ask in plain language: e.g., Do I qualify for the child tax credit?"
              : mode === "Expert"
              ? "Type commands or forms: e.g., compute itemized deduction with SALT cap"
              : "Write or dictate your question"
          }
          className="flex-1"
        />

        <TooltipProvider>
          <Tooltip>
            <TooltipTrigger asChild>
              <Button variant="soft" size="icon" aria-label="Voice input (coming soon)" disabled>
                <Mic />
              </Button>
            </TooltipTrigger>
            <TooltipContent>Voice input coming soon</TooltipContent>
          </Tooltip>
        </TooltipProvider>

        <Button variant="hero" onClick={handleSend} disabled={disabled} aria-label="Send message">
          <Send className="mr-2" /> Send
        </Button>
      </div>

      {suggestions.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-2">
          {suggestions.map((s) => (
            <Button key={s} size="sm" variant="soft" onClick={() => { setValue(s); onSend(s); }}>
              {s}
            </Button>
          ))}
        </div>
      )}
    </div>
  );
};

export default InputBar;
