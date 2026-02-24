import { Badge } from "@/components/ui/badge";
import {
  HoverCard,
  HoverCardContent,
  HoverCardTrigger,
} from "@/components/ui/hover-card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { CircleHelp } from "lucide-react";
import { KeywordSimilarity } from "@/types/keywords";
import { vscode } from "@/utilities/vscode";

interface DetailsSimilarityTableProps {
  keywordSimilarity: KeywordSimilarity[];
  keywordSimilaritySources: Record<string, string>;
}

const similarityInfoText =
  "The similarity score compares the source code of each keyword using text analysis:\n\n" +
  "1. Each keyword's code is tokenized and transformed into a vector based on word frequencies.\n" +
  "2. The vectors are compared using cosine similarity to measure how closely code structure and content match.\n" +
  "3. The result is shown as a percentage: 100% means identical code, lower values indicate less similarity.\n\n" +
  "Note: Starting at 80% similarity, the badge is shown in red, which may indicate a potential duplicate.";

function getSimilarityBadgeClass(percentage: number) {
  if (percentage > 80) {
    return "bg-destructive/30 text-foreground";
  }

  return "bg-chart-1/30 text-foreground";
}

export function DetailsSimilarityTable({
  keywordSimilarity,
  keywordSimilaritySources,
}: DetailsSimilarityTableProps) {
  const handleKeywordClick = (event: React.MouseEvent, keywordName: string) => {
    if (event.ctrlKey || event.metaKey) {
      event.stopPropagation();
      const filePath = keywordSimilaritySources[keywordName];
      if (filePath) {
        vscode.postMessage({ command: "openFile", filePath });
      }
    }
  };

  return (
    <div className="overflow-hidden rounded-md border border-border">
      <div className="max-h-90 overflow-y-auto">
        <Table className="table-fixed">
          <TableHeader>
            <TableRow>
              <TableHead className="px-3 py-2 text-xs uppercase tracking-wider">
                Keyword
              </TableHead>
              <TableHead className="w-28 px-3 py-2 text-right text-xs uppercase tracking-wider">
                <span className="inline-flex items-center gap-1">
                  Similarity
                  <HoverCard openDelay={150} closeDelay={100}>
                    <HoverCardTrigger asChild>
                      <button
                        type="button"
                        className="inline-flex items-center text-muted-foreground transition-colors hover:text-foreground"
                        aria-label="How similarity is calculated"
                      >
                        <CircleHelp className="size-3.5" />
                      </button>
                    </HoverCardTrigger>
                    <HoverCardContent
                      align="end"
                      className="w-80 text-left text-xs normal-case tracking-normal leading-relaxed"
                    >
                      <p className="whitespace-pre-line">
                        {similarityInfoText}
                      </p>
                    </HoverCardContent>
                  </HoverCard>
                </span>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {keywordSimilarity.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={2}
                  className="px-3 py-3 text-sm text-muted-foreground"
                >
                  No similar keywords found
                </TableCell>
              </TableRow>
            )}

            {keywordSimilarity.map((item) => {
              const percentage = Math.round(item.score * 100);
              const sourcePath =
                keywordSimilaritySources[item.keyword_name_without_prefix];
              const hasSource = Boolean(sourcePath);

              return (
                <TableRow
                  key={`${item.keyword_id}-${item.keyword_name_without_prefix}`}
                >
                  <TableCell
                    className="max-w-0 px-3 py-2 text-sm"
                    title={item.keyword_name_with_prefix ?? ""}
                    onClick={(event) =>
                      handleKeywordClick(
                        event,
                        item.keyword_name_without_prefix,
                      )
                    }
                  >
                    <span
                      className={
                        hasSource
                          ? "block truncate cursor-pointer text-foreground/90 hover:text-primary hover:underline"
                          : "block truncate"
                      }
                    >
                      {item.keyword_name_without_prefix}
                    </span>
                  </TableCell>
                  <TableCell className="w-28 px-3 py-2 text-right">
                    <Badge
                      className={`px-2 py-0.5 text-xs ${getSimilarityBadgeClass(percentage)}`}
                    >
                      {percentage}%
                    </Badge>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
