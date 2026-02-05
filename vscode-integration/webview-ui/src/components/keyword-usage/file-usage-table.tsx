import React from "react";
import { vscode } from "../../utilities/vscode";

interface FileUsage {
  file_name: string;
  path: string;
  usages: number;
}

interface FileUsageTableProps {
  files: FileUsage[];
}

export default function FileUsageTable({ files }: FileUsageTableProps) {
  const handleFileClick = (e: React.MouseEvent, filePath: string) => {
    if (e.ctrlKey || e.metaKey) {
      e.stopPropagation();
      vscode.postMessage({
        command: "openFile",
        filePath: filePath,
      });
    }
  };

  if (!files || files.length === 0) {
    return (
      <table>
        <thead>
          <tr>
            <th>File</th>
            <th>Count</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td colSpan={2} style={{ textAlign: "center", color: "#888" }}>
              No usage found
            </td>
          </tr>
        </tbody>
      </table>
    );
  }

  return (
    <table>
      <thead>
        <tr>
          <th>File</th>
          <th>Count</th>
        </tr>
      </thead>
      <tbody>
        {files.map(({ file_name, path, usages }) => (
          <tr key={file_name}>
            <td
              style={{ color: "#0078d4", cursor: "pointer" }}
              onClick={(e) => handleFileClick(e, path)}
              title={path}
            >
              {file_name}
            </td>
            <td>
              <span className="usage-badge blue">{usages}</span>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
