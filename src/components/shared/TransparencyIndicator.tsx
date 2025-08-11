import { ShieldCheck } from "lucide-react";

const TransparencyIndicator = () => {
  return (
    <div className="inline-flex items-center gap-2 rounded-md border border-border bg-card px-2 py-1 text-xs text-muted-foreground">
      <ShieldCheck className="h-4 w-4 text-accent" />
      Transparent AI
    </div>
  );
};

export default TransparencyIndicator;
