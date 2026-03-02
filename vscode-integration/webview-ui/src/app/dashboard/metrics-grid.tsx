import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Tag,
  RefreshCw,
  AlertTriangle,
  ShieldAlert,
  BookOpen,
  FileCode,
} from "lucide-react";
import { KPIData } from "@/types/dashboard";

export default function MetricsGrid({ kpiData }: { kpiData: KPIData | null }) {
  const formatPercentage = (value: number) => `${Math.round(value * 100)}%`;

  const metrics = [
    {
      title: "User Defined Keywords",
      value: kpiData ? String(kpiData.num_user_keywords) : "N/A",
      subtitle: "Total number of user defined keywords",
      icon: <Tag />,
      iconClass: "bg-chart-1/15 text-chart-1",
    },
    {
      title: "Keyword Reuse Rate",
      value: kpiData ? formatPercentage(kpiData.keyword_reusage_rate) : "N/A",
      subtitle: "Keywords used more than once",
      icon: <RefreshCw />,
      iconClass: "bg-chart-3/15 text-chart-3",
    },
    {
      title: "Unused Keywords",
      value: kpiData ? String(kpiData.num_unused_keywords) : "N/A",
      subtitle: "Keywords never called",
      icon: <AlertTriangle />,
      iconClass: "bg-chart-4/15 text-chart-4",
    },
    {
      title: "Robocop Issues",
      value: kpiData ? String(kpiData.num_robocop_issues) : "N/A",
      subtitle: "Total violations found",
      icon: <ShieldAlert />,
      iconClass: "bg-chart-5/15 text-chart-5",
    },
    {
      title: "Documentation Coverage",
      value: kpiData ? formatPercentage(kpiData.documentation_coverage) : "N/A",
      subtitle: "Keywords with [Documentation]",
      icon: <BookOpen />,
      iconClass: "bg-chart-2/15 text-chart-2",
    },
    {
      title: "Robot Framework Files",
      value: kpiData ? String(kpiData.num_rf_files) : "N/A",
      subtitle: "Total .robot and .resource files",
      icon: <FileCode />,
      iconClass: "bg-chart-1/15 text-chart-1",
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      {metrics.map((metric) => (
        <Card key={metric.title}>
          <CardHeader className="flex-row items-start justify-between gap-3 pb-2">
            <div>
              <CardTitle className="text-lg font-medium">
                {metric.title}
              </CardTitle>
            </div>
            <div
              className={`inline-flex h-9 w-9 items-center justify-center rounded-full text-sm ${metric.iconClass}`}
            >
              {metric.icon}
            </div>
          </CardHeader>
          <CardContent className="space-y-1">
            <div className="text-2xl font-semibold tracking-tight">
              {metric.value}
            </div>
            <p className="text-muted-foreground text-sm">{metric.subtitle}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
