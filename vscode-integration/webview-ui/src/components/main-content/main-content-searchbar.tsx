import React, { ChangeEvent } from "react";

interface SearchBarProps {
  searchTerm: string;
  onSearchChange: (value: string) => void;
  onClear: () => void;
  message: string;
}

export default function SearchBar({
  searchTerm,
  onSearchChange,
  onClear,
  message,
}: SearchBarProps) {
  return (
    <div className="search-bar-container">
      <div className="search-box">
        <input
          type="text"
          placeholder={message}
          value={searchTerm}
          onChange={(e: ChangeEvent<HTMLInputElement>) =>
            onSearchChange(e.target.value)
          }
        />
      </div>
      <button onClick={onClear}>Clear</button>
    </div>
  );
}
