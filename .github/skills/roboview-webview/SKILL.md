---
name: roboview-webview
description: React webview UI development for RoboView. Use when modifying the dashboard, keyword usage panel, robocop panel, or UI components. Covers React patterns, shadcn/ui components, VS Code theming, and webview communication.
applyTo: "vscode-integration/webview-ui/src/**/*.{tsx,ts}"
---

# RoboView Webview UI Development

## Architecture Overview

The webview UI is a React application embedded in VS Code, providing dashboard visualizations for Robot Framework analysis.

### Directory Structure

```
vscode-integration/webview-ui/src/
├── app/                    # Page components
│   ├── dashboard/          # Dashboard page with KPIs
│   ├── keyword-usage/      # Keyword usage analysis
│   ├── robocop/            # Robocop issues panel
│   └── reports/            # Report generation
├── components/
│   ├── ui/                 # shadcn/ui components
│   └── layout/             # Layout components (sidebar, nav)
├── hooks/                  # Custom React hooks
├── lib/                    # Utilities
└── types/                  # TypeScript types
```

## Development Patterns

### 1. Page Component Structure

Pages follow a consistent structure with VS Code messaging:

```tsx
import { useEffect, useState } from 'react';
import { useMessageListener } from '@/hooks/useMessageListener';
import { vscode } from '@/lib/vscode';
import type { KPIData } from '@/types/dashboard';

export function DashboardPage() {
    const [kpis, setKpis] = useState<KPIData | null>(null);
    const [loading, setLoading] = useState(true);
    
    // Request data on mount
    useEffect(() => {
        vscode.postMessage({ command: 'getKPIs' });
    }, []);
    
    // Handle responses from extension
    useMessageListener((message) => {
        if (message.command === 'kpisData') {
            setKpis(message.data as KPIData);
            setLoading(false);
        }
    });
    
    if (loading) {
        return <LoadingSkeleton />;
    }
    
    return (
        <div className="p-4 space-y-4">
            <MetricsGrid kpis={kpis} />
            <KeywordAnalysis />
        </div>
    );
}
```

### 2. VS Code Communication

Use the vscode API wrapper for type-safe messaging:

```tsx
// lib/vscode.ts
interface VsCodeApi {
    postMessage(message: WebviewMessage): void;
    getState(): unknown;
    setState(state: unknown): void;
}

declare function acquireVsCodeApi(): VsCodeApi;

export const vscode = acquireVsCodeApi();

// Usage
vscode.postMessage({ 
    command: 'openFile', 
    data: { path: filePath, line: lineNumber } 
});
```

### 3. Message Listener Hook

Type-safe message handling:

```tsx
// hooks/useMessageListener.ts
import { useEffect } from 'react';

interface ExtensionMessage {
    command: string;
    data?: unknown;
}

export function useMessageListener(
    handler: (message: ExtensionMessage) => void
): void {
    useEffect(() => {
        const listener = (event: MessageEvent<ExtensionMessage>) => {
            handler(event.data);
        };
        
        window.addEventListener('message', listener);
        return () => window.removeEventListener('message', listener);
    }, [handler]);
}
```

### 4. Component Development

Use shadcn/ui components with VS Code theming:

```tsx
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface MetricCardProps {
    title: string;
    value: number | string;
    trend?: 'up' | 'down' | 'neutral';
}

export function MetricCard({ title, value, trend }: MetricCardProps) {
    return (
        <Card>
            <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                    {title}
                </CardTitle>
            </CardHeader>
            <CardContent>
                <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold">{value}</span>
                    {trend && <TrendIndicator trend={trend} />}
                </div>
            </CardContent>
        </Card>
    );
}
```

### 5. Chart Components

Use Recharts for data visualization:

```tsx
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

interface KeywordBarChartProps {
    data: Array<{ name: string; count: number }>;
}

export function KeywordBarChart({ data }: KeywordBarChartProps) {
    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} layout="vertical">
                <XAxis type="number" />
                <YAxis 
                    dataKey="name" 
                    type="category" 
                    width={150}
                    tick={{ fontSize: 12 }}
                />
                <Tooltip />
                <Bar 
                    dataKey="count" 
                    fill="var(--chart-1)" 
                    radius={[0, 4, 4, 0]}
                />
            </BarChart>
        </ResponsiveContainer>
    );
}
```

### 6. Three-Panel Layout

For complex views like keyword usage:

```tsx
import { ResizablePanelGroup, ResizablePanel, ResizableHandle } from '@/components/ui/resizable';

export function KeywordUsagePage() {
    const [selectedFile, setSelectedFile] = useState<string | null>(null);
    const [selectedKeyword, setSelectedKeyword] = useState<KeywordUsage | null>(null);
    
    return (
        <ResizablePanelGroup direction="horizontal" className="h-full">
            {/* Sidebar - File Tree */}
            <ResizablePanel defaultSize={25} minSize={15}>
                <FileTreeSidebar onSelectFile={setSelectedFile} />
            </ResizablePanel>
            
            <ResizableHandle withHandle />
            
            {/* Main Content - Keyword List */}
            <ResizablePanel defaultSize={50} minSize={30}>
                <KeywordList 
                    file={selectedFile}
                    onSelectKeyword={setSelectedKeyword}
                />
            </ResizablePanel>
            
            <ResizableHandle withHandle />
            
            {/* Details Panel */}
            <ResizablePanel defaultSize={25} minSize={20}>
                <KeywordDetails keyword={selectedKeyword} />
            </ResizablePanel>
        </ResizablePanelGroup>
    );
}
```

### 7. Type Definitions

Maintain strict typing for all data structures:

```tsx
// types/keywords.ts
export interface KeywordUsage {
    keyword_id: string;
    file_name: string;
    keyword_name_with_prefix: string;
    keyword_name_without_prefix: string;
    documentation: string | null;
    source: string;
    file_usages: number;
    total_usages: number;
}

export interface SimilarKeyword {
    keyword_id: string;
    keyword_name_with_prefix: string;
    keyword_name_without_prefix: string;
    source: string;
    score: number;
}
```

## VS Code Theme Integration

Use CSS variables that map to VS Code colors:

```css
/* Automatically inherit VS Code theme */
:root {
    --background: var(--vscode-editor-background);
    --foreground: var(--vscode-editor-foreground);
    --muted: var(--vscode-input-background);
    --muted-foreground: var(--vscode-descriptionForeground);
    --border: var(--vscode-panel-border);
    --primary: var(--vscode-button-background);
    --primary-foreground: var(--vscode-button-foreground);
}
```

## Validation Requirements

Before committing webview changes:

1. **Type checking**: `npm run typecheck` in `webview-ui/`
2. **Build**: `npm run build` in `webview-ui/`
3. **Visual testing**: Test in both light and dark VS Code themes

## Key Dependencies

- **React 19** + **React Router DOM 7**: UI framework and routing
- **Tailwind CSS 4**: Styling
- **shadcn/ui**: Component library
- **Recharts**: Charts and visualizations
- **Lucide React** / **Tabler Icons**: Icon sets
- **Vite**: Build tool

## File Click Handling

Enable navigation to source files:

```tsx
function handleFileClick(source: string, lineNumber?: number) {
    vscode.postMessage({
        command: 'openFile',
        data: { 
            path: source, 
            line: lineNumber 
        },
    });
}
```
