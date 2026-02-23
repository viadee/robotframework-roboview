import {
  ReactNode,
  createContext,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";
import type { PanelImperativeHandle } from "react-resizable-panels";
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from "../ui/resizable";

interface UsageLayoutContextValue {
  isDetailsCollapsed: boolean;
  toggleDetails: () => void;
}

const UsageLayoutContext = createContext<UsageLayoutContextValue | null>(null);

export function useUsageLayoutControls() {
  return useContext(UsageLayoutContext);
}

interface AppLayoutProps {
  sidebar: ReactNode;
  content: ReactNode;
  details: ReactNode;
  sidebarSize?: number;
  contentSize?: number;
  detailsSize?: number;
}

export function AppLayout({
  sidebar,
  content,
  details,
  sidebarSize = 20,
  contentSize = 55,
  detailsSize = 25,
}: AppLayoutProps) {
  const detailsPanelRef = useRef<PanelImperativeHandle | null>(null);
  const [isDetailsCollapsed, setIsDetailsCollapsed] = useState(false);

  const handleToggleDetails = () => {
    if (!detailsPanelRef.current) {
      return;
    }

    if (isDetailsCollapsed) {
      detailsPanelRef.current.expand();
      setIsDetailsCollapsed(false);
      return;
    }

    detailsPanelRef.current.collapse();
    setIsDetailsCollapsed(true);
  };

  const contextValue = useMemo(
    () => ({
      isDetailsCollapsed,
      toggleDetails: handleToggleDetails,
    }),
    [isDetailsCollapsed],
  );

  return (
    <UsageLayoutContext.Provider value={contextValue}>
      <ResizablePanelGroup orientation="horizontal" className="h-full">
        <ResizablePanel defaultSize={sidebarSize} minSize={15}>
          <div className="h-full overflow-auto">{sidebar}</div>
        </ResizablePanel>

        <ResizableHandle withHandle />

        <ResizablePanel defaultSize={contentSize} minSize={30}>
          <div className="h-full overflow-auto">{content}</div>
        </ResizablePanel>

        <ResizableHandle withHandle />

        <ResizablePanel
          panelRef={detailsPanelRef}
          defaultSize={detailsSize}
          minSize={15}
          collapsible
          collapsedSize={0}
          onResize={(panelSize) => {
            setIsDetailsCollapsed(panelSize.asPercentage <= 0);
          }}
        >
          <div className="h-full overflow-auto">{details}</div>
        </ResizablePanel>
      </ResizablePanelGroup>
    </UsageLayoutContext.Provider>
  );
}
