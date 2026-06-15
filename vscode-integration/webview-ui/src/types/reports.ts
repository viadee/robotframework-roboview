export type ReportType = "summary";

export type ExportFormat = "html";

export interface ReportGenerateRequest {
  author?: string;
}

export interface ReportStatusResponse {
  report_id: string;
  status: "pending" | "completed" | "failed";
  download_url?: string;
  error_message?: string;
  file_size?: number;
  created_at?: string;
}

export interface AvailableReport {
  report_id: string;
  report_type: ReportType;
  export_format: ExportFormat;
  created_at: string;
  file_size?: number;
  status: string;
}
