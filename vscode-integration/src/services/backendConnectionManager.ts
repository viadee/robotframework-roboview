import axios from "axios";
import * as vscode from "vscode";
import { spawn, spawnSync, ChildProcess } from "child_process";

import { PathManager } from "./pathManager";
import { RobocopConfigFinder } from "./robocopConfigManager";

export class BackendConnectionManager {
  private readonly apiServerUrl: string;
  private readonly serverOutputChannel: vscode.OutputChannel;
  private serverProcess: ChildProcess | null;

  constructor(
    apiServerUrl: string = "http://127.0.0.1:8000",
    OutputChannelName: string = "RoboView Server",
    serverProcess: ChildProcess | null = null,
  ) {
    this.apiServerUrl = apiServerUrl;
    this.serverOutputChannel =
      vscode.window.createOutputChannel(OutputChannelName);
    this.serverProcess = serverProcess;
  }

  public async waitForServerReady(timeoutMs: number): Promise<boolean> {
    const start = Date.now();
    const retryDelay = 500;

    while (Date.now() - start < timeoutMs) {
      try {
        await axios.get(`${this.apiServerUrl}/api/v1/system/health`);
        return true;
      } catch {
        await new Promise((res) => setTimeout(res, retryDelay));
      }
    }

    throw new Error(
      `Timeout: Server ${this.apiServerUrl} not accessible after ${timeoutMs / 1000} seconds.`,
    );
  }

  public async startServer(pythonInterpreterPath: string): Promise<boolean> {
    const workspaceFolder = PathManager.getWorkspaceRoot();

    if (!workspaceFolder) {
      vscode.window.showErrorMessage("No Workspace Folder Selected.");
      return false;
    }

    this.killServerProcess();

    if (await this.isServerRunning()) {
      vscode.window.showInformationMessage("Server already running.");
      return true;
    }

    try {
      this.serverOutputChannel.appendLine("Starting Backend...");
      this.serverOutputChannel.appendLine(
        `Python Path: ${pythonInterpreterPath}`,
      );
      this.serverOutputChannel.appendLine(
        `Working Directory: ${workspaceFolder}`,
      );
      this.serverOutputChannel.appendLine("Starting RoboView Server...");
      this.serverOutputChannel.appendLine("─".repeat(50));

      this.serverProcess = spawn(
        pythonInterpreterPath,
        ["-m", "roboview.main"],
        {
          cwd: workspaceFolder,
          stdio: ["pipe", "pipe", "pipe"],
          shell: false,
        },
      );

      this.serverOutputChannel.show();

      this.serverProcess.stdout?.on("data", (data) => {
        const output = data.toString();
        this.serverOutputChannel.append(output);
      });

      this.serverProcess.stderr?.on("data", (data) => {
        const error = data.toString();
        this.serverOutputChannel.appendLine(error);
      });

      this.serverProcess.on("close", (code) => {
        const message = `Backend process exited with code ${code}`;
        this.serverOutputChannel.appendLine(message);
        vscode.window.showInformationMessage(message);
      });

      const started = await this.checkServerProcessAlive();

      if (!started) {
        this.killServerProcess();
        return false;
      }

      return true;
    } catch (error) {
      const message = `Error starting backend: ${error}. Please ensure that roboview is installed in the current Python environment.`;
      this.serverOutputChannel.appendLine(`[ERROR] ${message}`);
      vscode.window.showErrorMessage(message);
      return false;
    }
  }

  private checkServerProcessAlive(
    timeoutMs: number = 120000,
    intervalMs: number = 1000,
  ): Promise<boolean> {
    return new Promise((resolve) => {
      const startTime = Date.now();

      const onError = () => resolve(false);
      const onClose = () => resolve(false);

      this.serverProcess?.on("error", onError);
      this.serverProcess?.on("close", onClose);

      const interval = setInterval(async () => {
        if (Date.now() - startTime > timeoutMs) {
          clearInterval(interval);
          this.serverProcess?.removeListener("error", onError);
          this.serverProcess?.removeListener("close", onClose);
          resolve(false);
          return;
        }

        if (await this.isServerRunning()) {
          clearInterval(interval);
          this.serverProcess?.removeListener("error", onError);
          this.serverProcess?.removeListener("close", onClose);
          resolve(true);
        }
      }, intervalMs);
    });
  }

  public async initializeServer(
    currentPanel: vscode.WebviewPanel | undefined,
  ): Promise<void> {
    try {
      const vsProjectRootDir = PathManager.getWorkspaceRoot();
      const robocopConfigPath = new RobocopConfigFinder(
        vsProjectRootDir,
      ).getConfigPath();

      if (robocopConfigPath) {
        vscode.window.showInformationMessage(
          "Using Robocop Config File from .env: " + robocopConfigPath,
        );
      }

      if (!vsProjectRootDir) {
        vscode.window.showErrorMessage("Please Open a Workspace Folder.");
        return;
      }
      await axios.post(`${this.apiServerUrl}/api/v1/system/initialize`, {
        project_root_dir: vsProjectRootDir,
        robocop_config_file: robocopConfigPath,
      });
      vscode.window.showInformationMessage("RoboView is ready to use :)");
    } catch (error) {
      vscode.window.showErrorMessage("Process Failed: " + error);
    }
  }

  public getServerOutputChannel(): vscode.OutputChannel {
    return this.serverOutputChannel;
  }

  public killServerProcess(): void {
    if (this.serverProcess) {
      this.serverProcess.kill();
    }
  }

  public async isServerRunning(): Promise<boolean> {
    try {
      await axios.get(`${this.apiServerUrl}/api/v1/system/health`, {
        timeout: 1000,
      });
      return true;
    } catch (error) {
      return false;
    }
  }
}
