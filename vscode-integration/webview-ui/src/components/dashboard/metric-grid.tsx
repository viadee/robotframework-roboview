import React from "react";
import { KPIData } from "../../types/dashboard";

interface MetricsGridProps {
  kpiData: KPIData;
}

const MetricsGrid: React.FC<MetricsGridProps> = ({ kpiData }) => {
  const formatPercentage = (value: number) => {
    return `${Math.round(value * 100)}%`;
  };

  return (
    <div className="metrics-grid">
      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">User Defined Keywords</span>
          <div className="metric-icon icon-blue">📝</div>
        </div>
        <div className="metric-value">{kpiData.num_user_keywords}</div>
        <div className="metric-subtitle">
          Total number of user defined keywords
        </div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">Keyword Reuse Rate</span>
          <div className="metric-icon icon-green">♻️</div>
        </div>
        <div className="metric-value">
          {formatPercentage(kpiData.keyword_reusage_rate)}
        </div>
        <div className="metric-subtitle">Keywords used more than once</div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">Unused Keywords</span>
          <div className="metric-icon icon-orange">⚠️</div>
        </div>
        <div className="metric-value">{kpiData.num_unused_keywords}</div>
        <div className="metric-subtitle">Keywords never called</div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">Robocop Issues</span>
          <div className="metric-icon icon-red">🔍</div>
        </div>
        <div className="metric-value">{kpiData.num_robocop_issues}</div>
        <div className="metric-subtitle">Total violations found</div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">Documentation Coverage</span>
          <div className="metric-icon icon-purple">📚</div>
        </div>
        <div className="metric-value">
          {formatPercentage(kpiData.documentation_coverage)}
        </div>
        <div className="metric-subtitle">Keywords with [Documentation]</div>
      </div>

      <div className="metric-card">
        <div className="metric-header">
          <span className="metric-title">Robot Framework Files</span>
          <div className="metric-icon icon-blue">📊</div>
        </div>
        <div className="metric-value">{kpiData.num_rf_files}</div>
        <div className="metric-subtitle">Total .robot and .resource files</div>
      </div>
    </div>
  );
};

export default MetricsGrid;
