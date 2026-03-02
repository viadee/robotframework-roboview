import { Badge } from "@/components/ui/badge";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { FileUsage } from "@/types/keywords";
import { vscode } from "@/utilities/vscode";

interface DetailsUsageTableProps {
  files: FileUsage[];
}

export function DetailsUsageTable({ files }: DetailsUsageTableProps) {
  const handleFileClick = (event: React.MouseEvent, filePath: string) => {
    if (event.ctrlKey || event.metaKey) {
      event.stopPropagation();
      vscode.postMessage({ command: "openFile", filePath });
    }
  };

  return (
    <div className="overflow-hidden rounded-md border border-border">
      <div className="max-h-90 overflow-y-auto">
        <Table className="table-fixed">
          <TableHeader>
            <TableRow>
              <TableHead className="px-3 py-2 text-xs uppercase tracking-wider">
                File
              </TableHead>
              <TableHead className="w-20 px-3 py-2 text-right text-xs uppercase tracking-wider">
                Count
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {files.length === 0 && (
              <TableRow>
                <TableCell
                  colSpan={2}
                  className="px-3 py-3 text-sm text-muted-foreground"
                >
                  No usage found
                </TableCell>
              </TableRow>
            )}

            {files.map((file) => (
              <TableRow key={file.path}>
                <TableCell
                  className="max-w-0 px-3 py-2 text-sm"
                  title={file.path}
                  onClick={(event) => handleFileClick(event, file.path)}
                >
                  <span className="block truncate cursor-pointer text-foreground/90 hover:text-primary hover:underline">
                    {file.file_name}
                  </span>
                </TableCell>
                <TableCell className="w-20 px-3 py-2 text-right">
                  <Badge className="bg-chart-1/30 px-2 py-0.5 text-xs text-foreground">
                    {file.usages}
                  </Badge>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
