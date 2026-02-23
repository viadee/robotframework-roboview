import { IconFolderCode } from "@tabler/icons-react";
import { EmptyStateMessage } from "@/app/shared/empty-state-message";

export function NoFileSelected() {
  return (
    <EmptyStateMessage
      title="No File Selected"
      icon={<IconFolderCode />}
      description={
        <>
          <p className="mb-2">
            Please follow these steps to open the Keyword Overview:
          </p>
          <ol className="list-decimal text-left space-y-1 pl-5">
            <li>
              Select a <strong>Robot Framework File</strong> from the file
              selection
            </li>
            <li>
              Use the <strong>Type Filter</strong> for filtering in a selected
              file
            </li>
            <li>
              Use the <strong>Global Filter</strong> for filtering across all
              files
            </li>
            <li>
              Click on a Keyword to view its <strong>details</strong>
            </li>
          </ol>
        </>
      }
    />
  );
}
