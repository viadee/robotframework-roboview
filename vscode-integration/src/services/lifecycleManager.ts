import { PythonEnvironmentManager } from "./pythonEnvironmentManager";
import { BackendConnectionManager } from "./backendConnectionManager";
import vscode from "vscode";
import { RoboViewControlProvider } from "../views";
import { RoboViewPanel } from "../roboViewPanel";

export class LifecycleManager {
  private backendConnectionManager: BackendConnectionManager;
  private roboViewControlProvider: RoboViewControlProvider;

  constructor(
    backendConnectionManager: BackendConnectionManager,
    roboViewControlProvider: RoboViewControlProvider,
  ) {
    this.backendConnectionManager = backendConnectionManager;
    this.roboViewControlProvider = roboViewControlProvider;
  }

  public async startRoboView(
    currentPanel: vscode.WebviewPanel | undefined,
  ): Promise<void> {
    await vscode.window.withProgress(
      {
        location: vscode.ProgressLocation.Notification,
        title: "Starting RoboView",
        cancellable: false,
      },
      async (progress) => {
        progress.report({
          increment: 0,
          message: "Checking Python environment...",
        });
        const pythonInterpreterPath: string =
          await PythonEnvironmentManager.checkPythonEnvironment();

        if (await this.backendConnectionManager.isServerRunning()) {
          progress.report({ increment: 100, message: "Done!" });
          vscode.commands.executeCommand("roboview.show-monitor");
          this.roboViewControlProvider.setExtensionReady(true);
          return;
        }

        if (
          pythonInterpreterPath !== "" ||
          !(await this.backendConnectionManager.isServerRunning())
        ) {
          try {
            progress.report({ increment: 20, message: "Starting server..." });
            const serverStarted =
              await this.backendConnectionManager.startServer(
                pythonInterpreterPath,
              );

            if (!serverStarted) {
              vscode.window.showErrorMessage("Failed to start server.");
              return;
            }

            progress.report({
              increment: 40,
              message: "Waiting for server...",
            });
            await this.backendConnectionManager.waitForServerReady(100000);

            progress.report({
              increment: 70,
              message: "Initializing server...",
            });
            await this.backendConnectionManager.initializeServer(currentPanel);

            progress.report({ increment: 100, message: "Done!" });
            vscode.commands.executeCommand("roboview.show-monitor");
            this.roboViewControlProvider.setExtensionReady(true);
          } catch (error) {
            vscode.window.showErrorMessage(
              `Failed to start server: ${error instanceof Error ? error.message : String(error)}`,
            );
            return;
          }
        } else {
          vscode.window.showErrorMessage(
            "Not a valid Python Interpreter Path chosen.",
          );
          return;
        }
      },
    );
  }

  public async restartRoboView(): Promise<void> {
    RoboViewPanel.currentPanel?.dispose();
    vscode.commands.executeCommand("workbench.action.restartExtensionHost");
  }
}
