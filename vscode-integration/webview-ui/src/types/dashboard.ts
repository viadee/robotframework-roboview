import { KeywordUsage } from "./keywords";

export interface KPIData {
  num_user_keywords: number;
  num_unused_keywords: number;
  keyword_reusage_rate: number;
  num_robocop_issues: number;
  documentation_coverage: number;
  num_rf_files: number;
}

export interface MostUsedKeywords {
  most_used_user_keywords: KeywordUsage[];
  most_used_external_keywords: KeywordUsage[];
}

export interface IssueSummary {
  category: string;
  count: number;
}
