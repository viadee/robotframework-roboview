import { SearchX } from "lucide-react";
import { EmptyStateMessage } from "@/app/shared/empty-state-message";

export function NoKeywordFound() {
  return (
    <EmptyStateMessage
      title="No Keywords Found"
      icon={<SearchX />}
      description={
        <p className="mb-2">No keywords found for the selected filter</p>
      }
    />
  );
}
