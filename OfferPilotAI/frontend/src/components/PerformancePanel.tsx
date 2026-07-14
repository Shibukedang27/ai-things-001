import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { PerformancePoint } from "../app/types";

type PerformancePanelProps = {
  data: PerformancePoint[];
};

export function PerformancePanel({ data }: PerformancePanelProps) {
  return (
    <section className="panel performance-panel">
      <div className="panel-heading">
        <div>
          <h2>Performance Charts</h2>
          <span>Score, accuracy, communication</span>
        </div>
        <span className="pill">7 days</span>
      </div>
      <div className="chart-grid">
        <div className="chart-frame">
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={data} margin={{ top: 12, right: 16, left: -18, bottom: 0 }}>
              <defs>
                <linearGradient id="scoreFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--accent)" stopOpacity={0.45} />
                  <stop offset="95%" stopColor="var(--accent)" stopOpacity={0.02} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
              <XAxis dataKey="label" tickLine={false} axisLine={false} stroke="var(--muted)" />
              <YAxis tickLine={false} axisLine={false} stroke="var(--muted)" domain={[50, 100]} />
              <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)" }} />
              <Area type="monotone" dataKey="score" stroke="var(--accent)" strokeWidth={3} fill="url(#scoreFill)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
        <div className="chart-frame compact-chart">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={data} margin={{ top: 12, right: 12, left: -18, bottom: 0 }}>
              <CartesianGrid stroke="var(--chart-grid)" vertical={false} />
              <XAxis dataKey="label" tickLine={false} axisLine={false} stroke="var(--muted)" />
              <YAxis tickLine={false} axisLine={false} stroke="var(--muted)" domain={[50, 100]} />
              <Tooltip contentStyle={{ background: "var(--surface)", border: "1px solid var(--border)" }} />
              <Bar dataKey="accuracy" fill="var(--accent-2)" radius={[6, 6, 0, 0]} />
              <Bar dataKey="communication" fill="var(--accent-3)" radius={[6, 6, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </section>
  );
}
