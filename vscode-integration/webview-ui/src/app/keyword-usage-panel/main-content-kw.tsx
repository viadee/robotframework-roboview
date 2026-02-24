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
import { Keyword } from "@/types/keywords";
import {
  filterKeywordsBySearch,
  filterKeywordsByType,
} from "@/utilities/keyword_utils";
import { vscode } from "@/utilities/vscode";
import { TablePagination } from "@/app/shared/table-pagination";
import { NoFileSelected } from "./no-file-selected";
import { NoKeywordFound } from "./no-keywords-found";

type SortOption =
  | "default"
  | "name_asc"
  | "name_desc"
  | "file_usages_desc"
  | "total_usages_desc";
const PAGE_SIZE = 25;

interface MainContentKeywordUsageProps {
  initKeywords: Keyword[];
  calledKeywords: Keyword[];
  keywordsWithoutDoc: Keyword[];
  keywordsWithoutUsages: Keyword[];
  keywordDuplicates: Keyword[];
  currentFilter: string;
  fileSelected: boolean;
  selectedKeywordId: string | null;
  onKeywordSelect: (keyword: Keyword) => void;
}

function getUsageBadgeClass(totalUsages: number) {
  if (totalUsages === 0) {
    return "bg-destructive/30 text-foreground";
  }

  if (totalUsages <= 10) {
    return "bg-orange-400/30 text-foreground";
  }

  if (totalUsages <= 30) {
    return "bg-emerald-400/30 text-foreground";
  }

  return "bg-chart-1/20 text-foreground";
}

function isUserSource(source: string) {
  const normalizedSource = source.toLowerCase();
  return (
    normalizedSource.endsWith(".robot") ||
    normalizedSource.endsWith(".resource") ||
    normalizedSource.includes("/") ||
    normalizedSource.includes("\\")
  );
}

