import React from "react";
import DetailsHeader from "../details-panel/details-header";
import DetailsSectionText from "../details-panel/details-section-text";
import { RobocopMessage } from "../../types/robocop";

interface DetailsPanelProps {
  selectedMessage: RobocopMessage | null;
}

export default function DetailsPanelRobocopMessage({
  selectedMessage,
}: DetailsPanelProps) {
  return (
    <div className="details-panel">
      <DetailsHeader
        title={selectedMessage?.rule_id || "Select a Robocop Message"}
      />

      <div className="details-content">
        <DetailsSectionText
          title="General Rule Message"
          content={selectedMessage?.rule_message}
          emptyMessage="No rule message defined"
        />
        <DetailsSectionText
          title="Specific Error Message"
          content={selectedMessage?.message}
          emptyMessage="No error message defined"
        />
        <DetailsSectionText
          title="Affected Code Snippet"
          content={selectedMessage?.code}
          emptyMessage="No code found"
        />
      </div>
    </div>
  );
}
