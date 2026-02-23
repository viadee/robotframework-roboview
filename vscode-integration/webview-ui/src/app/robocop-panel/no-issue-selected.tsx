import { BadgeAlert } from "lucide-react";
import { EmptyStateMessage } from "@/app/shared/empty-state-message";

export function NoRobocopIssueSelected() {
  return (
    <EmptyStateMessage
      title="No Robocop Issue Selected"
      icon={<BadgeAlert />}
      description={
        <p className="mb-2">
          Please select a Robocop issue from the table to view its details
        </p>
      }
    />
  );
}
