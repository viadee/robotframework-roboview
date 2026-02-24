import { Separator } from "@/components/ui/separator";
import { NoKeywordSelected } from "./no-keyword-selected";
import { DetailsSectionTitle } from "@/app/shared/details-section-title";
import { FileUsage, Keyword, KeywordSimilarity } from "@/types/keywords";
import { DetailsUsageTable } from "./details-usage-table";
import { DetailsSimilarityTable } from "./details-similarity-table";

interface DetailsPanelKeywordUsageProps {
  selectedKeyword: Keyword | null;
  robotFileUsages: FileUsage[];
  resourceFileUsages: FileUsage[];
  keywordSimilarity: KeywordSimilarity[];
  keywordSimilaritySources: Record<string, string>;
}

export function DetailsPanelKeywordUsage({
  selectedKeyword,
  robotFileUsages,
  resourceFileUsages,
  keywordSimilarity,
  keywordSimilaritySources,
}: DetailsPanelKeywordUsageProps) {
  const sortedSimilarity = [...keywordSimilarity].sort(
    (left, right) => right.score - left.score,
  );

  return (
    <div className="flex h-full flex-col bg-background">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-xl font-semibold tracking-tight">
          {selectedKeyword?.keyword_name_without_prefix ?? "Select a Keyword"}
        </h2>
      </div>

      {!selectedKeyword ? (
        <NoKeywordSelected />
      ) : (
        <div className="flex-1 overflow-auto px-4 py-4 space-y-5">
          <div className="space-y-2">
            <DetailsSectionTitle title="Documentation" />
            <div className="whitespace-pre-wrap rounded-md border border-border bg-input px-3 py-2 text-sm leading-relaxed text-foreground">
              {selectedKeyword.documentation || "No [Documentation] defined"}
            </div>
          </div>

          <Separator />

          <div className="space-y-2">
            <DetailsSectionTitle title="Usage in Robot Files" />
            <DetailsUsageTable files={robotFileUsages} />
          </div>

          <Separator />

          <div className="space-y-2">
            <DetailsSectionTitle title="Usage in Resource Files" />
            <DetailsUsageTable files={resourceFileUsages} />
          </div>

          <Separator />

          <div className="space-y-2">
            <DetailsSectionTitle title="Similar Keywords" />
            <DetailsSimilarityTable
              keywordSimilarity={sortedSimilarity}
              keywordSimilaritySources={keywordSimilaritySources}
            />
          </div>
        </div>
      )}
    </div>
  );
}
