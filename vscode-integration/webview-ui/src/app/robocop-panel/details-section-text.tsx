interface DetailsSectionTextProps {
  content?: string;
  emptyMessage: string;
  codeBlock?: boolean;
}

export function DetailsSectionText({
  content,
  emptyMessage,
  codeBlock = false,
}: DetailsSectionTextProps) {
  if (codeBlock) {
    return (
      <pre className="overflow-auto rounded-md border border-border bg-input px-3 py-2 text-sm leading-relaxed whitespace-pre-wrap text-foreground">
        {content || emptyMessage}
      </pre>
    );
  }

  return (
    <div className="rounded-md border border-border bg-input px-3 py-2 text-sm leading-relaxed text-foreground">
      {content || emptyMessage}
    </div>
  );
}
