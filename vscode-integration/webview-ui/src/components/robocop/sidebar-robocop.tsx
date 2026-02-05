import React from "react";
import FilterGroup from "../sidebar/filter-group";

interface RobocopSidebarProps {
  calculateCountsForCategoryFilter: () => any[];
  calculateCountsForSeverityFilter: () => any[];
  currentFilter: string;
  setCurrentFilter: (filter: string) => void;
}

export default function RobocopSidebar({
  calculateCountsForCategoryFilter,
  calculateCountsForSeverityFilter,
  currentFilter,
  setCurrentFilter,
}: RobocopSidebarProps) {
  return (
    <div className="sidebar">
      <FilterGroup
        title="Category Filter"
        items={calculateCountsForCategoryFilter()}
        currentFilter={currentFilter}
        onFilterChange={setCurrentFilter}
      />
      <FilterGroup
        title="Severity Filter"
        items={calculateCountsForSeverityFilter()}
        currentFilter={currentFilter}
        onFilterChange={setCurrentFilter}
      />
    </div>
  );
}
