import * as fs from "fs";
import * as path from "path";
import * as dotenv from "dotenv";

export class RobocopConfigFinder {
  private readonly workspaceRoot: string;
  private readonly configFileNames: string[] = [
    ".robocop",
    "robocop.toml",
    "robot.toml",
    "pyproject.toml",
  ];

  constructor(workspaceRootDir: string) {
    this.workspaceRoot = workspaceRootDir;
  }

  public findConfigFile(): string | undefined {
    const envConfigPath = this.getConfigFromEnv();
    if (envConfigPath && this.fileExists(envConfigPath)) {
      return envConfigPath;
    }
    return;

  }

  private getConfigFromEnv(): string | undefined {
    if (!this.workspaceRoot) {
      return undefined;
    }

    const envPath = path.join(this.workspaceRoot, ".env");

    if (!this.fileExists(envPath)) {
      return undefined;
    }

    const result = dotenv.config({ path: envPath });

    if (result.error) {
      return undefined;
    }

    const configPath = process.env.ROBOCOP_CONFIG_PATH;

    if (!configPath) {
      return undefined;
    }

    return path.isAbsolute(configPath)
      ? configPath
      : path.resolve(this.workspaceRoot, configPath);
  }

  private fileExists(filePath: string): boolean {
    try {
      return fs.existsSync(filePath) && fs.statSync(filePath).isFile();
    } catch {
      return false;
    }
  }

  public getConfigPath(): string | undefined {
    return this.findConfigFile();
  }
}
