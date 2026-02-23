import { Separator } from "@/components/ui/separator";
import { DetailsSectionTitle } from "@/app/shared/details-section-title";
import { NoRobocopIssueSelected } from "./no-issue-selected";
import { DetailsSectionText } from "./details-section-text";
import { RobocopMessage } from "@/types/robocop";

interface DetailsPanelRobocopProps {
  selectedMessage: RobocopMessage | null;
}

export function DetailsPanelRobocop({
  selectedMessage,
}: DetailsPanelRobocopProps) {
  return (
    <div className="flex h-full flex-col bg-background">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-xl font-semibold tracking-tight">
          {selectedMessage?.rule_id ?? "Select a Robocop Message"}
        </h2>
      </div>

      {!selectedMessage ? (
        <NoRobocopIssueSelected />
      ) : (
        <div className="flex-1 space-y-5 overflow-auto px-4 py-4">
          <div className="space-y-2">
            <DetailsSectionTitle title="General Rule Message" />
            <DetailsSectionText
              content={selectedMessage.rule_message}
              emptyMessage="No rule message defined"
            />
          </div>

          <Separator />

          <div className="space-y-2">
            <DetailsSectionTitle title="Specific Error Message" />
            <DetailsSectionText
              content={selectedMessage.message}
              emptyMessage="No error message defined"
            />
          </div>

          <Separator />

          <div className="space-y-2">
            <DetailsSectionTitle title="Affected Code Snippet" />
            <DetailsSectionText
              content={selectedMessage.code}
              emptyMessage="No code found"
              codeBlock
            />
          </div>
        </div>
      )}
    </div>
  );
}
