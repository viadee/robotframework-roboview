import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface FilterButtonProps {
  id: string;
  label: string;
  count: number;
  isActive: boolean;
  onClick: (id: string) => void;
}

export function FilterButton({
  id,
  label,
  count,
  isActive,
  onClick,
}: FilterButtonProps) {
  return (
    <button
      onClick={() => onClick(id)}
      className={cn(
        "flex w-full items-center justify-between rounded-md px-3 py-1.5 text-left text-sm transition-all duration-150",
        isActive
          ? "bg-primary text-primary-foreground shadow-sm"
          : "text-foreground hover:bg-accent hover:text-accent-foreground",
      )}
    >
      <span className="flex-1 pr-2 font-medium leading-snug">{label}</span>
      <Badge className="shrink-0 border-transparent bg-primary-foreground/20 text-destructive-foreground text-xs font-semibold">
        {count}
      </Badge>
    </button>
  );
}
