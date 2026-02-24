import { ReactNode, useState } from "react";
import { ChevronDown } from "lucide-react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

interface CollapsibleFilterSectionProps {
  title: string;
  icon?: ReactNode;
  children: ReactNode;
  defaultOpen?: boolean;
}

export function CollapsibleFilterSection({
  title,
  icon,
  children,
  defaultOpen = true,
}: CollapsibleFilterSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <Collapsible open={open} onOpenChange={setOpen}>
      <CollapsibleTrigger className="group mb-1 flex w-full items-center justify-between">
        <span className="flex items-center gap-2 text-xs font-bold uppercase tracking-widest text-foreground transition-colors group-hover:text-foreground">
          {icon}
          {title}
        </span>
        <ChevronDown
          className={cn(
            "h-3.5 w-3.5 text-foreground transition-transform duration-200",
            open && "rotate-180",
          )}
        />
      </CollapsibleTrigger>
      <CollapsibleContent className="flex flex-col gap-0.5">
        {children}
      </CollapsibleContent>
    </Collapsible>
  );
}
