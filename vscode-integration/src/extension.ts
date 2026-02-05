import vscode from "vscode";

import { BackendConnectionManager } from "./services/backendConnectionManager";

import { CommandHandler } from "./commands";
import { RoboViewControlProvider } from "./views";
import { LifecycleManager } from "./services/lifecycleManager";

export let currentPanel: vscode.WebviewPanel | undefined;
export const API_BASE_URL: string = "http://127.0.0.1:8000";

let backendConnectionManager: BackendConnectionManager =
  new BackendConnectionManager(API_BASE_URL);

export async function activate(
  context: vscode.ExtensionContext,
): Promise<void> {
  context.subscriptions.push(backendConnectionManager.getServerOutputChannel());

  const roboViewControlProvider = new RoboViewControlProvider();

  const treeView = vscode.window.createTreeView("roboview-controls", {
    treeDataProvider: roboViewControlProvider,
  });
  context.subscriptions.push(treeView, roboViewControlProvider);

  const lifecycleManager: LifecycleManager = new LifecycleManager(
    backendConnectionManager,
    roboViewControlProvider,
  );

  CommandHandler.registerCommands(
    context,
    API_BASE_URL,
    lifecycleManager,
    currentPanel,
  );
  vscode.commands.executeCommand("roboview.start");
}

export function deactivate() {
  backendConnectionManager.killServerProcess();
}
