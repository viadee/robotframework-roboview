import React from "react";

interface HeaderProps {
  currentView: "dashboard" | "keyword-usage" | "robocop";
  onViewChange: (view: "dashboard" | "keyword-usage" | "robocop") => void;
}

function Header({ currentView, onViewChange }: HeaderProps) {
  return (
    <div className="header">
      <div className="header-left">
        <div className="logo">🤖</div>
        <h1>RoboView - Keyword Management in Robot Framework</h1>
      </div>
      <div className="header-nav">
        <button
          className={`nav-button ${currentView === "dashboard" ? "active" : ""}`}
          onClick={() => onViewChange("dashboard")}
        >
          📊 Dashboard
        </button>
        <button
          className={`nav-button ${currentView === "keyword-usage" ? "active" : ""}`}
          onClick={() => onViewChange("keyword-usage")}
        >
          🔤 Keyword Usage
        </button>
        <button
          className={`nav-button ${currentView === "robocop" ? "active" : ""}`}
          onClick={() => onViewChange("robocop")}
        >
          🔍 Robocop
        </button>
      </div>
    </div>
  );
}

export default Header;
