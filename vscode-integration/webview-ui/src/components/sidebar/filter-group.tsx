import React from "react";

interface FilterItem {
  id: string;
  label: string;
  count: number;
}

interface FilterGroupProps {
  title: string;
  items: FilterItem[];
  currentFilter: string;
  onFilterChange: (filter: string) => void;
}

export default function FilterGroup({
  title,
  items,
  currentFilter,
  onFilterChange,
}: FilterGroupProps) {
  return (
    <div className="filter-group">
      <h3>{title}</h3>
      {items.map((item) => (
        <div
          key={item.id}
          className={`filter-item ${currentFilter === item.id ? "active" : ""}`}
          onClick={() => onFilterChange(item.id)}
        >
          <span>{item.label}</span>
          <span className="count">{item.count}</span>
        </div>
      ))}
    </div>
  );
}
