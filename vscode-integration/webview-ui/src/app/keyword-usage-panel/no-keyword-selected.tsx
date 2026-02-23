import { KeyRound } from "lucide-react";
import { EmptyStateMessage } from "@/app/shared/empty-state-message";

export function NoKeywordSelected() {
  return (
    <EmptyStateMessage
      title="No Keyword Selected"
      icon={<KeyRound />}
      description={
        <p className="mb-2">
          Please select a keyword from the table to view its details
        </p>
      }
    />
  );
}
