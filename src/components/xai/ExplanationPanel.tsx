import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { ScrollArea } from "@/components/ui/scroll-area";

interface ExplanationPanelProps {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  content: string;
}

const ExplanationPanel = ({ open, onOpenChange, content }: ExplanationPanelProps) => {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle>Why the AI said that</DialogTitle>
        </DialogHeader>
        <ScrollArea className="max-h-[60vh] pr-4">
          <div className="prose prose-sm dark:prose-invert">
            <p>{content}</p>
            <ul>
              <li>Attribution to your inputs</li>
              <li>Referenced rules and thresholds</li>
              <li>Confidence and alternatives</li>
            </ul>
          </div>
        </ScrollArea>
      </DialogContent>
    </Dialog>
  );
};

export default ExplanationPanel;
