import { lazy, Suspense, useEffect, useState } from "react";
import {
  Activity,
  BarChart3,
  Brain,
  CalendarCheck2,
  Code2,
  FileSearch,
  Gauge,
  LayoutDashboard,
  LogOut,
  Moon,
  PanelLeft,
  Sun,
  Target,
  Trophy,
  UserCircle2,
} from "lucide-react";

import { Leaderboard } from "../components/Leaderboard";
import { LearningProgress } from "../components/LearningProgress";
import { LoadingScreen } from "../components/LoadingScreen";
import { MetricCard } from "../components/MetricCard";
import { PerformancePanel } from "../components/PerformancePanel";
import { RecentInterviews } from "../components/RecentInterviews";
import { TopicPanel } from "../components/TopicPanel";
import { useDarkMode } from "../hooks/useDarkMode";
import { AuthPage } from "../pages/AuthPage";
import { LandingPage } from "../pages/LandingPage";
import {
  authStorageKeys,
  clearAuth,
  logout as logoutFromApi,
  readStoredUser,
  type AuthResponse,
  type UserProfile,
} from "../services/authApi";
import { dashboardData } from "./dashboardData";

const metricIcons = [Gauge, Trophy, CalendarCheck2, Target];
const LiveCodingWorkspace = lazy(() =>
  import("../features/liveCoding/LiveCodingWorkspace").then((module) => ({ default: module.LiveCodingWorkspace })),
);
const ResumeAnalyzerWorkspace = lazy(() =>
  import("../features/resumeAnalyzer/ResumeAnalyzerWorkspace").then((module) => ({
    default: module.ResumeAnalyzerWorkspace,
  })),
);
const AnalyticsWorkspace = lazy(() =>
  import("../features/analytics/AnalyticsWorkspace").then((module) => ({ default: module.AnalyticsWorkspace })),
);

type AppView = "dashboard" | "analytics" | "live-coding" | "resume-analyzer" | "interviews" | "roadmap" | "reports";
type AppScreen = "auth" | "landing" | "dashboard";

const navItems: Array<{ label: string; icon: typeof LayoutDashboard; view: AppView }> = [
  { label: "Dashboard", icon: LayoutDashboard, view: "dashboard" },
  { label: "Analytics", icon: Activity, view: "analytics" },
  { label: "Live Coding", icon: Code2, view: "live-coding" },
  { label: "Resume Analyzer", icon: FileSearch, view: "resume-analyzer" },
  { label: "Interviews", icon: Brain, view: "interviews" },
  { label: "Roadmap", icon: Target, view: "roadmap" },
  { label: "Reports", icon: BarChart3, view: "reports" },
];

