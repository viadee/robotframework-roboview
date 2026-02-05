import React from "react";
import KeywordTable from "./main-content-keyword-table";
import SearchBar from "../main-content/main-content-searchbar";
import Toolbar from "../main-content/main-content-toolbar";
import { Keyword } from "../../types/keywords";
import { SortOption } from "../../types/toolbar";
import {
  filterKeywordsByType,
  filterKeywordsBySearch,
  sortKeywords,
} from "../../utilities/keyword_utils";

const keywordUsageSortOptions: SortOption[] = [
  { value: "sort", label: "Sort: Default" },
  { value: "name_asc", label: "Sort: Name (A-Z)" },
  { value: "name_desc", label: "Sort: Name (Z-A)" },
  { value: "usages_desc", label: "Sort: Usage (High-Low)" },
  { value: "usages_asc", label: "Sort: Usage (Low-High)" },
];

interface MainContentProps {
  initKeywords: Keyword[];
  calledKeywords: Keyword[];
  keywordsWithoutDoc: Keyword[];
  keywordsWithoutUsages: Keyword[];
  keywordDuplicates: Keyword[];
  currentFilter: string;
  searchTerm: string;
  sortBy: string;
  onSortChange: (sort: string) => void;
  onSearchChange: (value: string) => void;
  onClear: () => void;
  selectedKeyword: Keyword | null;
  onKeywordClick: (keyword: Keyword) => void;
  fileSelected?: boolean;
}

export default function MainContentKeywordUsage({
  initKeywords,
  calledKeywords,
  keywordsWithoutDoc,
  keywordsWithoutUsages,
  keywordDuplicates,
  currentFilter,
  searchTerm,
  sortBy,
  onSortChange,
  onSearchChange,
  onClear,
  selectedKeyword,
  onKeywordClick,
  fileSelected = false,
}: MainContentProps) {
  let keywordsToShow: Keyword[] = [];

  keywordsToShow = filterKeywordsByType(
    initKeywords,
    calledKeywords,
    keywordsWithoutDoc,
    keywordsWithoutUsages,
    keywordDuplicates,
    currentFilter,
  );

  keywordsToShow = filterKeywordsBySearch(keywordsToShow, searchTerm);
  keywordsToShow = sortKeywords(keywordsToShow, sortBy);

  const hasKeywords =
    keywordsToShow.length > 0 ||
    (currentFilter !== "kw_wo_doc" &&
      currentFilter !== "kw_wo_usages" &&
      currentFilter !== "kw_with_cycles" &&
      (initKeywords.length > 0 || calledKeywords.length > 0));

  if (!hasKeywords) {
    return (
      <div className="main-content">
        <div className="keyword-placeholder">
          <div className="placeholder-icon">📊</div>
          <h2>{fileSelected ? "No Keyword Calls or Initialized Keywords" : "No File Selected"}</h2>
          {!fileSelected && (
            <>
              <p>Please follow these steps to open the Keyword Overview:</p>
              <ol className="placeholder-steps">
                <li>
                  Select a <strong>Robot Framework File</strong> from the file
                  selection
                </li>
                <li>
                  Use the <strong>Type Filters</strong> or{" "}
                  <strong>Global Filter</strong> to group Keywords global or locally
                </li>
                <li>
                  Click on a Keyword to view its <strong>details</strong>
                </li>
              </ol>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="main-content">
      <div className="controls-bar">
        <Toolbar
          sortBy={sortBy}
          onSortChange={onSortChange}
          options={keywordUsageSortOptions}
        />
        <SearchBar
          searchTerm={searchTerm}
          onSearchChange={onSearchChange}
          onClear={onClear}
          message={"Search Keywords..."}
        />
      </div>

      <div className="table-container">
        <KeywordTable
          keywords={keywordsToShow}
          selectedKeyword={selectedKeyword}
          onKeywordClick={onKeywordClick}
        />
      </div>
    </div>
  );
}