import React from "react";

interface DetailsSectionTableProps {
  title: string;
  children: React.ReactNode;
  className?: string;
}

export default function DetailsSectionTable({
  title,
  children,
  className = "",
}: DetailsSectionTableProps) {
  return (
    <div className={`details-section ${className}`}>
      <h3>{title}</h3>
      <div className="usage-table-container">{children}</div>
    </div>
  );
}
