import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { KeywordSimilarity } from "@/types/keywords";
import { vscode } from "@/utilities/vscode";

interface DetailsSimilarityTableProps {
  keywordSimilarity: KeywordSimilarity[];
  keywordSimilaritySources: Record<string, string>;
}

function getSimilarityBadgeClass(percentage: number) {
  if (percentage > 80) {
    return "bg-destructive/20 text-destructive";
  }

  return "bg-chart-1/20 text-chart-1";
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
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="px-3 py-2 text-xs uppercase tracking-wider">
              Keyword
            </TableHead>
            <TableHead className="px-3 py-2 text-right text-xs uppercase tracking-wider">
              Similarity
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
                  className="px-3 py-2 text-sm"
                  title={sourcePath ?? ""}
                  onClick={(event) =>
                    handleKeywordClick(event, item.keyword_name_without_prefix)
                  }
                >
                  <span
                    className={
                      hasSource
                        ? "cursor-pointer text-primary hover:underline"
                        : ""
                    }
                  >
                    {item.keyword_name_without_prefix}
                  </span>
                </TableCell>
                <TableCell className="px-3 py-2 text-right">
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
  );
}
