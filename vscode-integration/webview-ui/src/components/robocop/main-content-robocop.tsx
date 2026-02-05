import React from "react";
import SearchBar from "../main-content/main-content-searchbar";
import Toolbar from "../main-content/main-content-toolbar";
import RobocopMessageTable from "../robocop/robocop-message-table";
import { SortOption } from "../../types/toolbar";
import { RobocopMessage } from "../../types/robocop";
import {
  filterMessagesBySearch,
  filterMessagesByType,
  sortRobocopMessages,
} from "../../utilities/robocop_utils";

const robocopMessageSortOptions: SortOption[] = [
  { value: "sort", label: "Sort: Default" },
  { value: "name_asc", label: "Sort: Name (A-Z)" },
  { value: "name_desc", label: "Sort: Name (Z-A)" },
  { value: "severity_high", label: "Sort: Severity (High-Low)" },
  { value: "severity_low", label: "Sort: Severity (Low-High)" },
];

interface MainContentProps {
  robocopMessages: RobocopMessage[];
  currentFilter: string;
  searchTerm: string;
  sortBy: string;
  onSortChange: (sort: string) => void;
  onSearchChange: (value: string) => void;
  onClear: () => void;
  selectedMessage: RobocopMessage | null;
  onMessageClick: (message: RobocopMessage) => void;
}

export default function MainContentRobocopMessages({
  robocopMessages,
  currentFilter,
  searchTerm,
  sortBy,
  onSortChange,
  onSearchChange,
  onClear,
  selectedMessage,
  onMessageClick,
}: MainContentProps) {
  let messagesToShow: RobocopMessage[] = [];

  messagesToShow = filterMessagesByType(robocopMessages, currentFilter);
  messagesToShow = filterMessagesBySearch(messagesToShow, searchTerm);
  messagesToShow = sortRobocopMessages(messagesToShow, sortBy);

  if (!messagesToShow) {
    return (
      <div className="main-content">
        <div className="keyword-placeholder">
          <div className="placeholder-icon">📝</div>
          <h2>No Robocop Message Selected</h2>
          <p>Please follow these steps to open the Robocop Message Overview:</p>
          <ol className="placeholder-steps">
            <li>
              Select a <strong>Filter</strong> Sidebar to group your Messages
              according to category or severity
            </li>
            <li>
              Click on a Message to view its <strong>details</strong>
            </li>
          </ol>
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
          options={robocopMessageSortOptions}
        />
        <SearchBar
          searchTerm={searchTerm}
          onSearchChange={onSearchChange}
          onClear={onClear}
          message={"Search Messages..."}
        />
      </div>

      <div className="table-container">
        <RobocopMessageTable
          messages={messagesToShow}
          selectedMessage={selectedMessage}
          onMessageClick={onMessageClick}
        />
      </div>
    </div>
  );
}
