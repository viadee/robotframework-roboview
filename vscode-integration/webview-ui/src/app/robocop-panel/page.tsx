import { useEffect, useMemo, useState } from "react";
import { AppLayout } from "@/components/layout/layout";
import { useMessageListener } from "@/hooks/useMessageListener";
import { FilterItem } from "@/types/keywords";
import { RobocopMessage } from "@/types/robocop";
import { filterMessagesByType } from "@/utilities/robocop_utils";
import { vscode } from "@/utilities/vscode";
import { SidebarRobocop } from "@/app/robocop-panel/sidebar-robocop";
import { MainContentRobocop } from "@/app/robocop-panel/main-content-robocop";
import { DetailsPanelRobocop } from "@/app/robocop-panel/details-panel-robocop";

export default function RobocopPage() {
  const [allRobocopMessages, setRobocopMessages] = useState<RobocopMessage[]>(
    [],
  );
  const [selectedRobocopMessage, setSelectedRobocopMessage] =
    useState<RobocopMessage | null>(null);
  const [currentFilter, setCurrentFilter] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");
  const [sortBy, setSortBy] = useState("sort");

  useMessageListener({
    robocopMessages: (message) => {
      const robocopMessages = message.messages || [];

      setRobocopMessages(
        robocopMessages.map((robocopMessage: RobocopMessage) => ({
          message_id: robocopMessage.message_id,
          rule_id: robocopMessage.rule_id,
          rule_message: robocopMessage.rule_message,
          message: robocopMessage.message,
          category: robocopMessage.category,
          file_name: robocopMessage.file_name,
          source: robocopMessage.source,
          severity: robocopMessage.severity,
          code: robocopMessage.code,
        })),
      );
    },
  });

  useEffect(() => {
    vscode.postMessage({ command: "getRobocopMessages" });
  }, []);

  const categoryFilters = useMemo<FilterItem[]>(() => {
    const allFilter = {
      id: "all",
      label: "All",
      count: allRobocopMessages.length,
    };

    const categories = [
      { id: "arguments", label: "Arguments" },
      { id: "comments", label: "Comments" },
      { id: "documentation", label: "Documentation" },
      { id: "duplication", label: "Duplication" },
      { id: "errors", label: "Errors" },
      { id: "imports", label: "Imports" },
      { id: "keywords", label: "Keywords" },
      { id: "lengths", label: "Lengths" },
      { id: "miscellaneous", label: "Miscellaneous" },
      { id: "naming", label: "Naming" },
      { id: "deprecated", label: "Deprecated" },
      { id: "order", label: "Order" },
      { id: "spacing", label: "Spacing" },
      { id: "tags", label: "Tags" },
      { id: "variables", label: "Variables" },
      { id: "annotations", label: "Annotations" },
    ]
      .map((category) => ({
        ...category,
        count: filterMessagesByType(allRobocopMessages, category.id).length,
      }))
      .filter((category) => category.count > 0)
      .sort((left, right) => right.count - left.count);

    return [allFilter, ...categories];
  }, [allRobocopMessages]);

  const severityFilters = useMemo<FilterItem[]>(() => {
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
  }, [allRobocopMessages]);

  const handleMessageSelect = (message: RobocopMessage) => {
    setSelectedRobocopMessage(message);
    vscode.postMessage({
      command: "getRobocopMessage",
      messageUuid: message.message_id,
    });
  };

  const handleClearSearch = () => {
    setSearchTerm("");
  };

  return (
    <AppLayout
      sidebar={
        <SidebarRobocop
          categoryFilters={categoryFilters}
          severityFilters={severityFilters}
          currentFilter={currentFilter}
          onFilterChange={setCurrentFilter}
        />
      }
      content={
        <MainContentRobocop
          robocopMessages={allRobocopMessages}
          currentFilter={currentFilter}
          searchTerm={searchTerm}
          sortBy={sortBy}
          selectedMessage={selectedRobocopMessage}
          onSortChange={setSortBy}
          onSearchChange={setSearchTerm}
          onClearSearch={handleClearSearch}
          onMessageSelect={handleMessageSelect}
        />
      }
      details={<DetailsPanelRobocop selectedMessage={selectedRobocopMessage} />}
    />
  );
}
