import React from "react";

interface DetailsSectionTextProps {
  title: string;
  content: string | React.ReactNode;
  emptyMessage?: string;
  className?: string;
}

export default function DetailsSectionText({
  title,
  content,
  emptyMessage = "No content available",
  className = "",
}: DetailsSectionTextProps) {
  const displayContent = content || emptyMessage;

  return (
    <div className={`details-section ${className}`}>
      <h3>{title}</h3>
      <div className="section-content">{displayContent}</div>
    </div>
  );
}
