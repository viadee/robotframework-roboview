import { ReactNode, useState, useRef, useCallback, useEffect } from "react";

interface LayoutProps {
  sidebar: ReactNode;
  mainContent: ReactNode;
  detailsPanel: ReactNode;
}

export default function Layout({
  sidebar,
  mainContent,
  detailsPanel,
}: LayoutProps) {
  const [isDetailsPanelOpen, setIsDetailsPanelOpen] = useState(true);
  const [isResizing, setIsResizing] = useState(false);
  const [detailsWidthFr, setDetailsWidthFr] = useState(3);
  const [detailsWidthPx, setDetailsWidthPx] = useState(450);
  const containerRef = useRef<HTMLDivElement>(null);

  const gridLayout = {
    sidebar: 2,
    mainContent: 5,
    details: detailsWidthFr,
  };

  const startResizing = useCallback(() => {
    setIsResizing(true);
  }, []);

  const stopResizing = useCallback(() => {
    setIsResizing(false);
  }, []);

  const resize = useCallback(
    (e: MouseEvent) => {
      if (isResizing && containerRef.current) {
        const containerRect = containerRef.current.getBoundingClientRect();
        const containerWidth = containerRect.width;
        const rightEdgeDistance = containerRect.right - e.clientX;

        // Update pixel width for button positioning
        setDetailsWidthPx(rightEdgeDistance);

        const totalFr =
          gridLayout.sidebar + gridLayout.mainContent + gridLayout.details;
        const pixelPerFr = containerWidth / totalFr;
        const newDetailsFr = rightEdgeDistance / pixelPerFr;

        // Min: 2fr (~20%), Max: 6fr (~60%)
        if (newDetailsFr >= 2 && newDetailsFr <= 6) {
          setDetailsWidthFr(newDetailsFr);
        }
      }
    },
    [
      isResizing,
      gridLayout.sidebar,
      gridLayout.mainContent,
      gridLayout.details,
    ],
  );

  // Calculate details width on mount and window resize
  useEffect(() => {
    const updateDetailsWidth = () => {
      if (containerRef.current && isDetailsPanelOpen) {
        const containerRect = containerRef.current.getBoundingClientRect();
        const containerWidth = containerRect.width;
        const totalFr =
          gridLayout.sidebar + gridLayout.mainContent + detailsWidthFr;
        const pixelPerFr = containerWidth / totalFr;
        const calculatedWidth = detailsWidthFr * pixelPerFr;
        setDetailsWidthPx(calculatedWidth);
      }
    };

    updateDetailsWidth();
    window.addEventListener("resize", updateDetailsWidth);

    return () => {
      window.removeEventListener("resize", updateDetailsWidth);
    };
  }, [
    isDetailsPanelOpen,
    detailsWidthFr,
    gridLayout.sidebar,
    gridLayout.mainContent,
  ]);

  useEffect(() => {
    if (isResizing) {
      window.addEventListener("mousemove", resize as any);
      window.addEventListener("mouseup", stopResizing);
      document.body.style.cursor = "col-resize";
      document.body.style.userSelect = "none";
    } else {
      window.removeEventListener("mousemove", resize as any);
      window.removeEventListener("mouseup", stopResizing);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    }

    return () => {
      window.removeEventListener("mousemove", resize as any);
      window.removeEventListener("mouseup", stopResizing);
      document.body.style.cursor = "";
      document.body.style.userSelect = "";
    };
  }, [isResizing, resize, stopResizing]);

  const toggleDetailsPanel = () => {
    setIsDetailsPanelOpen(!isDetailsPanelOpen);
  };

  // Grid-Spalten mit fr-Einheiten und smooth transition
  const gridTemplateColumns = isDetailsPanelOpen
    ? `${gridLayout.sidebar}fr ${gridLayout.mainContent}fr ${detailsWidthFr}fr`
    : `${gridLayout.sidebar}fr ${gridLayout.mainContent + detailsWidthFr}fr 0fr`;

  return (
    <div
      className={`layout-container ${isResizing ? "resizing" : ""}`}
      ref={containerRef}
      style={{
        gridTemplateColumns,
        gridTemplateRows: "1fr",
        // CSS Variable für Toggle-Button Position
        ["--details-width" as any]: `${detailsWidthPx}px`,
      }}
    >
      <div className="sidebar-section">{sidebar}</div>

      <div className="main-content-section">{mainContent}</div>

      {/* Details Panel wird immer gerendert */}
      <div
        className={`details-panel-section ${isDetailsPanelOpen ? "open" : "closed"}`}
      >
        {isDetailsPanelOpen && (
          <>
            {/* Resize handle nur wenn offen */}
            <div
              className="resize-handle"
              onMouseDown={startResizing}
              title="Drag to resize details panel"
            />
            {detailsPanel}
          </>
        )}
      </div>

      {/* Toggle button - IMMER SICHTBAR mit fixed positioning */}
      <button
        className={`details-toggle-btn ${isDetailsPanelOpen ? "open" : "closed"}`}
        onClick={toggleDetailsPanel}
        title={
          isDetailsPanelOpen ? "Close Details Panel" : "Open Details Panel"
        }
        aria-label={
          isDetailsPanelOpen ? "Close Details Panel" : "Open Details Panel"
        }
      >
        {isDetailsPanelOpen ? "›" : "‹"}
      </button>
    </div>
  );
}
