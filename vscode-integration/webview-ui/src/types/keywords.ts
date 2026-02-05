export interface KeywordUsage {
  keyword_id: string;
  file_name: string;
  keyword_name_without_prefix: string;
  keyword_name_with_prefix: string;
  source: string;
  file_usages: number;
  total_usages: number;
}

export interface Keyword {
  keyword_id: string;
  file_name: string;
  keyword_name_without_prefix: string;
  keyword_name_with_prefix: string;
  documentation: string;
  source: string;
  file_usages: number;
  total_usages: number;
}

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

export interface KeywordCountsNew {
  all: number;
  initialized: number;
  called: number;
  unused: number;
  kw_wo_doc: number;
}

export interface FileUsage {
  file_name: string;
  path: string;
  usages: number;
}

export interface KeywordSimilarity {
  keyword_id: string;
  keyword_name_without_prefix: string;
  keyword_name_with_prefix: string;
  source: string;
  score: number;
}

export interface SimilarKeywordsMap {
  similar_keywords: Record<string, number>;
}

export interface FilterItem {
  id: string;
  label: string;
  count: number;
}
