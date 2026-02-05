import React from "react";
import FileUsageTable from "./file-usage-table";
import KeywordSimilarityTable from "./keyword-similarity-table";
import DetailsHeader from "../details-panel/details-header";
import DetailsSectionText from "../details-panel/details-section-text";
import DetailsSectionTable from "../details-panel/details-section-table";
import { Keyword } from "../../types/keywords";

interface FileUsage {
  file_name: string;
  path: string;
  usages: number;
}

interface KeywordSimilarity {
  similar_keywords: Record<string, number>;
}

interface DetailsPanelProps {
  selectedKeyword: Keyword | null;
  testFiles: FileUsage[];
  resourceFiles: FileUsage[];
  keywordSimilarity: KeywordSimilarity | null;
  keywordSimilaritySources?: Record<string, string>;
}

export default function DetailsPanelKeywordUsage({
  selectedKeyword,
  testFiles,
  resourceFiles,
  keywordSimilarity,
  keywordSimilaritySources,
}: DetailsPanelProps) {
  return (
    <div className="details-panel">
      <DetailsHeader
        title={
          selectedKeyword?.keyword_name_without_prefix || "Select a Keyword"
        }
      />

      <div className="details-content">
        <DetailsSectionText
          title="Documentation"
          content={selectedKeyword?.documentation}
          emptyMessage="No [Documentation] defined"
        />

        <DetailsSectionTable title="Usage in Robot Files">
          <FileUsageTable files={testFiles} />
        </DetailsSectionTable>

        <DetailsSectionTable title="Usage in Resource Files">
          <FileUsageTable files={resourceFiles} />
        </DetailsSectionTable>

        <DetailsSectionTable title="Similar Keywords">
          <KeywordSimilarityTable
            keywordSimilarity={keywordSimilarity}
            keywordSources={keywordSimilaritySources}
          />
        </DetailsSectionTable>
      </div>
    </div>
  );
}
