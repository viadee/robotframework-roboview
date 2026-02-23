import { Shield, Tag } from "lucide-react";
import { Separator } from "@/components/ui/separator";
import { CollapsibleFilterSection } from "@/app/shared/collapsible-filter-section";
import { FilterButton } from "@/app/shared/filter-button";
import { FilterItem } from "@/types/keywords";

interface SidebarRobocopProps {
  categoryFilters: FilterItem[];
  severityFilters: FilterItem[];
  currentFilter: string;
  onFilterChange: (filterId: string) => void;
}

export function SidebarRobocop({
  categoryFilters,
  severityFilters,
  currentFilter,
  onFilterChange,
}: SidebarRobocopProps) {
  return (
    <div className="flex h-full flex-col gap-5 bg-background p-3">
      <CollapsibleFilterSection
        title="Category Filter"
        icon={<Tag className="h-3.5 w-3.5 text-emerald-400" />}
        defaultOpen
      >
        {categoryFilters.map(({ id, label, count }) => (
          <FilterButton
            key={id}
            id={id}
            label={label}
            count={count}
            isActive={currentFilter === id}
            onClick={onFilterChange}
          />
        ))}
      </CollapsibleFilterSection>

      <Separator />

      <CollapsibleFilterSection
        title="Severity Filter"
        icon={<Shield className="h-3.5 w-3.5 text-orange-400" />}
        defaultOpen
      >
        {severityFilters.map(({ id, label, count }) => (
          <FilterButton
            key={id}
            id={id}
            label={label}
            count={count}
            isActive={currentFilter === id}
            onClick={onFilterChange}
          />
        ))}
      </CollapsibleFilterSection>
    </div>
  );
}
