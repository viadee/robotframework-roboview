import {
  Disposable,
  Webview,
  WebviewPanel,
  window,
  Uri,
  ViewColumn,
  Range,
} from "vscode";
import axios from "axios";
import { getUri } from "./utils/getUri";
import { getNonce } from "./utils/getNonce";
import { PathManager } from "./services/pathManager";

let roboviewPathManager: PathManager = new PathManager(
  PathManager.getWorkspaceRoot(),
);

export class RoboViewPanel {
  public static currentPanel: RoboViewPanel | undefined;
  private readonly _panel: WebviewPanel;
  private _disposables: Disposable[] = [];
  private _axiosInstance: any;
  private _currentProjectDir: string | undefined;

  private constructor(
    panel: WebviewPanel,
    extensionUri: Uri,
    apiBaseUrl: string,
  ) {
    this._panel = panel;
    this._axiosInstance = axios.create({ baseURL: apiBaseUrl });
    this._currentProjectDir = roboviewPathManager.getCurrentProjectPath();

    roboviewPathManager.onPathChange((newPath) => {
      this._currentProjectDir = newPath;
    });

    this._panel.onDidDispose(() => this.dispose(), null, this._disposables);
    this._panel.webview.html = this._getWebviewContent(
      this._panel.webview,
      extensionUri,
    );
    this._setWebviewMessageListener(this._panel.webview);

    setTimeout(() => {
      if (this._currentProjectDir) {
        this._panel.webview.postMessage({
          command: "projectPath",
          path: this._currentProjectDir,
        });
      }
    }, 100);
  }

  public static render(extensionUri: Uri, apiBaseUrl: string) {
    if (RoboViewPanel.currentPanel) {
      RoboViewPanel.currentPanel._panel.reveal(ViewColumn.One);
    } else {
      const panel = window.createWebviewPanel(
        "KeywordDetails",
        "RoboView Monitor",
        ViewColumn.One,
        {
          enableScripts: true,
          retainContextWhenHidden: true,
          enableFindWidget: true,
          localResourceRoots: [
            Uri.joinPath(extensionUri, "out"),
            Uri.joinPath(extensionUri, "webview-ui/build"),
          ],
        },
      );

      RoboViewPanel.currentPanel = new RoboViewPanel(
        panel,
        extensionUri,
        apiBaseUrl,
      );
    }
  }

  public dispose() {
    RoboViewPanel.currentPanel = undefined;
    this._panel.dispose();

    while (this._disposables.length) {
      const disposable = this._disposables.pop();
      if (disposable) {
        disposable.dispose();
      }
    }
  }

  public static close() {
    if (RoboViewPanel.currentPanel) {
      RoboViewPanel.currentPanel.dispose();
    }
  }

  private _getWebviewContent(webview: Webview, extensionUri: Uri) {
    const scriptUri = getUri(webview, extensionUri, [
      "webview-ui",
      "build",
      "assets",
      "index.js",
    ]);
    const styleUri = getUri(webview, extensionUri, [
      "webview-ui",
      "build",
      "assets",
      "index.css",
    ]);
    const nonce = getNonce();

    return /*html*/ `
      <!DOCTYPE html>
      <html lang="en">
        <head>
          <meta charset="UTF-8">
          <meta name="viewport" content="width=device-width, initial-scale=1.0">
          <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}';">
          <link href="${styleUri}" rel="stylesheet">
          <title>Robot Framework Keyword Manager</title>
        </head>
        <body>
          <div id="root"></div>
          <script nonce="${nonce}" src="${scriptUri}"></script>
        </body>
      </html>
    `;
  }

