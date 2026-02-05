import React from "react";
import { FileSelect } from "../../types/files";
import FileSelector from "../sidebar/file-selection";
import FilterGroup from "../sidebar/filter-group";

interface KeywordSidebarProps {
  selectedResource: FileSelect | null;
  all_files: FileSelect[];
  handleResourceChange: (value: FileSelect | null) => void;
  calculateCountsForTypeFilter: () => any[];
  calculateCountsForGlobalFilter: () => any[];
  currentFilter: string;
  setCurrentFilter: (filter: string) => void;
}

export default function KeywordSidebar({
  selectedResource,
  all_files,
  handleResourceChange,
  calculateCountsForTypeFilter,
  calculateCountsForGlobalFilter,
  currentFilter,
  setCurrentFilter,
}: KeywordSidebarProps) {
  return (
    <div className="sidebar">
      <FileSelector
        title="File Selection"
        selectedResource={selectedResource}
        file_list={all_files}
        onResourceChange={handleResourceChange}
      />
      <FilterGroup
        title="Type Filter"
        items={calculateCountsForTypeFilter()}
        currentFilter={currentFilter}
        onFilterChange={setCurrentFilter}
      />
      <FilterGroup
        title="Global Filter"
        items={calculateCountsForGlobalFilter()}
        currentFilter={currentFilter}
        onFilterChange={setCurrentFilter}
      />
    </div>
  );
}
