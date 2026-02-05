import React from "react";
import { FileSelect } from "../../types/files";

interface FileSelectorProps {
  title: string;
  selectedResource: FileSelect | null;
  file_list: FileSelect[];
  onResourceChange: (value: FileSelect | null) => void;
  placeholder?: string;
}

export default function FileSelector({
  title,
  selectedResource,
  file_list,
  onResourceChange,
  placeholder = "--- SELECT FILE ---",
}: FileSelectorProps) {
  const robotFiles = file_list
    .filter((name) => name.file_name.endsWith(".robot"))
    .sort((a, b) => a.file_name.localeCompare(b.file_name));

  const resourceFiles = file_list
    .filter((name) => name.file_name.endsWith(".resource"))
    .sort((a, b) => a.file_name.localeCompare(b.file_name));

  return (
    <div className="filter-group">
      <h3>{title}</h3>
      <select
        id="resource"
        className="filter-select"
        value={selectedResource?.file_name || ""}
        onChange={(e) => {
          const fileName = e.target.value;
          if (fileName === "") {
            onResourceChange(null);
          } else {
            const selected = file_list.find((f) => f.file_name === fileName);
            onResourceChange(selected || null);
          }
        }}
      >
        <option value="">{placeholder}</option>
        {resourceFiles.length > 0 && (
          <optgroup label="Resource files">
            {resourceFiles.map((resource) => (
              <option key={resource.path} value={resource.file_name}>
                {resource.file_name}
              </option>
            ))}
          </optgroup>
        )}
        {robotFiles.length > 0 && (
          <optgroup label="Robot files">
            {robotFiles.map((resource) => (
              <option key={resource.path} value={resource.file_name}>
                {resource.file_name}
              </option>
            ))}
          </optgroup>
        )}
      </select>
    </div>
  );
}
