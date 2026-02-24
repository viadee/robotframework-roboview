import { useEffect, useMemo, useState } from "react";
import { PanelRightClose, PanelRightOpen } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useUsageLayoutControls } from "@/components/layout/layout";
import { cn } from "@/lib/utils";
import { RobocopMessage } from "@/types/robocop";
import {
  filterMessagesBySearch,
  filterMessagesByType,
  sortRobocopMessages,
} from "@/utilities/robocop_utils";
import { vscode } from "@/utilities/vscode";
import { TablePagination } from "@/components/main-content/table-pagination";
import { NoRobocopIssuesFound } from "./no-issues-found";

type SortOption =
  | "sort"
  | "name_asc"
  | "name_desc"
  | "severity_high"
  | "severity_low";
const PAGE_SIZE = 25;

interface MainContentRobocopProps {
  robocopMessages: RobocopMessage[];
  currentFilter: string;
  searchTerm: string;
  sortBy: string;
  selectedMessage: RobocopMessage | null;
  onSortChange: (sort: SortOption) => void;
  onSearchChange: (value: string) => void;
  onClearSearch: () => void;
  onMessageSelect: (message: RobocopMessage) => void;
}

function getSeverityBadgeClass(severity: string) {
  if (severity === "E") {
    return "bg-destructive text-primary-foreground";
  }

  if (severity === "W") {
    return "bg-chart-4 text-primary-foreground";
  }

  return "bg-chart-1 text-primary-foreground";
}

export function MainContentRobocop({
  robocopMessages,
  currentFilter,
  searchTerm,
  sortBy,
  selectedMessage,
  onSortChange,
  onSearchChange,
  onClearSearch,
  onMessageSelect,
}: MainContentRobocopProps) {
  const layoutControls = useUsageLayoutControls();
  const [currentPage, setCurrentPage] = useState(1);

  const messagesToShow = useMemo(() => {
    const filteredByType = filterMessagesByType(robocopMessages, currentFilter);
    const filteredBySearch = filterMessagesBySearch(filteredByType, searchTerm);

    return sortRobocopMessages(filteredBySearch, sortBy);
  }, [currentFilter, robocopMessages, searchTerm, sortBy]);

  useEffect(() => {
    setCurrentPage(1);
  }, [currentFilter, searchTerm, sortBy, robocopMessages]);

  const totalPages = Math.max(1, Math.ceil(messagesToShow.length / PAGE_SIZE));
  const pageStartIndex = (currentPage - 1) * PAGE_SIZE;
  const paginatedMessages = messagesToShow.slice(
    pageStartIndex,
    pageStartIndex + PAGE_SIZE,
  );

  const handleSourceClick = (event: React.MouseEvent, filePath: string) => {
    if (event.ctrlKey || event.metaKey) {
      event.stopPropagation();
      vscode.postMessage({ command: "openFile", filePath });
    }
  };

  return (
    <div className="flex h-full flex-col gap-4 p-4">
      <div className="flex w-full items-center gap-3">
        <Select
          value={sortBy}
          onValueChange={(value) => onSortChange(value as SortOption)}
        >
          <SelectTrigger className="h-9 w-56 bg-input text-sm border-border">
            <SelectValue placeholder="Sort: Default" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="sort">Sort: Default</SelectItem>
            <SelectItem value="name_asc">Sort: Name (A-Z)</SelectItem>
            <SelectItem value="name_desc">Sort: Name (Z-A)</SelectItem>
            <SelectItem value="severity_high">
              Sort: Severity (High-Low)
            </SelectItem>
            <SelectItem value="severity_low">
              Sort: Severity (Low-High)
            </SelectItem>
          </SelectContent>
        </Select>

        <Input
          placeholder="Search Messages..."
          value={searchTerm}
          onChange={(event) => onSearchChange(event.target.value)}
          className="h-9 flex-1 bg-input text-sm border-border"
        />

        <Button variant="default" size="default" onClick={onClearSearch}>
          Clear
        </Button>

        {layoutControls && (
          <Button
            variant="outline"
            size="icon"
            className="h-10 w-10"
            onClick={layoutControls.toggleDetails}
            aria-label={
              layoutControls.isDetailsCollapsed
                ? "Open details panel"
                : "Close details panel"
            }
            title={
              layoutControls.isDetailsCollapsed
                ? "Open details panel"
                : "Close details panel"
            }
          >
            {layoutControls.isDetailsCollapsed ? (
              <PanelRightOpen className="size-6" />
            ) : (
              <PanelRightClose className="size-6" />
            )}
          </Button>
        )}
      </div>

      <div className="flex-1 overflow-auto rounded-md border border-border">
        {messagesToShow.length === 0 ? (
          <NoRobocopIssuesFound />
        ) : (
          <Table className="w-full table-fixed border-collapse">
            <TableHeader className="sticky top-0 z-10 bg-background">
              <TableRow className="border-b border-border">
                <TableHead className="w-[16%] px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-foreground">
                  Rule ID
                </TableHead>
                <TableHead className="w-[40%] px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-foreground">
                  Message
                </TableHead>
                <TableHead className="w-[28%] px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-foreground">
                  Source
                </TableHead>
                <TableHead className="w-[16%] px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-foreground">
                  Severity
                </TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {paginatedMessages.map((messageData) => {
                const isSelected =
                  selectedMessage?.message_id === messageData.message_id;

                return (
                  <TableRow
                    key={messageData.message_id}
                    onClick={() => onMessageSelect(messageData)}
                    className={cn(
                      "cursor-pointer border-b border-border/60 transition-colors hover:bg-accent/40",
                      isSelected && "bg-accent",
                    )}
                  >
                    <TableCell className="px-4 py-3 text-sm">
                      <div className="flex min-w-0 items-center gap-2">
                        <Badge
                          className={cn(
                            "h-6 rounded-sm px-2 text-xs font-bold",
                            getSeverityBadgeClass(messageData.severity),
                          )}
                        >
                          {messageData.severity}
                        </Badge>
                        <span
                          className="block truncate"
                          title={messageData.rule_id}
                        >
                          {messageData.rule_id}
                        </span>
                      </div>
                    </TableCell>

                    <TableCell className="px-4 py-3 text-sm">
                      <span
                        className="block truncate"
                        title={messageData.message}
                      >
                        {messageData.message}
                      </span>
                    </TableCell>

                    <TableCell
                      className="px-4 py-3 text-sm"
                      onClick={(event) =>
                        handleSourceClick(event, messageData.source)
                      }
                      title={messageData.source}
                    >
                      <span className="cursor-pointer text-primary hover:underline">
                        {messageData.file_name}
                      </span>
                    </TableCell>

                    <TableCell className="px-4 py-3 text-center text-sm">
                      {messageData.severity}
                    </TableCell>
                  </TableRow>
                );
              })}
            </TableBody>
          </Table>
        )}
      </div>

      {messagesToShow.length > 0 && (
        <TablePagination
          currentPage={currentPage}
          totalPages={totalPages}
          onPageChange={setCurrentPage}
        />
      )}
    </div>
  );
}
