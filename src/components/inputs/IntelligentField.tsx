import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip";
import { useState } from "react";

interface IntelligentFieldProps {
  id: string;
  label: string;
  placeholder?: string;
  help?: string;
  type?: "text" | "number";
  required?: boolean;
  onValid?: (value: string | number) => void;
}

const IntelligentField = ({ id, label, placeholder, help, type = "text", required, onValid }: IntelligentFieldProps) => {
  const [value, setValue] = useState<string>("");
  const [error, setError] = useState<string>("");

  const validate = (v: string) => {
    if (required && !v) return `${label} is required.`;
    if (type === "number" && v && isNaN(Number(v))) return `${label} must be a number.`;
    return "";
  };

  return (
    <div className="space-y-1.5">
      <div className="flex items-center gap-2">
        <Label htmlFor={id}>{label}</Label>
        {help && (
          <TooltipProvider>
            <Tooltip>
              <TooltipTrigger asChild>
                <span className="text-muted-foreground text-xs underline decoration-dotted cursor-help">help</span>
              </TooltipTrigger>
              <TooltipContent className="max-w-xs">{help}</TooltipContent>
            </Tooltip>
          </TooltipProvider>
        )}
      </div>
      <Input
        id={id}
        placeholder={placeholder}
        inputMode={type === "number" ? "numeric" : undefined}
        value={value}
        onChange={(e) => {
          const v = e.target.value;
          setValue(v);
          const err = validate(v);
          setError(err);
          if (!err) onValid?.(type === "number" ? Number(v) : v);
        }}
        aria-invalid={!!error}
        aria-errormessage={error ? `${id}-error` : undefined}
      />
      {error && (
        <p id={`${id}-error`} className="text-xs text-destructive">
          {error}
        </p>
      )}
    </div>
  );
};

export default IntelligentField;
