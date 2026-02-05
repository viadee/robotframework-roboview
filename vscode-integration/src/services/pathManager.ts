import path from "path";
import vscode from "vscode";

export class PathManager {
  private currentPath: string;
  private listeners: ((newPath: string) => void)[] = [];

  constructor(projectPath: string) {
    this.currentPath = projectPath;
  }

  public getCurrentProjectPath(): string {
    return this.currentPath.split(path.sep).join(path.posix.sep);
  }

  public onPathChange(listener: (newPath: string) => void): () => void {
    this.listeners.push(listener);
    return () => {
      const idx = this.listeners.indexOf(listener);
      if (idx !== -1) {
        this.listeners.splice(idx, 1);
      }
    };
  }

  public static getWorkspaceRoot(): string {
    const workspaceFolders = vscode.workspace.workspaceFolders;
    return workspaceFolders?.length ? workspaceFolders[0].uri.fsPath : "";
  }
}
