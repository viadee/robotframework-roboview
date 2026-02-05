import React, { useState } from "react";
import Header from "./components/layout/header";
import Footer from "./components/layout/footer";
import DashboardView from "./app/dashboard/page";
import KeywordUsageView from "./app/keyword-usage/page";
import RobocopMessageView from "./app/robocop/page";
import "./App.css";

function App() {
  const [currentView, setCurrentView] = useState<
    "dashboard" | "keyword-usage" | "robocop"
  >("dashboard");

  return (
    <div className="app">
      <Header currentView={currentView} onViewChange={setCurrentView} />
      {currentView === "dashboard" && <DashboardView />}
      {currentView === "keyword-usage" && <KeywordUsageView />}
      {currentView === "robocop" && <RobocopMessageView />}
      <Footer />
    </div>
  );
}

export default App;
