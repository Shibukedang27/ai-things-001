import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  PolarAngleAxis,
  PolarGrid,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, Flame, Loader2, Radar as RadarIcon, RefreshCw, Target } from "lucide-react";
import { useMemo, useState } from "react";

import { fetchAnalyticsOverview } from "../../services/analyticsApi";
import { sampleAnalytics } from "./analyticsData";
import type { AnalyticsOverview } from "./types";

const toNumber = (value: string | number | null | undefined) => Number(value ?? 0);

export function AnalyticsWorkspace() {
  const [analytics, setAnalytics] = useState<AnalyticsOverview>(sampleAnalytics);
  const [isLoading, setIsLoading] = useState(false);
  const [notice, setNotice] = useState("Showing latest local analytics snapshot.");

  const weeklyData = useMemo(
    () =>
      analytics.weekly_progress.map((point) => ({
        ...point,
        average_score: toNumber(point.average_score),
        accuracy: toNumber(point.accuracy),
      })),
    [analytics.weekly_progress],
  );
  const monthlyData = useMemo(
    () =>
      analytics.monthly_progress.map((point) => ({
        ...point,
        average_score: toNumber(point.average_score),
        accuracy: toNumber(point.accuracy),
      })),
    [analytics.monthly_progress],
  );
  const radarData = useMemo(
    () =>
      analytics.radar_chart.map((point) => ({
        ...point,
        score: toNumber(point.score),
        benchmark: toNumber(point.benchmark),
      })),
    [analytics.radar_chart],
  );
  const performanceData = useMemo(
    () =>
      analytics.performance_graphs.map((point) => ({
        ...point,
        overall_score: toNumber(point.overall_score),
        technical_accuracy: toNumber(point.technical_accuracy),
        communication: toNumber(point.communication),
        problem_solving: toNumber(point.problem_solving),
        explanation_quality: toNumber(point.explanation_quality),
      })),
    [analytics.performance_graphs],
  );

  const refreshAnalytics = async () => {
    setIsLoading(true);
    try {
      setAnalytics(await fetchAnalyticsOverview());
      setNotice("Analytics refreshed from the backend.");
    } catch (error) {
      setNotice(error instanceof Error ? error.message : "Could not refresh analytics.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="analytics-workspace" aria-label="Analytics">
      <div className="module-heading">
        <div>
          <p className="eyebrow">Analytics</p>
          <h2>Topic accuracy, progress, trends, and history</h2>
        </div>
        <button className="secondary-action" disabled={isLoading} onClick={refreshAnalytics} type="button">
          {isLoading ? <Loader2 className="spin" size={17} /> : <RefreshCw size={17} />}
          Refresh
        </button>
      </div>

      <div className="analytics-summary">
        <article className="metric-card">
          <div className="metric-icon">
            <Activity size={20} />
          </div>
          <div>
            <p className="eyebrow">Average Score</p>
            <div className="metric-row">
              <strong>{analytics.summary.average_score}</strong>
            </div>
            <span className="subtle">{notice}</span>
          </div>
        </article>
        <article className="metric-card">
          <div className="metric-icon">
            <Target size={20} />
          </div>
          <div>
            <p className="eyebrow">Strongest Topic</p>
            <div className="metric-row">
              <strong>{analytics.summary.strongest_topic ?? "None"}</strong>
            </div>
            <span className="subtle">Highest score {analytics.summary.highest_score}</span>
          </div>
        </article>
        <article className="metric-card">
          <div className="metric-icon">
            <Flame size={20} />
          </div>
          <div>
            <p className="eyebrow">Weakest Topic</p>
            <div className="metric-row">
              <strong>{analytics.summary.weakest_topic ?? "None"}</strong>
            </div>
            <span className="subtle">{analytics.summary.interview_count} interviews tracked</span>
          </div>
        </article>
      </div>

      <div className="analytics-grid">
        <section className="panel analytics-wide">
          <div className="panel-heading">
            <div>
              <h2>Performance Graphs</h2>
              <span>Overall, accuracy, communication, problem solving</span>
            </div>
          </div>
          <div className="chart-frame">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={performanceData} margin={{ top: 12, right: 16, left: -18, bottom: 0 }}>
                <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
                <XAxis dataKey="label" tickLine={false} axisLine={false} stroke="var(--muted)" />
                <YAxis domain={[50, 100]} tickLine={false} axisLine={false} stroke="var(--muted)" />
                <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)" }} />
                <Legend />
                <Line type="monotone" dataKey="overall_score" stroke="var(--accent)" strokeWidth={3} dot={false} />
                <Line type="monotone" dataKey="technical_accuracy" stroke="var(--accent-2)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="communication" stroke="var(--accent-3)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="problem_solving" stroke="var(--success)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <div>
              <h2>Radar Chart</h2>
              <span>Skill dimensions</span>
            </div>
            <RadarIcon size={20} />
          </div>
          <div className="chart-frame">
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="var(--chart-grid)" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: "var(--muted)", fontSize: 12 }} />
                <Radar dataKey="benchmark" stroke="var(--border)" fill="var(--border)" fillOpacity={0.18} />
                <Radar dataKey="score" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.28} />
                <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)" }} />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      <div className="analytics-grid">
        <section className="panel">
          <div className="panel-heading">
            <h2>Topic Wise Accuracy</h2>
            <span className="pill">Accuracy</span>
          </div>
          <div className="topic-accuracy-list">
            {analytics.topic_wise_accuracy.map((topic) => (
              <div className="topic-accuracy-row" key={topic.topic}>
                <div>
                  <strong>{topic.topic}</strong>
                  <span>
                    {topic.attempts} attempts · trend {topic.trend}
                  </span>
                </div>
                <div className="topic-meter">
                  <div style={{ width: `${topic.accuracy}%` }} />
                </div>
                <b>{topic.accuracy}</b>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Weekly Progress</h2>
            <span className="pill">Weeks</span>
          </div>
          <div className="chart-frame">
            <ResponsiveContainer width="100%" height={250}>
              <AreaChart data={weeklyData} margin={{ top: 12, right: 12, left: -18, bottom: 0 }}>
                <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
                <XAxis dataKey="label" tickLine={false} axisLine={false} stroke="var(--muted)" />
                <YAxis domain={[50, 100]} tickLine={false} axisLine={false} stroke="var(--muted)" />
                <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)" }} />
                <Area type="monotone" dataKey="average_score" stroke="var(--accent)" fill="var(--accent)" fillOpacity={0.18} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Monthly Progress</h2>
            <span className="pill">Months</span>
          </div>
          <div className="chart-frame">
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={monthlyData} margin={{ top: 12, right: 12, left: -18, bottom: 0 }}>
                <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
                <XAxis dataKey="label" tickLine={false} axisLine={false} stroke="var(--muted)" />
                <YAxis domain={[50, 100]} tickLine={false} axisLine={false} stroke="var(--muted)" />
                <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)" }} />
                <Bar dataKey="average_score" fill="var(--accent-2)" radius={[6, 6, 0, 0]} />
                <Bar dataKey="accuracy" fill="var(--accent-3)" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </section>
      </div>

      <div className="analytics-grid">
        <section className="panel">
          <div className="panel-heading">
            <h2>Heat Map</h2>
            <span className="pill">Practice</span>
          </div>
          <div className="heatmap-grid">
            {analytics.heat_map.map((cell) => (
              <div
                className="heatmap-cell"
                key={`${cell.day}-${cell.hour}`}
                style={{ opacity: 0.24 + Number(cell.intensity) * 0.76 }}
                title={`${cell.day} ${cell.hour}:00 · ${cell.value}`}
              >
                <span>{cell.value}</span>
              </div>
            ))}
          </div>
          <div className="heatmap-axis">
            <span>9</span>
            <span>12</span>
            <span>15</span>
            <span>18</span>
            <span>21</span>
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Weakness Trends</h2>
            <span className="pill pill-weak">Focus</span>
          </div>
          <div className="trend-list">
            {analytics.weakness_trends.map((trend) => (
              <div className="trend-row" key={trend.topic}>
                <span>{trend.topic}</span>
                <strong>{trend.score}</strong>
              </div>
            ))}
          </div>
        </section>

        <section className="panel">
          <div className="panel-heading">
            <h2>Strength Trends</h2>
            <span className="pill pill-strong">Lead</span>
          </div>
          <div className="trend-list">
            {analytics.strength_trends.map((trend) => (
              <div className="trend-row" key={trend.topic}>
                <span>{trend.topic}</span>
                <strong>{trend.score}</strong>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="panel">
        <div className="panel-heading">
          <h2>Interview History</h2>
          <span className="pill">Recent</span>
        </div>
        <div className="analytics-history-list">
          {analytics.interview_history.map((interview) => (
            <div className="analytics-history-row" key={interview.id}>
              <div>
                <strong>{interview.title}</strong>
                <span>
                  {interview.role_title} · {interview.status} · {interview.duration_minutes} min
                </span>
              </div>
              <b>{interview.score ?? "Pending"}</b>
            </div>
          ))}
        </div>
      </section>
    </section>
  );
}
