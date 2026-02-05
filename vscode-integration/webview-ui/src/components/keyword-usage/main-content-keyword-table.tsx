import React from "react";
import { Keyword } from "../../types/keywords";
import { getUsageClass } from "../../utilities/keyword_utils";
import { vscode } from "../../utilities/vscode";
import "../../styles/mainView/contentTable.css";

interface KeywordTableProps {
  keywords: Keyword[];
  selectedKeyword: Keyword | null;
  onKeywordClick: (keyword: Keyword) => void;
}

export default function KeywordTable({
  keywords,
  selectedKeyword,
  onKeywordClick,
}: KeywordTableProps) {
  const handleFileClick = (e: React.MouseEvent, filePath: string) => {
    if (e.ctrlKey || e.metaKey) {
      e.stopPropagation();
      vscode.postMessage({
        command: "openFile",
        filePath: filePath,
      });
    }
  };

  return (
    <table>
      <thead>
        <tr>
          <th>Keyword</th>
          <th>Initialized In</th>
          <th className="center-align">Usages In File</th>
          <th className="center-align">Total Usages</th>
        </tr>
      </thead>
      <tbody>
        {keywords.map((keywordData: Keyword) => {
          const {
            keyword_name_without_prefix,
            keyword_name_with_prefix,
            file_name,
            source,
            file_usages,
            total_usages,
          } = keywordData;
          const usageClass = getUsageClass(total_usages);
          const isUserDefined =
            source &&
            (source.includes(".resource") || source.includes(".robot"));
          const iconClass = isUserDefined ? "user-defined" : "external";
          const iconLetter = isUserDefined ? "U" : "E";
          const isSelected =
            selectedKeyword?.keyword_name_without_prefix ===
            keyword_name_without_prefix;

          return (
            <tr
              key={keyword_name_with_prefix}
              className={isSelected ? "selected" : ""}
              onClick={() => onKeywordClick(keywordData)}
            >
              <td>
                <div className="keyword-name">
                  <span className={`keyword-icon ${iconClass}`}>
                    {iconLetter}
                  </span>
                  {keyword_name_without_prefix}
                </div>
              </td>
              <td>
                <div
                  className="path-scroll"
                  onClick={(e) => handleFileClick(e, source)}
                  style={{ cursor: "pointer" }}
                  title={source}
                >
                  <span className="path">{file_name}</span>
                </div>
              </td>
              <td>{file_usages}</td>
              <td>
                <span className={`usage-badge ${usageClass}`}>
                  {total_usages}
                </span>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
