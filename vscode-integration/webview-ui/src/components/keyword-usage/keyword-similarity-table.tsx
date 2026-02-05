import React from "react";
import { vscode } from "../../utilities/vscode";

interface KeywordSimilarity {
  similar_keywords: Record<string, number>;
}

interface KeywordSimilarityTableProps {
  keywordSimilarity: KeywordSimilarity | null;
  keywordSources?: Record<string, string>;
}

export default function KeywordSimilarityTable({
  keywordSimilarity,
  keywordSources,
}: KeywordSimilarityTableProps) {
  const handleKeywordClick = (e: React.MouseEvent, keywordName: string) => {
    if (e.ctrlKey || e.metaKey) {
      e.stopPropagation();
      const filePath = keywordSources?.[keywordName];
      if (filePath) {
        vscode.postMessage({
          command: "openFile",
          filePath: filePath,
        });
      }
    }
  };

  const getSimilarityClass = (score: number): string => {
    const percent = score * 100;
    return percent > 80 ? "high-similarity" : "blue";
  };

  const getTooltip = (keywordName: string): string => {
    const filePath = keywordSources?.[keywordName];
    if (filePath) {
      return filePath;
    }
    return "";
  };

  const similarityTooltip =
    "The similarity score compares the source code of each keyword using text analysis.\n" +
    "First, each keyword's code is tokenized and converted into a vector using word counts.\n" +
    "Then, the similarity between keywords is measured using cosine similarity, which reflects how similar their code structures and content are.\n" +
    "The score is shown as a percentage: 100% means the keywords are identical, lower values mean less similarity.";

  if (
    !keywordSimilarity ||
    Object.keys(keywordSimilarity.similar_keywords).length === 0
  ) {
    return (
      <div className="usage-table-container">
        <table>
          <thead>
            <tr>
              <th>Keyword</th>
              <th>
                Similarity
                <span
                  className="similarity-icon"
                  title={similarityTooltip}
                  tabIndex={0}
                  aria-label="Similarity info"
                >
                  &#x2753;
                </span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td colSpan={2} className="no-similar-keywords">
                No similar keywords found
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    );
  }

  return (
    <div className="usage-table-container">
      <table>
        <thead>
          <tr>
            <th>Keyword</th>
            <th>
              Similarity
              <span
                className="similarity-icon"
                title={similarityTooltip}
                tabIndex={0}
                aria-label="Similarity info"
              >
                &#x2753;
              </span>
            </th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(keywordSimilarity.similar_keywords).map(
            ([similarKeyword, score]) => {
              const similarityPercent = (score * 100).toFixed(0);
              const hasSource =
                keywordSources && keywordSources[similarKeyword];
              const similarityClass = getSimilarityClass(score);

              return (
                <tr key={similarKeyword}>
                  <td
                    style={{
                      cursor: hasSource ? "pointer" : "default",
                      color: hasSource ? "#0078d4" : "inherit",
                    }}
                    onClick={(e) => handleKeywordClick(e, similarKeyword)}
                    title={getTooltip(similarKeyword)}
                  >
                    {similarKeyword}
                  </td>
                  <td>
                    <span className={`usage-badge ${similarityClass}`}>
                      {similarityPercent}%
                    </span>
                  </td>
                </tr>
              );
            },
          )}
        </tbody>
      </table>
    </div>
  );
}