export function App() {
  const { theme, toggleTheme } = useDarkMode();
  const [isLoading, setIsLoading] = useState(true);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState<UserProfile | null>(() => readStoredUser());
  const [screen, setScreen] = useState<AppScreen>(() =>
    window.localStorage.getItem(authStorageKeys.accessToken) && readStoredUser() ? "dashboard" : "auth",
  );
  const [activeView, setActiveView] = useState<AppView>("dashboard");

  useEffect(() => {
    const timer = window.setTimeout(() => setIsLoading(false), 850);
    return () => window.clearTimeout(timer);
  }, []);

  if (isLoading) {
    return <LoadingScreen />;
  }

  const handleAuthenticated = (auth: AuthResponse) => {
    setCurrentUser(auth.user);
    setScreen("dashboard");
  };

  const handleLogout = () => {
    const refreshToken = window.localStorage.getItem(authStorageKeys.refreshToken);
    clearAuth();
    setCurrentUser(null);
    setActiveView("dashboard");
    setScreen("auth");
    void logoutFromApi(refreshToken);
  };

  if (screen === "landing") {
    return <LandingPage theme={theme} onToggleTheme={toggleTheme} onOpenApp={() => setScreen("auth")} />;
  }

  if (screen === "auth") {
    return (
      <AuthPage
        theme={theme}
        onToggleTheme={toggleTheme}
        onAuthenticated={handleAuthenticated}
        onViewLanding={() => setScreen("landing")}
      />
    );
  }

  const viewTitle =
    activeView === "live-coding"
      ? "Live Coding"
      : activeView === "resume-analyzer"
        ? "Resume Analyzer"
        : activeView === "analytics"
          ? "Analytics"
        : "Interview Readiness";
  const viewEyebrow =
    activeView === "live-coding"
      ? "Practice Studio"
      : activeView === "resume-analyzer"
        ? "Career Intelligence"
        : activeView === "analytics"
          ? "Performance Intelligence"
          : "Dashboard";

  return (
    <div className="dashboard-app">
      <aside className={`sidebar ${isSidebarOpen ? "open" : ""}`}>
        <div className="brand">
          <div className="brand-mark">
            OP
          </div>
          <div>
            <strong>OfferPilot AI</strong>
            <span>Interview Intelligence</span>
          </div>
        </div>
        <nav className="sidebar-nav" aria-label="Dashboard">
          {navItems.map((item) => {
            const NavIcon = item.icon;
            return (
              <button
                className={item.view === activeView ? "active" : ""}
                key={item.label}
                type="button"
                onClick={() => {
                  setActiveView(item.view);
                  setIsSidebarOpen(false);
                }}
              >
                <NavIcon size={18} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>
      <button
        aria-label="Close navigation"
        className={`sidebar-backdrop ${isSidebarOpen ? "open" : ""}`}
        onClick={() => setIsSidebarOpen(false)}
        type="button"
      />

      <main className="dashboard-main">
        <header className="topbar">
          <button
            aria-expanded={isSidebarOpen}
            aria-label="Open navigation"
            className="icon-button mobile-menu"
            onClick={() => setIsSidebarOpen(true)}
            title="Open navigation"
            type="button"
          >
            <PanelLeft size={20} />
          </button>
          <div>
            <p className="eyebrow">{viewEyebrow}</p>
            <h1>{viewTitle}</h1>
          </div>
          <div className="topbar-actions">
            <span className="sync-pill">Updated 2m ago</span>
            {currentUser && (
              <span className="user-chip" title={currentUser.email}>
                <UserCircle2 size={17} />
                {currentUser.full_name}
              </span>
            )}
            <button
              className="icon-button"
              type="button"
              aria-label="Toggle theme"
              title="Toggle theme"
              onClick={toggleTheme}
            >
              {theme === "dark" ? <Sun size={19} /> : <Moon size={19} />}
            </button>
            <button className="icon-button" type="button" aria-label="Logout" title="Logout" onClick={handleLogout}>
              <LogOut size={19} />
            </button>
          </div>
        </header>

        {activeView === "live-coding" ? (
          <Suspense fallback={<div className="panel workspace-loading">Loading editor...</div>}>
            <LiveCodingWorkspace theme={theme} />
          </Suspense>
        ) : activeView === "resume-analyzer" ? (
          <Suspense fallback={<div className="panel workspace-loading">Loading analyzer...</div>}>
            <ResumeAnalyzerWorkspace />
          </Suspense>
        ) : activeView === "analytics" ? (
          <Suspense fallback={<div className="panel workspace-loading">Loading analytics...</div>}>
            <AnalyticsWorkspace />
          </Suspense>
        ) : (
          <DashboardContent />
        )}
      </main>
    </div>
  );
}

function DashboardContent() {
  return (
    <>
      <section className="metrics-grid" aria-label="Score summary">
        {dashboardData.metrics.map((metric, index) => (
          <MetricCard metric={metric} icon={metricIcons[index]} key={metric.label} />
        ))}
      </section>

      <div className="dashboard-grid">
        <PerformancePanel data={dashboardData.performance} />
        <section className="streak-panel">
          <div className="streak-inner">
            <span className="streak-ring">14</span>
            <div>
              <h2>Daily Streak</h2>
              <p>Five sessions from monthly badge.</p>
            </div>
          </div>
          <div className="streak-days">
            {["M", "T", "W", "T", "F", "S", "S"].map((day, index) => (
              <span className={index < 6 ? "done" : ""} key={`${day}-${index}`}>
                {day}
              </span>
            ))}
          </div>
        </section>
      </div>

      <div className="split-grid">
        <TopicPanel title="Weak Topics" topics={dashboardData.weakTopics} tone="weak" />
        <TopicPanel title="Strong Topics" topics={dashboardData.strongTopics} tone="strong" />
      </div>

      <div className="lower-grid">
        <RecentInterviews interviews={dashboardData.recentInterviews} />
        <LearningProgress items={dashboardData.learningProgress} />
        <Leaderboard entries={dashboardData.leaderboard} />
      </div>
    </>
  );
}
