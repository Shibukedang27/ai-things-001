import type { LucideIcon } from "lucide-react";
import { ArrowDownRight, ArrowUpRight, Minus } from "lucide-react";

import type { ScoreMetric } from "../app/types";

type MetricCardProps = {
  metric: ScoreMetric;
  icon: LucideIcon;
};

export function MetricCard({ metric, icon: Icon }: MetricCardProps) {
  const TrendIcon = metric.trend === "up" ? ArrowUpRight : metric.trend === "down" ? ArrowDownRight : Minus;

  return (
    <article className="metric-card">
      <div className="metric-icon">
        <Icon size={20} strokeWidth={2.2} />
      </div>
      <div>
        <p className="eyebrow">{metric.label}</p>
        <div className="metric-row">
          <strong>{metric.value}</strong>
          <span className={`trend trend-${metric.trend}`}>
            <TrendIcon size={16} />
          </span>
        </div>
        <span className="subtle">{metric.delta}</span>
      </div>
    </article>
  );
}
