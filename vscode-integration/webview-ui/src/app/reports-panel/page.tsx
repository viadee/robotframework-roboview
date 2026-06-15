import { useState } from "react";
import { vscode } from "@/utilities/vscode";
import {
  ReportStatusResponse,
  AvailableReport,
} from "@/types/reports";
import { useMessageListener } from "@/hooks/useMessageListener";
import { Button } from "@/components/ui/button";
import {
  FileCode2,
  Download,
  Loader2,
  CheckCircle2,
  XCircle,
  ClipboardList,
} from "lucide-react";
import { cn } from "@/lib/utils";

function formatBytes(bytes: number | undefined): string {
  if (!bytes) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(iso: string | undefined): string {
  if (!iso) return "";
  return new Date(iso).toLocaleString();
}

export default function ReportsPage() {
  const [author, setAuthor] = useState<string>("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [lastStatus, setLastStatus] = useState<ReportStatusResponse | null>(
    null,
  );
  const [availableReports, setAvailableReports] = useState<AvailableReport[]>(
    [],
  );

  useMessageListener({
    reportGenerated: (message) => {
      setLastStatus(message.status as ReportStatusResponse);
      setIsGenerating(false);
      // Refresh list after generation
      vscode.postMessage({ command: "getAvailableReports" });
    },
    reportError: (message) => {
      setLastStatus({
        report_id: "",
        status: "failed",
        error_message: message.error,
      });
      setIsGenerating(false);
    },
    availableReports: (message) => {
      setAvailableReports(message.reports as AvailableReport[]);
    },
  });

  function handleGenerate() {
    setIsGenerating(true);
    setLastStatus(null);
    vscode.postMessage({
      command: "generateReport",
      author: author.trim() || undefined,
    });
  }

  function handleDownload(reportId: string) {
    vscode.postMessage({ command: "downloadReport", reportId });
  }

  function handleDelete(reportId: string) {
    vscode.postMessage({ command: "deleteReport", reportId });
    setAvailableReports((prev) => prev.filter((r) => r.report_id !== reportId));
  }

  // Load available reports on first render
  useState(() => {
    vscode.postMessage({ command: "getAvailableReports" });
  });

  return (
    <div className="mx-auto flex h-full w-full max-w-4xl flex-col gap-6 overflow-y-auto p-6">
      {/* Generate Section */}
      <section className="rounded-lg border border-border bg-card p-5">
        <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold text-foreground">
          <ClipboardList className="h-4 w-4 text-blue-400" />
          Generate Summary Report
        </h2>

        <p className="mb-4 text-xs text-muted-foreground">
          Generate a comprehensive HTML report including project health assessment,
          KPIs, keyword analysis, and code quality issues.
        </p>

        {/* Author */}
        <p className="mb-2 text-xs font-medium text-muted-foreground">
          Author (optional)
        </p>
        <input
          type="text"
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          placeholder="e.g. John Doe"
          className="mb-4 w-full rounded-md border border-border bg-background px-3 py-1.5 text-xs text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-primary"
        />

        {/* Generate button */}
        <Button
          size="sm"
          onClick={handleGenerate}
          disabled={isGenerating}
          className="gap-2"
        >
          {isGenerating ? (
            <Loader2 className="h-3.5 w-3.5 animate-spin" />
          ) : (
            <ClipboardList className="h-3.5 w-3.5" />
          )}
          {isGenerating ? "Generating…" : "Generate Report"}
        </Button>

        {/* Status feedback */}
        {lastStatus && (
          <div
            className={cn(
              "mt-3 flex items-start gap-2 rounded-md border p-3 text-xs",
              lastStatus.status === "completed"
                ? "border-green-600/40 bg-green-950/30 text-green-400"
                : "border-red-600/40 bg-red-950/30 text-red-400",
            )}
          >
            {lastStatus.status === "completed" ? (
              <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            ) : (
              <XCircle className="mt-0.5 h-3.5 w-3.5 shrink-0" />
            )}
            <span>
              {lastStatus.status === "completed" ? (
                <>
                  Report generated successfully
                  {lastStatus.file_size
                    ? ` (${formatBytes(lastStatus.file_size)})`
                    : ""}
                  .{" "}
                  {lastStatus.download_url && lastStatus.report_id && (
                    <button
                      onClick={() =>
                        handleDownload(lastStatus.report_id)
                      }
                      className="underline underline-offset-2 hover:opacity-80"
                    >
                      Download
                    </button>
                  )}
                </>
              ) : (
                lastStatus.error_message ?? "Report generation failed."
              )}
            </span>
          </div>
        )}
      </section>

      {/* Available Reports */}
      <section className="rounded-lg border border-border bg-card p-5">
        <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold text-foreground">
          <Download className="h-4 w-4 text-amber-400" />
          Available Reports
        </h2>

        {availableReports.length === 0 ? (
          <p className="text-xs text-muted-foreground">
            No reports generated yet.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-border text-muted-foreground">
                  <th className="pb-2 text-left font-medium">Report</th>
                  <th className="pb-2 text-left font-medium">Created</th>
                  <th className="pb-2 text-right font-medium">Size</th>
                  <th className="pb-2 text-right font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {availableReports.map((report) => (
                  <tr
                    key={report.report_id}
                    className="border-b border-border/50 last:border-0"
                  >
                    <td className="py-2 pr-4">
                      <div className="flex items-center gap-2">
                        <FileCode2 className="h-3.5 w-3.5 text-blue-400" />
                        <span>Summary Report</span>
                      </div>
                    </td>
                    <td className="py-2 pr-4 text-muted-foreground">
                      {formatDate(report.created_at)}
                    </td>
                    <td className="py-2 pr-4 text-right text-muted-foreground">
                      {formatBytes(report.file_size)}
                    </td>
                    <td className="py-2 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <button
                          onClick={() =>
                            handleDownload(report.report_id)
                          }
                          className="text-blue-400 hover:text-blue-300"
                          title="Download"
                        >
                          <Download className="h-3.5 w-3.5" />
                        </button>
                        <button
                          onClick={() => handleDelete(report.report_id)}
                          className="text-red-400 hover:text-red-300"
                          title="Delete"
                        >
                          <XCircle className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <Button
          variant="ghost"
          size="sm"
          className="mt-3 text-xs"
          onClick={() => vscode.postMessage({ command: "getAvailableReports" })}
        >
          Refresh
        </Button>
      </section>
    </div>
  );
}
