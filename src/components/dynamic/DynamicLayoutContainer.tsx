import { ReactNode, useRef } from "react";
import { cn } from "@/lib/utils";

interface DynamicLayoutContainerProps {
  children: ReactNode;
  className?: string;
  interactiveGlow?: boolean;
}

const DynamicLayoutContainer = ({ children, className, interactiveGlow = true }: DynamicLayoutContainerProps) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const onMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!interactiveGlow) return;
    const el = containerRef.current;
    if (!el) return;
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    el.style.setProperty("--pointer-x", `${x}px`);
    el.style.setProperty("--pointer-y", `${y}px`);
  };

  return (
    <div
      ref={containerRef}
      onMouseMove={onMouseMove}
      className={cn(
        "relative",
        interactiveGlow && "before:pointer-events-none before:absolute before:inset-0 before:bg-[radial-gradient(600px_300px_at_var(--pointer-x,50%)_var(--pointer-y,0),hsl(var(--ring)/0.10),transparent_60%)]",
        className
      )}
    >
      {children}
    </div>
  );
};

export default DynamicLayoutContainer;
