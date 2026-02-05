import vscode from "vscode";

export class PythonEnvironmentManager {
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
}
