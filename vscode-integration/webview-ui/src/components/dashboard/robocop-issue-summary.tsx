import React from "react";
import { IssueSummary } from "../../types/dashboard";

interface RobocopIssuesSummaryProps {
  issues: IssueSummary[];
}

const RobocopIssuesSummary: React.FC<RobocopIssuesSummaryProps> = ({
  issues,
}) => {
  // Map category codes to readable names
  const getCategoryName = (category: string): string => {
    const categoryMap: Record<string, string> = {
      ARG: "Arguments",
      COM: "Comments",
      DOC: "Documentation",
      DUP: "Duplication",
      ERR: "Errors",
      IMP: "Imports",
      KW: "Keywords",
      LEN: "Lengths",
      MISC: "Miscellaneous",
      NAME: "Naming",
      ORD: "Order",
      SPC: "Spacing",
      TAG: "Tags",
      VAR: "Variables",
      ANN: "Annotations",
    };
    return categoryMap[category] || category;
  };

  // Determine severity based on category
  const getSeverityClass = (category: string): string => {
    const errorCategories = ["ERR", "DUP"];
    const warningCategories = ["DOC", "LEN", "ARG", "NAME"];

    if (errorCategories.includes(category)) {
      return "severity-error";
    } else if (warningCategories.includes(category)) {
      return "severity-warning";
    }
    return "severity-info";
  };

  // Sort issues by count (descending)
  const sortedIssues = [...issues].sort((a, b) => b.count - a.count);

  return (
    <div className="issues-list">
      {sortedIssues.length === 0 ? (
        <div className="no-issues">
          <div className="no-issues-icon">✓</div>
          <div className="no-issues-text">No Robocop issues found!</div>
        </div>
      ) : (
        sortedIssues.map((issue, index) => (
          <div key={index} className="issue-item">
            <div
              className={`issue-severity ${getSeverityClass(issue.category)}`}
            ></div>
            <div className="issue-text">
              {getCategoryName(issue.category)} issues
            </div>
            <div className="issue-count">{issue.count} issues</div>
          </div>
        ))
      )}
    </div>
  );
};

export default RobocopIssuesSummary;