export function MainContentKeywordUsage({
  initKeywords,
  calledKeywords,
  keywordsWithoutDoc,
  keywordsWithoutUsages,
  keywordDuplicates,
  currentFilter,
  fileSelected,
  selectedKeywordId,
  onKeywordSelect,
}: MainContentKeywordUsageProps) {
  const layoutControls = useUsageLayoutControls();
  const [sortBy, setSortBy] = useState<SortOption>("default");
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const filteredKeywords = useMemo(() => {
    const keywordsByFilter = filterKeywordsByType(
      initKeywords,
      calledKeywords,
      keywordsWithoutDoc,
      keywordsWithoutUsages,
      keywordDuplicates,
      currentFilter,
    );

    const filtered = filterKeywordsBySearch(keywordsByFilter, searchTerm);

    if (sortBy === "name_asc") {
      return [...filtered].sort((left, right) =>
        left.keyword_name_without_prefix.localeCompare(
          right.keyword_name_without_prefix,
        ),
      );
    }

    if (sortBy === "name_desc") {
      return [...filtered].sort((left, right) =>
        right.keyword_name_without_prefix.localeCompare(
          left.keyword_name_without_prefix,
        ),
      );
    }

    if (sortBy === "file_usages_desc") {
      return [...filtered].sort(
        (left, right) => right.file_usages - left.file_usages,
      );
    }

    if (sortBy === "total_usages_desc") {
      return [...filtered].sort(
        (left, right) => right.total_usages - left.total_usages,
      );
    }

    return filtered;
  }, [
    calledKeywords,
    currentFilter,
    initKeywords,
    keywordDuplicates,
    keywordsWithoutDoc,
    keywordsWithoutUsages,
    searchTerm,
    sortBy,
  ]);

  const showNoFileSelected =
    !fileSelected && ["all", "initialized", "called"].includes(currentFilter);

  useEffect(() => {
    setCurrentPage(1);
  }, [
    currentFilter,
    searchTerm,
    sortBy,
    initKeywords,
    calledKeywords,
    keywordsWithoutDoc,
    keywordsWithoutUsages,
    keywordDuplicates,
  ]);

  const totalPages = Math.max(
    1,
    Math.ceil(filteredKeywords.length / PAGE_SIZE),
  );
  const pageStartIndex = (currentPage - 1) * PAGE_SIZE;
  const paginatedKeywords = filteredKeywords.slice(
    pageStartIndex,
    pageStartIndex + PAGE_SIZE,
  );

  const handleSourceClick = (event: React.MouseEvent, filePath: string) => {
    if (event.ctrlKey || event.metaKey) {
      event.stopPropagation();
      vscode.postMessage({ command: "openFile", filePath });
    }
  };

  if (showNoFileSelected) {
    return <NoFileSelected />;
  }

  if (filteredKeywords.length === 0) {
    return <NoKeywordFound />;
  }

  return (
    <div className="flex h-full flex-col gap-4 p-4">
      <div className="flex w-full items-center gap-3">
        <Select
          value={sortBy}
          onValueChange={(value) => setSortBy(value as SortOption)}
        >
          <SelectTrigger className="h-9 w-44 bg-input text-sm border-border">
            <SelectValue placeholder="Sort: Default" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="default">Sort: Default</SelectItem>
            <SelectItem value="name_asc">Sort: Name (A-Z)</SelectItem>
            <SelectItem value="name_desc">Sort: Name (Z-A)</SelectItem>
            <SelectItem value="file_usages_desc">
              Sort: Usages In File
            </SelectItem>
            <SelectItem value="total_usages_desc">
              Sort: Total Usages
            </SelectItem>
          </SelectContent>
        </Select>

        <Input
          placeholder="Search Keywords..."
          value={searchTerm}
          onChange={(event) => setSearchTerm(event.target.value)}
          className="h-9 flex-1 bg-input text-sm border-border"
        />

        <Button
          variant="default"
          size="default"
          onClick={() => setSearchTerm("")}
        >
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
        <Table className="w-full table-fixed border-collapse">
          <TableHeader className="sticky top-0 z-10 bg-background">
            <TableRow className="border-b border-border">
              <TableHead className="w-[42%] px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-foreground">
                Keyword
              </TableHead>
              <TableHead className="w-[22%] px-4 py-3 text-left text-xs font-semibold uppercase tracking-wider text-foreground">
                Initialized In
              </TableHead>
              <TableHead className="w-[18%] px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-foreground">
                Usages In File
              </TableHead>
              <TableHead className="w-[18%] px-4 py-3 text-center text-xs font-semibold uppercase tracking-wider text-foreground">
                Total Usages
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedKeywords.map((keyword) => {
              const isSelected = selectedKeywordId === keyword.keyword_id;
              const sourceType = isUserSource(keyword.source)
                ? "user"
                : "external";

              return (
                <TableRow
                  key={keyword.keyword_id}
                  onClick={() => onKeywordSelect(keyword)}
                  className={cn(
                    "cursor-pointer border-b border-border/60 transition-colors hover:bg-accent/40",
                    isSelected && "bg-accent",
                  )}
                >
                  <TableCell className="px-4 py-3 text-sm">
                    <div className="flex min-w-0 items-center gap-2">
                      <Badge
                        className={cn(
                          "h-5 w-5 rounded-sm p-0 text-[10px] font-bold",
                          sourceType === "user"
                            ? "bg-primary text-primary-foreground"
                            : "bg-chart-4 text-primary-foreground",
                        )}
                      >
                        {sourceType === "user" ? "U" : "E"}
                      </Badge>
                      <span
                        className="block truncate"
                        title={keyword.keyword_name_with_prefix}
                      >
                        {keyword.keyword_name_without_prefix}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell
                    className="px-4 py-3 text-sm text-muted-foreground"
                    onClick={(event) =>
                      handleSourceClick(event, keyword.source)
                    }
                    title={keyword.source}
                  >
                    <span
                      className="block cursor-pointer truncate text-primary hover:underline"
                      title={keyword.source}
                    >
                      {keyword.file_name}
                    </span>
                  </TableCell>
                  <TableCell className="px-4 py-3 text-center text-sm">
                    {keyword.file_usages}
                  </TableCell>
                  <TableCell className="px-4 py-3 text-center text-sm">
                    <Badge
                      className={cn(
                        "px-2 py-0.5 text-xs",
                        getUsageBadgeClass(keyword.total_usages),
                      )}
                    >
                      {keyword.total_usages}
                    </Badge>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      <TablePagination
        currentPage={currentPage}
        totalPages={totalPages}
        onPageChange={setCurrentPage}
      />
    </div>
  );
}
