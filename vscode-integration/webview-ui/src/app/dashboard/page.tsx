import React, { useState, useEffect } from "react";
import { vscode } from "../../utilities/vscode";
import { useMessageListener } from "../../hooks/useMessageListener";
import MetricsGrid from "../../components/dashboard/metric-grid";
import KeywordAnalysis from "../../components/dashboard/keyword-analysis";
import RobocopIssuesSummary from "../../components/dashboard/robocop-issue-summary";
import ProjectInfo from "../../components/dashboard/project-info";
import { KPIData, IssueSummary, MostUsedKeywords } from "../../types/dashboard";

export default function DashboardView() {
  const [projectPath, setProjectPath] = useState<string>("");
  const [kpiData, setKpiData] = useState<KPIData | null>(null);
  const [mostUsedKeywords, setMostUsedKeywords] =
    useState<MostUsedKeywords | null>(null);
  const [issueSummary, setIssueSummary] = useState<IssueSummary[]>([]);

  useMessageListener({
    projectPath: (message) => {
      setProjectPath(message.path);
    },
    kpis: (message) => {
      setKpiData(message.data);
    },
    mostUsedKeywords: (message) => {
      setMostUsedKeywords({
        most_used_user_keywords: message.mostUsedUser,
        most_used_external_keywords: message.mostUsedExternal,
      });
    },
    robocopIssueSummary: (message) => {
      setIssueSummary(message.summary);
    },
  });

  useEffect(() => {
    vscode.postMessage({ command: "getProjectPath" });
    vscode.postMessage({ command: "getKPIs" });
    vscode.postMessage({ command: "getMostUsedKeywords" });
    vscode.postMessage({ command: "getRobocopIssueSummary" });
  }, []);

  return (
    <div className="dashboard-view">
      <div className="dashboard-content">
        <h2 className="section-title">Selected Project</h2>
        <ProjectInfo projectPath={projectPath} />

        <h2 className="section-title">KPIs</h2>
        {kpiData && <MetricsGrid kpiData={kpiData} />}

        <h2 className="section-title">Keyword Analysis</h2>
        {mostUsedKeywords && (
          <KeywordAnalysis
            mostUsedUserKeywords={mostUsedKeywords.most_used_user_keywords}
            mostUsedExternalKeywords={
              mostUsedKeywords.most_used_external_keywords
            }
          />
        )}

        <h2 className="section-title">Robocop Issues Summary</h2>
        <RobocopIssuesSummary issues={issueSummary} />
      </div>
    </div>
  );
}
