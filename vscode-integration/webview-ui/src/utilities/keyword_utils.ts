import { Keyword } from "../types/keywords";

export function deduplicateKeywords(keywords: Keyword[]): Keyword[] {
  const seen = new Map<string, Keyword>();

  keywords.forEach((keyword) => {
    const key = keyword.keyword_name_with_prefix;

    if (!seen.has(key)) {
      seen.set(key, keyword);
    }
  });

  return Array.from(seen.values());
}
export function filterKeywordsByType(
  initKeywords: Keyword[],
  calledKeywords: Keyword[],
  keywordsWithoutDoc: Keyword[],
  keywordsWithoutUsages: Keyword[],
  keywordDuplicates: Keyword[],
  filterType: string,
): Keyword[] {
  let result: Keyword[];

  switch (filterType) {
    case "all":
      result = [...initKeywords, ...calledKeywords];
      break;
    case "initialized":
      result = initKeywords;
      break;
    case "called":
      result = calledKeywords;
      break;
    case "kw_wo_usages":
      result = keywordsWithoutUsages;
      break;
    case "kw_wo_doc":
      result = keywordsWithoutDoc;
      break;
    case "kw_duplicates":
      result = keywordDuplicates;
      break;
    default:
      result = [...initKeywords, ...calledKeywords];
  }

  return deduplicateKeywords(result);
}

/**
 * Filter keywords by search term
 */
export function filterKeywordsBySearch(
  keywords: Keyword[],
  searchTerm: string,
): Keyword[] {
  if (!searchTerm.trim()) return keywords;

  const lowerSearch = searchTerm.toLowerCase();
  return keywords.filter(
    (kw) =>
      kw.keyword_name_without_prefix.toLowerCase().includes(lowerSearch) ||
      kw.source.toLowerCase().includes(lowerSearch),
  );
}

/**
 * Sort keywords
 */
export function sortKeywords(keywords: Keyword[], sortBy: string): Keyword[] {
  const sorted = [...keywords];

  switch (sortBy) {
    case "name_asc":
      return sorted.sort((a, b) =>
        a.keyword_name_without_prefix.localeCompare(
          b.keyword_name_without_prefix,
        ),
      );
    case "name_desc":
      return sorted.sort((a, b) =>
        b.keyword_name_without_prefix.localeCompare(
          a.keyword_name_without_prefix,
        ),
      );
    case "usages_asc":
      return sorted.sort((a, b) => a.total_usages - b.total_usages);
    case "usages_desc":
      return sorted.sort((a, b) => b.total_usages - a.total_usages);
    default:
      return sorted;
  }
}

export function getUsageClass(total_usages: number): string {
  if (total_usages === 0) return "none";
  if (total_usages <= 5) return "low";
  if (total_usages <= 20) return "medium";
  return "high";
}
