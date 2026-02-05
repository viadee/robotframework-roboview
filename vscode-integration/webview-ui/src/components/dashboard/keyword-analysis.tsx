import React from "react";
import { KeywordUsage } from "../../types/keywords";

interface KeywordAnalysisProps {
  mostUsedUserKeywords: KeywordUsage[];
  mostUsedExternalKeywords: KeywordUsage[];
}

const KeywordAnalysis: React.FC<KeywordAnalysisProps> = ({
  mostUsedUserKeywords,
  mostUsedExternalKeywords,
}) => {
  // Calculate max value for scaling bars
  const maxUserUsage = Math.max(
    ...mostUsedUserKeywords.map((kw) => kw.total_usages),
    1,
  );
  const maxExternalUsage = Math.max(
    ...mostUsedExternalKeywords.map((kw) => kw.total_usages),
    1,
  );

  return (
    <div className="charts-container">
      <div className="chart-card">
        <div className="chart-title">Top 5 Most Used User Defined Keywords</div>
        <div className="bar-chart">
          {mostUsedUserKeywords.map((keyword, index) => {
            const percentage = (keyword.total_usages / maxUserUsage) * 100;
            return (
              <div key={keyword.keyword_id || index} className="bar-item">
                <div
                  className="bar-label"
                  title={keyword.keyword_name_with_prefix}
                >
                  {keyword.keyword_name_without_prefix}
                </div>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: "#4fc3f7",
                    }}
                  ></div>
                </div>
                <div className="bar-value">{keyword.total_usages}</div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="chart-card">
        <div className="chart-title">
          Top 5 Most Used External/BuiltIn Keywords
        </div>
        <div className="bar-chart">
          {mostUsedExternalKeywords.map((keyword, index) => {
            const percentage = (keyword.total_usages / maxExternalUsage) * 100;
            return (
              <div key={keyword.keyword_id || index} className="bar-item">
                <div
                  className="bar-label"
                  title={keyword.keyword_name_with_prefix}
                >
                  {keyword.keyword_name_without_prefix}
                </div>
                <div className="bar-track">
                  <div
                    className="bar-fill"
                    style={{
                      width: `${percentage}%`,
                      backgroundColor: "#ab47bc",
                    }}
                  ></div>
                </div>
                <div className="bar-value">{keyword.total_usages}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default KeywordAnalysis;
