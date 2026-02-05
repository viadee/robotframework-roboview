import React from "react";

interface DetailsHeaderProps {
  title: string;
  subtitle?: string;
}

export default function DetailsHeader({ title, subtitle }: DetailsHeaderProps) {
  return (
    <div className="details-header">
      <h2>{title}</h2>
      {subtitle && <p className="details-subtitle">{subtitle}</p>}
    </div>
  );
}
