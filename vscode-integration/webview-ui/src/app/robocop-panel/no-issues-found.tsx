import { SearchX } from "lucide-react";
import { EmptyStateMessage } from "@/app/shared/empty-state-message";

export function NoRobocopIssuesFound() {
  return (
    <EmptyStateMessage
      title="No Robocop Issues Found"
      icon={<SearchX />}
      description={
        <p className="mb-2">No Robocop issues found for the selected filter</p>
      }
    />
  );
}
