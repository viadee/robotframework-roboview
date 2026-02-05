import React from "react";
import { RobocopMessage } from "../../types/robocop";
import { vscode } from "../../utilities/vscode";

interface RobocopTableProps {
  messages: RobocopMessage[];
  selectedMessage: RobocopMessage | null;
  onMessageClick: (message: RobocopMessage) => void;
}

export default function RobocopMessageTable({
  messages,
  selectedMessage,
  onMessageClick,
}: RobocopTableProps) {
  const handleFileClick = (
    e: React.MouseEvent,
    filePath: string,
    line?: number,
  ) => {
    if (e.ctrlKey || e.metaKey) {
      e.stopPropagation();
      vscode.postMessage({
        command: "openFile",
        filePath: filePath,
        line: line,
      });
    }
  };

  return (
    <table>
      <thead>
        <tr>
          <th>Rule ID</th>
          <th>Message</th>
          <th className="center-align">Source</th>
          <th className="center-align">Severity</th>
        </tr>
      </thead>
      <tbody>
        {messages.map((messageData: RobocopMessage) => {
          const { message_id, rule_id, message, severity, file_name, source } =
            messageData;
          const iconClass =
            severity === "E" ? "E" : severity === "W" ? "W" : "info";
          const iconLetter = severity;
          const isSelected = selectedMessage?.message_id === message_id;

          return (
            <tr
              key={message_id}
              className={isSelected ? "selected" : ""}
              onClick={() => onMessageClick(messageData)}
            >
              <td>
                <div className="keyword-name">
                  <span className={`keyword-icon ${iconClass}`}>
                    {iconLetter}
                  </span>
                  {rule_id}
                </div>
              </td>
              <td>{message}</td>
              <td>
                <div
                  className="path-scroll"
                  onClick={(e) => handleFileClick(e, source)}
                  style={{ cursor: "pointer" }}
                  title={source}
                >
                  <span className="path">{file_name}</span>
                </div>
              </td>
              <td>{severity}</td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
}
