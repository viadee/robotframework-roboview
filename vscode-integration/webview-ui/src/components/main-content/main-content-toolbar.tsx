import React, { ChangeEvent } from "react";
import { SortOption } from "../../types/toolbar";

interface ToolbarProps {
  sortBy: string;
  onSortChange: (sort: string) => void;
  options: SortOption[];
}

export default function Toolbar({
  sortBy,
  onSortChange,
  options,
}: ToolbarProps) {
  return (
    <div className="toolbar">
      <select
        value={sortBy}
        onChange={(e: ChangeEvent<HTMLSelectElement>) =>
          onSortChange(e.target.value)
        }
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </div>
  );
}
