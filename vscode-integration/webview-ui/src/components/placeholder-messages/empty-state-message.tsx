import { ReactNode } from "react";
import {
  Empty,
  EmptyDescription,
  EmptyHeader,
  EmptyMedia,
  EmptyTitle,
} from "@/components/ui/empty";

interface EmptyStateMessageProps {
  title: string;
  icon: ReactNode;
  description: ReactNode;
}

export function EmptyStateMessage({
  title,
  icon,
  description,
}: EmptyStateMessageProps) {
  return (
    <Empty className="h-full items-center justify-center">
      <EmptyHeader>
        <EmptyMedia variant="icon">{icon}</EmptyMedia>
        <EmptyTitle>{title}</EmptyTitle>
        <EmptyDescription>{description}</EmptyDescription>
      </EmptyHeader>
    </Empty>
  );
}
