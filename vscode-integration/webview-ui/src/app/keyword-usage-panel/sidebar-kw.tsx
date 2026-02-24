import {
  FileText,
  Bot,
  Tag,
  Globe,
  LibraryBig,
  MousePointerClick,
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectLabel,
  SelectSeparator,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { CollapsibleFilterSection } from "@/components/panel-section/collapsible-filter-section";
import { FilterButton } from "@/components/sidebar/filter-button";
import { FileSelect } from "@/types/files";
import { FilterItem } from "@/types/keywords";

interface SidebarKeywordUsageProps {
  allFiles: FileSelect[];
  selectedFilePath: string | null;
  onFileChange: (file: FileSelect | null) => void;
  typeFilters: FilterItem[];
  globalFilters: FilterItem[];
  currentFilter: string;
  onFilterChange: (filterId: string) => void;
}

export function SidebarKeywordUsage({
  allFiles,
  selectedFilePath,
  onFileChange,
  typeFilters,
  globalFilters,
  currentFilter,
  onFilterChange,
}: SidebarKeywordUsageProps) {
  const robotFiles = allFiles.filter((file) =>
    file.file_name.toLowerCase().endsWith(".robot"),
  );
  const resourceFiles = allFiles.filter((file) =>
    file.file_name.toLowerCase().endsWith(".resource"),
  );

  const handleFileSelect = (filePath: string) => {
    const selected = allFiles.find((file) => file.path === filePath) ?? null;
    onFileChange(selected);
  };

  return (
    <div className="flex flex-col gap-5 p-3 h-full bg-background">
      <div className="flex flex-col gap-3">
        <span className="text-xs font-bold tracking-widest uppercase text-foreground">
          <MousePointerClick className="w-4 h-4 inline-block mr-1 text-orange-400" />
          File Selection
        </span>
        <Select
          value={selectedFilePath ?? undefined}
          onValueChange={handleFileSelect}
        >
          <SelectTrigger className="h-9 text-sm bg-input border-border w-full">
            <SelectValue
              placeholder={
                <span className="flex items-center gap-2 text-foreground">
                  <FileText className="w-4 h-4 shrink-0" />
                  Select a file
                </span>
              }
            />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectLabel>Resource Files</SelectLabel>
              {resourceFiles.map((file) => (
                <SelectItem key={file.path} value={file.path}>
                  <span className="flex items-center gap-2">
                    <LibraryBig className="w-4 h-4 text-orange-400" />
                    {file.file_name}
                  </span>
                </SelectItem>
              ))}
            </SelectGroup>

            <SelectSeparator />

            <SelectGroup>
              <SelectLabel>Robot Files</SelectLabel>
              {robotFiles.map((file) => (
                <SelectItem key={file.path} value={file.path}>
                  <span className="flex items-center gap-2">
                    <Bot className="w-4 h-4 text-primary" />
                    {file.file_name}
                  </span>
                </SelectItem>
              ))}
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      <CollapsibleFilterSection
        title="Type Filter"
        icon={<Tag className="w-3.5 h-3.5 text-emerald-400" />}
        defaultOpen={true}
      >
        {typeFilters.map(({ id, label, count }) => (
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
        title="Global Filter"
        icon={<Globe className="w-3.5 h-3.5 text-blue-400" />}
        defaultOpen={true}
      >
        {globalFilters.map(({ id, label, count }) => (
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
