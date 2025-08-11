import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Label } from "@/components/ui/label";

export type Mode = "Novice" | "Expert" | "Accessibility";

interface ModeSwitcherProps {
  mode: Mode;
  onChange: (mode: Mode) => void;
}

const ModeSwitcher = ({ mode, onChange }: ModeSwitcherProps) => {
  return (
    <div className="flex items-center gap-3">
      <Label htmlFor="mode">Mode</Label>
      <Select value={mode} onValueChange={(v) => onChange(v as Mode)}>
        <SelectTrigger id="mode" className="w-40">
          <SelectValue placeholder="Select mode" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="Novice">Novice</SelectItem>
          <SelectItem value="Expert">Expert</SelectItem>
          <SelectItem value="Accessibility">Accessibility-First</SelectItem>
        </SelectContent>
      </Select>
    </div>
  );
};

export default ModeSwitcher;
