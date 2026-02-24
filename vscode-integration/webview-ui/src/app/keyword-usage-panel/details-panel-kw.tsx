import { NoKeywordSelected } from "./no-keyword-selected";
import { CollapsibleFilterSection } from "@/components/panel-section/collapsible-filter-section";
import { FileUsage, Keyword, KeywordSimilarity } from "@/types/keywords";
import { DetailsUsageTable } from "./details-usage-table";
import { DetailsSimilarityTable } from "./details-similarity-table";
import { Bot, BookText, KeyRound, Library, Sparkles } from "lucide-react";

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
        <h2 className="flex items-center gap-2 text-xl font-semibold tracking-tight">
          <KeyRound className="size-5 shrink-0 text-primary" />
          {selectedKeyword?.keyword_name_without_prefix ?? "Select a Keyword"}
        </h2>
      </div>

      {!selectedKeyword ? (
        <NoKeywordSelected />
      ) : (
        <div className="flex-1 overflow-auto px-4 py-4 space-y-5">
          <CollapsibleFilterSection
            title="Documentation"
            icon={<BookText className="size-4 shrink-0 text-amber-400" />}
          >
            <div className="whitespace-pre-wrap rounded-md border border-border bg-input px-3 py-2 text-sm leading-relaxed text-foreground">
              {selectedKeyword.documentation || "No [Documentation] defined"}
            </div>
          </CollapsibleFilterSection>

          <CollapsibleFilterSection
            title="Usage in Robot Files"
            icon={<Bot className="size-4 shrink-0 text-primary" />}
          >
            <DetailsUsageTable files={robotFileUsages} />
          </CollapsibleFilterSection>

          <CollapsibleFilterSection
            title="Usage in Resource Files"
            icon={<Library className="size-4 shrink-0 text-orange-400" />}
          >
            <DetailsUsageTable files={resourceFileUsages} />
          </CollapsibleFilterSection>

          <CollapsibleFilterSection
            title="Similar Keywords"
            icon={<Sparkles className="size-4 shrink-0 text-violet-400" />}
          >
            <DetailsSimilarityTable
              keywordSimilarity={sortedSimilarity}
              keywordSimilaritySources={keywordSimilaritySources}
            />
          </CollapsibleFilterSection>
        </div>
      )}
    </div>
  );
}
