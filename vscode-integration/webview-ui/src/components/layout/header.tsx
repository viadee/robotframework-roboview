import { useLocation, useNavigate } from "react-router-dom";
import { LayoutDashboard, KeyRound, ShieldAlert, Bot } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const navItems = [
  {
    path: "/dashboard",
    label: "Dashboard",
    icon: LayoutDashboard,
    color: "text-blue-400",
  },
  {
    path: "/keyword-usage",
    label: "Keyword Usage",
    icon: KeyRound,
    color: "text-amber-400",
  },
  {
    path: "/robocop",
    label: "Robocop",
    icon: ShieldAlert,
    color: "text-red-400",
  },
];

export function Header() {
  const { pathname } = useLocation();
  const navigate = useNavigate();

  return (
    <header className="h-16 shrink-0 border-b border-border bg-background flex items-center justify-between px-4">
      <div className="flex items-center gap-2.5">
        <div className="w-7 h-7 rounded-md bg-primary flex items-center justify-center shrink-0">
          <Bot className="w-4 h-4 text-primary-foreground" />
        </div>
        <span className="text-sm font-semibold text-foreground">RoboView</span>
        <span className="text-border">|</span>
        <span className="text-sm text-foreground hidden sm:block">
          Keyword Management in Robot Framework
        </span>
      </div>

      <nav className="flex items-center gap-1">
        {navItems.map(({ path, label, icon: Icon, color }) => {
          const isActive = pathname === path;
          return (
            <Button
              key={path}
              variant="ghost"
              size="sm"
              onClick={() => navigate(path)}
              className={cn(
                "gap-2 text-xs font-medium h-8 px-3",
                isActive
                  ? "bg-primary text-primary-foreground hover:bg-primary hover:text-primary-foreground"
                  : "text-foreground hover:text-foreground hover:bg-accent",
              )}
            >
              <Icon
                className={cn(
                  "w-3.5 h-3.5",
                  isActive ? "text-primary-foreground" : color,
                )}
              />
              {label}
            </Button>
          );
        })}
      </nav>
    </header>
  );
}
