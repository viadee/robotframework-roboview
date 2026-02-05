import React from "react";
import FileUsageTable from "../keyword-usage/file-usage-table";
import KeywordSimilarityTable from "../keyword-usage/keyword-similarity-table";
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
}

export default function DetailsPanel({
  selectedKeyword,
  testFiles,
  resourceFiles,
  keywordSimilarity,
}: DetailsPanelProps) {
  return (
    <div className="details-panel">
      <div className="details-header">
        <h2>
          {selectedKeyword?.keyword_name_without_prefix || "Select a Keyword"}
        </h2>
      </div>

      <div className="details-content">
        <div className="details-section">
          <h3>Documentation</h3>
          <div className="documentation">
            {selectedKeyword?.documentation || "No [Documentation] defined"}
          </div>
        </div>

        <div className="details-section">
          <h3>Usage in Robot Files</h3>
          <div className="usage-table-container">
            <FileUsageTable files={testFiles} />
          </div>
        </div>

        <div className="details-section">
          <h3>Usage in Resource Files</h3>
          <div className="usage-table-container">
            <FileUsageTable files={resourceFiles} />
          </div>
        </div>

        <div className="details-section">
          <h3>Similar Keywords</h3>
          <div className="usage-table-container">
            <KeywordSimilarityTable keywordSimilarity={keywordSimilarity} />
          </div>
        </div>
      </div>
    </div>
  );
}
