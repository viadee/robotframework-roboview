import { Routes, Route, Navigate } from "react-router-dom";
import { Header } from "./components/layout/header";
import Footer from "./components/layout/footer";
import KeywordUsagePage from "./app/keyword-usage-panel/page";
import RobocopPage from "./app/robocop-panel/page";
import DashboardPage from "./app/dashboard/page";

export function App() {
  return (
    <div className="h-screen w-screen flex flex-col overflow-hidden">
      <Header />
      <main className="flex-1 overflow-hidden pb-10">
        <Routes>
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/keyword-usage" element={<KeywordUsagePage />} />
          <Route path="/robocop" element={<RobocopPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}