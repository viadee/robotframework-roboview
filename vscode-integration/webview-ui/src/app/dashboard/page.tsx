import { useEffect, useState } from "react";
import { useMessageListener } from "@/hooks/useMessageListener";
import { KPIData, IssueSummary, MostUsedKeywords } from "@/types/dashboard";
import ProjectInfoCard from "./project-info-card";
import MetricsGrid from "./metrics-grid";
import KeywordAnalysis from "./keyword-analysis";
import RobocopIssuesSummary from "./robocop-issues";
import { vscode } from "@/utilities/vscode";
import { CollapsibleSection } from "./collapsible-section";
import { FolderOpen, ShieldAlert, BarChart2, Activity } from "lucide-react";

export default function DashboardPage() {
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
    <div className="mx-auto flex h-full w-full max-w-8xl flex-col gap-6 overflow-y-auto p-6">
      <CollapsibleSection
        title="Selected Project"
        icon={FolderOpen}
        iconColor="text-amber-400"
      >
        <ProjectInfoCard projectPath={projectPath} />
      </CollapsibleSection>

      <CollapsibleSection
        title="KPIs"
        icon={Activity}
        iconColor="text-blue-400"
      >
        <MetricsGrid kpiData={kpiData} />
      </CollapsibleSection>

      <CollapsibleSection
        title="Keyword Analysis"
        icon={BarChart2}
        iconColor="text-amber-400"
      >
        <KeywordAnalysis
          mostUsedUserKeywords={mostUsedKeywords?.most_used_user_keywords ?? []}
          mostUsedExternalKeywords={
            mostUsedKeywords?.most_used_external_keywords ?? []
          }
        />
      </CollapsibleSection>

      <CollapsibleSection
        title="Robocop Issues Summary"
        icon={ShieldAlert}
        iconColor="text-red-400"
      >
        <RobocopIssuesSummary issues={issueSummary} />
      </CollapsibleSection>
    </div>
  );
}