  private _setWebviewMessageListener(webview: Webview) {
    webview.onDidReceiveMessage(
      async (message: any) => {
        console.log(`Received message: ${JSON.stringify(message)}`);
        try {
          switch (message.command) {
            // ========================================
            // Files Commands
            // ========================================
            case "getRobotFiles": {
              const response = await this._axiosInstance.get(
                "/api/v1/files/robot",
                {
                  params: { project_root_dir: this._currentProjectDir },
                },
              );
              this._panel.webview.postMessage({
                command: "robotFiles",
                files: response.data.robot_files,
              });
              break;
            }

            case "getProjectPath": {
              this._panel.webview.postMessage({
                command: "projectPath",
                path: this._currentProjectDir || "",
              });
              break;
            }

            case "openFile": {
              const filePath = message.filePath;
              const line = message.line || 1;

              if (filePath) {
                const fileUri = Uri.file(filePath);
                window.showTextDocument(fileUri, {
                  preview: false,
                  viewColumn: ViewColumn.Active,
                  selection:
                    line > 1 ? new Range(line - 1, 0, line - 1, 0) : undefined,
                });
              }
              break;
            }

            case "getResourceFiles": {
              const response = await this._axiosInstance.get(
                "/api/v1/files/resource",
                {
                  params: { project_root_dir: this._currentProjectDir },
                },
              );
              this._panel.webview.postMessage({
                command: "resourceFiles",
                files: response.data.resource_files,
              });
              break;
            }

            case "getAllFiles": {
              const response = await this._axiosInstance.get(
                "/api/v1/files/all-files",
                {
                  params: { project_root_dir: this._currentProjectDir },
                },
              );
              this._panel.webview.postMessage({
                command: "allFiles",
                files: response.data.all_files,
              });
              break;
            }

            case "getInitKeywords": {
              const initResponse = await this._axiosInstance.get(
                "/api/v1/keyword-usage/keywords-initialized",
                {
                  params: { file_path: message.filePath },
                },
              );
              this._panel.webview.postMessage({
                command: "initKeywords",
                init_keywords: initResponse.data.initialized_keywords,
              });
              break;
            }

            case "getCalledKeywords": {
              const calledResponse = await this._axiosInstance.get(
                "/api/v1/keyword-usage/keywords-called",
                {
                  params: { file_path: message.filePath },
                },
              );
              this._panel.webview.postMessage({
                command: "calledKeywords",
                called_keywords: calledResponse.data.called_keywords,
              });
              break;
            }

            case "getKeywordUsageRobot": {
              const testResponse = await this._axiosInstance.get(
                "/api/v1/keyword-usage/keyword-usage-robot",
                {
                  params: { keyword_name: message.keyword },
                },
              );
              this._panel.webview.postMessage({
                command: "keywordUsageRobot",
                usage: testResponse.data.keyword_usage_robot,
              });
              break;
            }

            case "getKeywordUsageResource": {
              const resourceResponse = await this._axiosInstance.get(
                "/api/v1/keyword-usage/keyword-usage-resource",
                {
                  params: { keyword_name: message.keyword },
                },
              );
              this._panel.webview.postMessage({
                command: "keywordUsageResource",
                usage: resourceResponse.data.keyword_usage_resource,
              });
              break;
            }

            case "getKeywordSimilarity": {
              const similarityResponse = await this._axiosInstance.get(
                "/api/v1/keyword-usage/keyword-similarity",
                {
                  params: { keyword_name: message.keyword },
                },
              );
              this._panel.webview.postMessage({
                command: "keywordSimilarity",
                similarity: similarityResponse.data.top_n_similar_keywords,
              });
              break;
            }

            case "getKeywordsWithoutDoc": {
              const response = await this._axiosInstance.get(
                "/api/v1/keyword-usage/keywords-without-documentation",
              );
              this._panel.webview.postMessage({
                command: "keywordsWithoutDoc",
                keywords: response.data.keywords_wo_documentation,
              });
              break;
            }

            case "getKeywordsWithoutUsages": {
              const response = await this._axiosInstance.get(
                "/api/v1/keyword-usage/keywords-without-usages",
              );
              this._panel.webview.postMessage({
                command: "keywordsWithoutUsages",
                keywords: response.data.keywords_wo_usages,
              });
              break;
            }

            case "getKeywordDuplicates": {
              const response = await this._axiosInstance.get(
                "/api/v1/keyword-usage/keywords-duplicates",
              );
              this._panel.webview.postMessage({
                command: "keywordDuplicates",
                keywords: response.data.duplicate_keywords,
              });
              break;
            }

            // ========================================
            // Overview Commands
            // ========================================
            case "getKPIs": {
              const response = await this._axiosInstance.get(
                "/api/v1/overview/kpis",
                {
                  params: { project_root_dir: this._currentProjectDir },
                },
              );
              this._panel.webview.postMessage({
                command: "kpis",
                data: response.data,
              });
              break;
            }

            case "getMostUsedKeywords": {
              const response = await this._axiosInstance.get(
                "/api/v1/overview/most-used-keywords",
              );
              this._panel.webview.postMessage({
                command: "mostUsedKeywords",
                mostUsedUser: response.data.most_used_user_keywords,
                mostUsedExternal: response.data.most_used_external_keywords,
              });
              break;
            }

            // ========================================
            // Robocop Commands
            // ========================================
            case "getRobocopMessage": {
              const response = await this._axiosInstance.get(
                "/api/v1/robocop/robocop-message",
                {
                  params: { message_uuid: message.messageUuid },
                },
              );
              this._panel.webview.postMessage({
                command: "robocopMessage",
                message: response.data.message,
              });
              break;
            }

            case "getRobocopMessages": {
              const response = await this._axiosInstance.get(
                "/api/v1/robocop/robocop-messages-all",
              );
              this._panel.webview.postMessage({
                command: "robocopMessages",
                messages: response.data.messages,
              });
              break;
            }

            case "getRobocopIssueSummary": {
              const response = await this._axiosInstance.get(
                "/api/v1/overview/robocop-issue-summary",
              );
              this._panel.webview.postMessage({
                command: "robocopIssueSummary",
                summary: response.data.robocop_issue_summary,
              });
              break;
            }

            default: {
              console.warn(`Unknown command: ${message.command}`);
              this._panel.webview.postMessage({
                command: "error",
                message: `Unknown command: ${message.command}`,
              });
              break;
            }
          }
        } catch (error: any) {
          console.error(`Error processing ${message.command}:`, error);
          const errorMessage =
            error.response?.data?.detail || error.message || "Unknown error";
          window.showErrorMessage(
            `Failed to fetch data for ${message.command}: ${errorMessage}`,
          );
          this._panel.webview.postMessage({
            command: "error",
            originalCommand: message.command,
            message: errorMessage,
          });
        }
      },
      undefined,
      this._disposables,
    );
  }
}
