import React, { useState, useEffect } from "react";
import { vscode } from "../../utilities/vscode";
import { useMessageListener } from "../../hooks/useMessageListener";
import { RobocopMessage } from "../../types/robocop";
import { FilterItem } from "../../types/keywords";
import Layout from "../../components/layout/layout";
import RobocopSidebar from "../../components/robocop/sidebar-robocop";
import MainContentRobocopMessages from "../../components/robocop/main-content-robocop";
import DetailsPanelRobocopMessage from "../../components/robocop/details-panel-robocop";
import { filterMessagesByType } from "../../utilities/robocop_utils";

const RobocopMessageView: React.FC = () => {
  // State
  const [allRobocopMessages, setRobocopMessages] = useState<RobocopMessage[]>(
    [],
  );
  const [selectedRobocopMessage, setSelectedRobocopMessage] =
    useState<RobocopMessage | null>(null);
  const [currentFilter, setCurrentFilter] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [sortBy, setSortBy] = useState<string>("sort");

  useMessageListener({
    robocopMessages: (message) => {
      const rm_messages = message.messages || [];
      setRobocopMessages(
        rm_messages.map((rm: RobocopMessage) => ({
          message_id: rm.message_id,
          rule_id: rm.rule_id,
          rule_message: rm.rule_message,
          message: rm.message,
          category: rm.category,
          file_name: rm.file_name,
          source: rm.source,
          severity: rm.severity,
          code: rm.code,
        })),
      );
    },
  });

  useEffect(() => {
    vscode.postMessage({ command: "getRobocopMessages" });
  }, []);

  const handleRobocopMessageClick = (message: RobocopMessage) => {
    setSelectedRobocopMessage(message);

    vscode.postMessage({
      command: "getRobocopMessage",
      messageUuid: message.message_id,
    });
  };

  const handleClear = () => {
    setSearchTerm("");
  };

  const calculateCountsForCategoryFilter = (): FilterItem[] => {
    const allItem = {
      id: "all",
      label: "All",
      count: allRobocopMessages.length,
    };
    const categories = [
      {
        id: "arguments",
        label: "Arguments",
        count: filterMessagesByType(allRobocopMessages, "arguments").length,
      },
      {
        id: "comments",
        label: "Comments",
        count: filterMessagesByType(allRobocopMessages, "comments").length,
      },
      {
        id: "documentation",
        label: "Documentation",
        count: filterMessagesByType(allRobocopMessages, "documentation").length,
      },
      {
        id: "duplication",
        label: "Duplication",
        count: filterMessagesByType(allRobocopMessages, "duplication").length,
      },
      {
        id: "errors",
        label: "Errors",
        count: filterMessagesByType(allRobocopMessages, "errors").length,
      },
      {
        id: "imports",
        label: "Imports",
        count: filterMessagesByType(allRobocopMessages, "imports").length,
      },
      {
        id: "keywords",
        label: "Keywords",
        count: filterMessagesByType(allRobocopMessages, "keywords").length,
      },
      {
        id: "lengths",
        label: "Lengths",
        count: filterMessagesByType(allRobocopMessages, "lengths").length,
      },
      {
        id: "miscellaneous",
        label: "Miscellaneous",
        count: filterMessagesByType(allRobocopMessages, "miscellaneous").length,
      },
      {
        id: "naming",
        label: "Naming",
        count: filterMessagesByType(allRobocopMessages, "naming").length,
      },
      {
        id: "deprecated",
        label: "Deprecated",
        count: filterMessagesByType(allRobocopMessages, "deprecated").length,
      },
      {
        id: "order",
        label: "Order",
        count: filterMessagesByType(allRobocopMessages, "order").length,
      },
      {
        id: "spacing",
        label: "Spacing",
        count: filterMessagesByType(allRobocopMessages, "spacing").length,
      },
      {
        id: "tags",
        label: "Tags",
        count: filterMessagesByType(allRobocopMessages, "tags").length,
      },
      {
        id: "variables",
        label: "Variables",
        count: filterMessagesByType(allRobocopMessages, "variables").length,
      },
      {
        id: "annotations",
        label: "Annotations",
        count: filterMessagesByType(allRobocopMessages, "annotations").length,
      },
    ]
      .filter((category) => category.count > 0)
      .sort((a, b) => b.count - a.count);
    return [allItem, ...categories];
  };

  const calculateCountsForSeverityFilter = (): FilterItem[] => {
    return [
      {
        id: "info",
        label: "Info",
        count: filterMessagesByType(allRobocopMessages, "info").length,
      },
      {
        id: "warning",
        label: "Warning",
        count: filterMessagesByType(allRobocopMessages, "warning").length,
      },
      {
        id: "error",
        label: "Error",
        count: filterMessagesByType(allRobocopMessages, "error").length,
      },
    ];
  };

  return (
    <Layout
      sidebar={
        <RobocopSidebar
          calculateCountsForCategoryFilter={calculateCountsForCategoryFilter}
          calculateCountsForSeverityFilter={calculateCountsForSeverityFilter}
          currentFilter={currentFilter}
          setCurrentFilter={setCurrentFilter}
        />
      }
      mainContent={
        <MainContentRobocopMessages
          robocopMessages={allRobocopMessages}
          currentFilter={currentFilter}
          searchTerm={searchTerm}
          sortBy={sortBy}
          onSortChange={setSortBy}
          onSearchChange={setSearchTerm}
          onClear={handleClear}
          selectedMessage={selectedRobocopMessage}
          onMessageClick={handleRobocopMessageClick}
        />
      }
      detailsPanel={
        <DetailsPanelRobocopMessage selectedMessage={selectedRobocopMessage} />
      }
    />
  );
};
export default RobocopMessageView;
