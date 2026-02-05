export interface Keyword {
  keyword: string;
  documentation: string;
  source: string;
  file_usages: number;
  total_usages: number;
}

export interface FileUsage {
  file_name: string;
  usages: number;
}

export interface KeywordSimilarity {
  similar_keywords: Record<string, number>;
}

export interface GraphData {
  [key: string]: string[];
}

export type GraphMode = "keyword-dependency" | "resource-hierarchy";
export type FileFilterType =
  | "all-files"
  | "robot-files"
  | "resource-files"
  | "files-with-cycles";
export type FilterMode = "all" | "cycles";
export type ViewType = "table" | "graph";

export interface KeywordCounts {
  all: number;
  initialized: number;
  called: number;
  high: number;
  medium: number;
  low: number;
  unused: number;
  kw_wo_doc: number;
}
