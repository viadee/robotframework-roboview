import { CollapsibleFilterSection } from "@/components/panel-section/collapsible-filter-section";
import { NoRobocopIssueSelected } from "./no-issue-selected";
import { DetailsSectionText } from "./details-section-text";
import { RobocopMessage } from "@/types/robocop";
import {
  BadgeAlert,
  CircleAlert,
  Code2,
  MessageCircleWarning,
} from "lucide-react";

interface DetailsPanelRobocopProps {
  selectedMessage: RobocopMessage | null;
}

export function DetailsPanelRobocop({
  selectedMessage,
}: DetailsPanelRobocopProps) {
  return (
    <div className="flex h-full flex-col bg-background">
      <div className="border-b border-border px-4 py-3">
        <h2 className="flex items-center gap-2 text-xl font-semibold tracking-tight">
          <BadgeAlert className="size-5 shrink-0 text-orange-400" />
          {selectedMessage?.rule_id ?? "Select a Robocop Message"}
        </h2>
      </div>

      {!selectedMessage ? (
        <NoRobocopIssueSelected />
      ) : (
        <div className="flex-1 space-y-5 overflow-auto px-4 py-4">
          <CollapsibleFilterSection
            title="General Rule Message"
            icon={
              <MessageCircleWarning className="size-4 shrink-0 text-amber-400" />
            }
          >
            <DetailsSectionText
              content={selectedMessage.rule_message}
              emptyMessage="No rule message defined"
            />
          </CollapsibleFilterSection>

          <CollapsibleFilterSection
            title="Specific Error Message"
            icon={<CircleAlert className="size-4 shrink-0 text-destructive" />}
          >
            <DetailsSectionText
              content={selectedMessage.message}
              emptyMessage="No error message defined"
            />
          </CollapsibleFilterSection>

          <CollapsibleFilterSection
            title="Affected Code Snippet"
            icon={<Code2 className="size-4 shrink-0 text-blue-400" />}
          >
            <DetailsSectionText
              content={selectedMessage.code}
              emptyMessage="No code found"
              codeBlock
            />
          </CollapsibleFilterSection>
        </div>
      )}
    </div>
  );
}
