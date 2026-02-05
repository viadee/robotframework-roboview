import * as vscode from "vscode";

import { RoboViewPanel } from "./roboViewPanel";
import { LifecycleManager } from "./services/lifecycleManager";

export class CommandHandler {
  public static registerCommands(
    context: vscode.ExtensionContext,
    apiUrl: string,
    lifecycleManager: LifecycleManager,
    currentPanel: vscode.WebviewPanel | undefined,
  ): void {
    context.subscriptions.push(
      vscode.commands.registerCommand("roboview.show-monitor", () =>
        RoboViewPanel.render(context.extensionUri, apiUrl),
      ),
      vscode.commands.registerCommand("roboview.start", () =>
        lifecycleManager.startRoboView(currentPanel),
      ),

      vscode.commands.registerCommand("roboview.restart", () =>
        lifecycleManager.restartRoboView(currentPanel),
      ),
    );
  }
}
