import vscode from "vscode";
import { spawnSync } from "child_process";

export class PythonEnvironmentManager {
  private static readonly PACKAGE_NAME = "robotframework-roboview";
  private static readonly REFERENCE_VERSION = "0.0.4";

  public static async checkPythonEnvironment(): Promise<string> {
    const pythonExt = vscode.extensions.getExtension("ms-python.python");
    if (!pythonExt) {
      vscode.window.showErrorMessage(
        "Python Extension (ms-python.python) is not installed.",
      );
      return "";
    }

    await pythonExt.activate();
    const pythonApi = pythonExt.exports;
    const execDetails = pythonApi.settings.getExecutionDetails();
    const pythonPath = execDetails.execCommand[0];

    if (!pythonPath) {
      vscode.window.showErrorMessage("Python-Interpreter could not be found.");
      return "";
    } else {
      return pythonPath;
    }
  }

  public static async validateBackendPackageForStartup(
    pythonInterpreterPath: string,
    outputChannel: vscode.OutputChannel,
  ): Promise<boolean> {
    if (!pythonInterpreterPath) {
      vscode.window.showErrorMessage("Python-Interpreter could not be found.");
      return false;
    }

    outputChannel.appendLine("Checking Python pip availability...");
    const pipVersionResult = spawnSync(
      pythonInterpreterPath,
      ["-m", "pip", "--version"],
      { encoding: "utf-8" },
    );

    if (pipVersionResult.status !== 0) {
      outputChannel.appendLine(
        "pip is not available. Skipping package check and continuing with backend startup.",
      );
      return true;
    }

    outputChannel.appendLine(
      "Checking backend package version via pip show...",
    );

    const installedVersion = this.getInstalledPackageVersion(
      pythonInterpreterPath,
      this.PACKAGE_NAME,
    );

    if (!installedVersion) {
      this.showPackageActionMessage(
        `Python package '${this.PACKAGE_NAME}' is not installed. Please install it before starting RoboView again.`,
        `${pythonInterpreterPath} -m pip install "${this.PACKAGE_NAME}"`,
      );
      return false;
    }

    if (installedVersion !== this.REFERENCE_VERSION) {
      this.showPackageActionMessage(
        `Python package '${this.PACKAGE_NAME}' has version ${installedVersion}, but ${this.REFERENCE_VERSION} is required. Please update it before starting RoboView again.`,
        `${pythonInterpreterPath} -m pip install --upgrade "${this.PACKAGE_NAME}"`,
      );
      return false;
    }

    outputChannel.appendLine("Backend package is already up to date.");
    return true;
  }

  private static getInstalledPackageVersion(
    pythonInterpreterPath: string,
    packageName: string,
  ): string {
    const showResult = spawnSync(
      pythonInterpreterPath,
      ["-m", "pip", "show", packageName],
      { encoding: "utf-8" },
    );

    if (showResult.status !== 0) {
      return "";
    }

    const versionLine = showResult.stdout
      ?.split(/\r?\n/)
      .find((line) => line.startsWith("Version:"));

    return versionLine?.replace("Version:", "").trim() ?? "";
  }

  private static showPackageActionMessage(
    message: string,
    command: string,
  ): void {
    const copyCommand = "Copy command";
    void vscode.window
      .showWarningMessage(`${message} Command: ${command}`, copyCommand)
      .then(async (selectedAction) => {
        if (selectedAction === copyCommand) {
          await vscode.env.clipboard.writeText(command);
          vscode.window.showInformationMessage(
            "Install command copied to clipboard.",
          );
        }
      });
  }
}
