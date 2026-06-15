---
name: roboview-extension
description: VS Code extension development for RoboView. Use when modifying extension activation, commands, services, or webview communication. Covers TypeScript patterns, VS Code API usage, and backend coordination.
applyTo: "vscode-integration/src/**/*.ts"
---

# RoboView VS Code Extension Development

## Architecture Overview

The RoboView extension connects the VS Code UI with the Python backend, providing a webview-based dashboard for Robot Framework analysis.

### Directory Structure

```
vscode-integration/src/
├── extension.ts           # Entry point, activation
├── commands.ts            # Command handlers
├── roboViewPanel.ts       # Webview panel management
├── views.ts               # TreeDataProviders
├── services/              # Backend communication
│   ├── backendConnectionManager.ts
│   ├── lifecycleManager.ts
│   ├── pathManager.ts
│   ├── pythonEnvironmentManager.ts
│   └── robocopConfigFinder.ts
└── utils/                 # Shared utilities
```

## Development Patterns

### 1. Extension Activation

The extension follows VS Code's activation pattern:

```typescript
export async function activate(context: vscode.ExtensionContext): Promise<void> {
    // Initialize services
    const pathManager = new PathManager(context);
    const backendManager = new BackendConnectionManager(pathManager);
    
    // Register commands
    const commandHandler = new CommandHandler(backendManager);
    commandHandler.registerCommands(context);
    
    // Execute startup
    await vscode.commands.executeCommand('roboview.start');
}

export function deactivate(): void {
    // Cleanup resources
}
```

### 2. Command Registration

Commands follow a centralized registration pattern:

```typescript
class CommandHandler {
    private readonly disposables: vscode.Disposable[] = [];
    
    constructor(private readonly backendManager: BackendConnectionManager) {}
    
    registerCommands(context: vscode.ExtensionContext): void {
        this.disposables.push(
            vscode.commands.registerCommand('roboview.command-name', 
                () => this.executeCommand())
        );
        context.subscriptions.push(...this.disposables);
    }
    
    private async executeCommand(): Promise<void> {
        // Command implementation
    }
}
```

### 3. Service Development

Services encapsulate specific functionality:

```typescript
export class NewService {
    private readonly _onStatusChanged = new vscode.EventEmitter<Status>();
    public readonly onStatusChanged = this._onStatusChanged.event;
    
    constructor(
        private readonly pathManager: PathManager,
        private readonly outputChannel: vscode.OutputChannel
    ) {}
    
    async initialize(): Promise<void> {
        // Initialization logic
        this._onStatusChanged.fire('ready');
    }
    
    dispose(): void {
        this._onStatusChanged.dispose();
    }
}
```

### 4. Backend Communication

Use Axios for HTTP communication with the Python backend:

```typescript
import axios, { AxiosInstance } from 'axios';

export class BackendConnectionManager {
    private readonly client: AxiosInstance;
    
    constructor(pathManager: PathManager) {
        this.client = axios.create({
            baseURL: 'http://127.0.0.1:18123',
            timeout: 30000,
        });
    }
    
    async healthCheck(): Promise<boolean> {
        try {
            const response = await this.client.get('/system/health');
            return response.status === 200;
        } catch {
            return false;
        }
    }
    
    async initialize(projectPath: string): Promise<void> {
        await this.client.post('/system/initialize', {
            project_path: projectPath,
        });
    }
}
```

### 5. Webview Panel Development

Webview panels handle bidirectional communication:

```typescript
export class RoboViewPanel {
    public static currentPanel: RoboViewPanel | undefined;
    private readonly _panel: vscode.WebviewPanel;
    private readonly _disposables: vscode.Disposable[] = [];
    
    private constructor(
        panel: vscode.WebviewPanel,
        private readonly backendManager: BackendConnectionManager
    ) {
        this._panel = panel;
        this._panel.webview.onDidReceiveMessage(
            this.handleMessage.bind(this),
            null,
            this._disposables
        );
    }
    
    private async handleMessage(message: WebviewMessage): Promise<void> {
        switch (message.command) {
            case 'getKPIs':
                const kpis = await this.backendManager.getKPIs();
                this._panel.webview.postMessage({ command: 'kpisData', data: kpis });
                break;
            case 'openFile':
                await this.openFileInEditor(message.data.path, message.data.line);
                break;
        }
    }
    
    private async openFileInEditor(path: string, line?: number): Promise<void> {
        const uri = vscode.Uri.file(path);
        const document = await vscode.workspace.openTextDocument(uri);
        const editor = await vscode.window.showTextDocument(document);
        if (line) {
            const position = new vscode.Position(line - 1, 0);
            editor.selection = new vscode.Selection(position, position);
            editor.revealRange(new vscode.Range(position, position));
        }
    }
}
```

### 6. TreeDataProvider Development

For sidebar views:

```typescript
export class RoboViewControlProvider implements vscode.TreeDataProvider<ControlItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<ControlItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    
    getTreeItem(element: ControlItem): vscode.TreeItem {
        return element;
    }
    
    getChildren(element?: ControlItem): Thenable<ControlItem[]> {
        if (!element) {
            return Promise.resolve(this.getRootItems());
        }
        return Promise.resolve([]);
    }
    
    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }
}
```

## Message Protocol

Define typed messages for webview communication:

```typescript
// From webview to extension
interface WebviewMessage {
    command: 'getKPIs' | 'getMostUsedKeywords' | 'openFile' | 'getKeywordsForFile';
    data?: Record<string, unknown>;
}

// From extension to webview
interface ExtensionMessage {
    command: 'kpisData' | 'mostUsedKeywordsData' | 'keywordsData' | 'error';
    data?: unknown;
}
```

## Validation Requirements

Before committing extension changes:

1. **Type checking**: `npm run check-types` in `vscode-integration/`
2. **Linting**: `npm run lint` in `vscode-integration/`
3. **Build**: `npm run compile`

## Key Dependencies

- **VS Code API**: `@types/vscode`
- **Axios**: HTTP client for backend communication
- **esbuild**: Build bundler

## Error Handling

Always provide user-friendly error messages:

```typescript
try {
    await this.backendManager.initialize(projectPath);
} catch (error) {
    const message = error instanceof Error ? error.message : 'Unknown error';
    vscode.window.showErrorMessage(`Failed to initialize: ${message}`);
    this.outputChannel.appendLine(`Error: ${message}`);
}
```
