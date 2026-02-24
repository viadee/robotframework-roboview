import { useState } from "react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { ChevronDown, LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface CollapsibleSectionProps {
  title: string;
  icon: LucideIcon;
  iconOpen?: LucideIcon;
  iconColor?: string;
  defaultOpen?: boolean;
  children: React.ReactNode;
}

export function CollapsibleSection({
  title,
  icon: Icon,
  iconOpen: IconOpen,
  iconColor = "text-amber-400",
  defaultOpen = true,
  children,
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);
  const ActiveIcon = isOpen && IconOpen ? IconOpen : Icon;

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen}>
      <section className="space-y-3">
        <CollapsibleTrigger className="flex w-full items-center justify-between group">
          <div className="flex items-center gap-2">
            <ActiveIcon className={cn("w-5 h-5 shrink-0", iconColor)} />
            <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
          </div>
          <ChevronDown
            className={cn(
              "w-4 h-4 text-muted-foreground transition-transform duration-200",
              isOpen && "rotate-180",
            )}
          />
        </CollapsibleTrigger>

        <CollapsibleContent>{children}</CollapsibleContent>
      </section>
    </Collapsible>
  );
}
