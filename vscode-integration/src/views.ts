import * as vscode from "vscode";

export class RoboViewControlProvider
  implements vscode.TreeDataProvider<ControlButton>, vscode.Disposable
{
  private _onDidChangeTreeData: vscode.EventEmitter<ControlButton | undefined> =
    new vscode.EventEmitter<ControlButton | undefined>();
  readonly onDidChangeTreeData: vscode.Event<ControlButton | undefined> =
    this._onDidChangeTreeData.event;

  private _isExtensionReady: boolean = false;

  dispose(): void {
    this._onDidChangeTreeData.dispose();
  }

  public setExtensionReady(ready: boolean): void {
    this._isExtensionReady = ready;
    this.refresh();
  }

  public refresh(): void {
    this._onDidChangeTreeData.fire(undefined);
  }

  getTreeItem(element: ControlButton): vscode.TreeItem {
    const treeItem = new vscode.TreeItem(element.label);
    treeItem.iconPath = new vscode.ThemeIcon(element.icon);
    treeItem.command = {
      command: element.command,
      title: element.label,
      arguments: [],
    };
    treeItem.tooltip = element.tooltip;
    return treeItem;
  }

  getChildren(element?: ControlButton): Thenable<ControlButton[]> {
    if (element) {
      return Promise.resolve([]);
    } else {
      const buttons: ControlButton[] = [];

      if (this._isExtensionReady) {
        buttons.push({
          label: "Open RoboView Monitor",
          icon: "play",
          command: "roboview.show-monitor",
          tooltip: "Opens the RoboView Monitor",
        });
      }

      buttons.push({
        label: "Restart Extension",
        icon: "refresh",
        command: "roboview.restart",
        tooltip: "Restarts the RoboView Extension",
      });

      return Promise.resolve(buttons);
    }
  }
}

interface ControlButton {
  label: string;
  icon: string;
  command: string;
  tooltip: string;
}
