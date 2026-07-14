export type TopicAccuracyPoint = {
  topic: string;
  accuracy: string;
  attempts: number;
  average_score: string;
  trend: string;
};

export type ProgressPoint = {
  label: string;
  average_score: string;
  interview_count: number;
  accuracy: string;
};

export type HeatMapCell = {
  day: string;
  hour: number;
  value: number;
  intensity: string;
};

export type RadarMetric = {
  metric: string;
  score: string;
  benchmark: string;
};

export type TrendPoint = {
  label: string;
  score: string;
  topic: string;
};

export type InterviewHistoryAnalyticsItem = {
  id: string;
  title: string;
  role_title: string;
  status: string;
  score: string | null;
  duration_minutes: number;
  completed_at: string | null;
};

export type PerformanceGraphPoint = {
  label: string;
  overall_score: string;
  technical_accuracy: string;
  communication: string;
  problem_solving: string;
  explanation_quality: string;
};

export type AnalyticsOverview = {
  summary: {
    average_score: string;
    highest_score: string;
    interview_count: number;
    strongest_topic: string | null;
    weakest_topic: string | null;
  };
  topic_wise_accuracy: TopicAccuracyPoint[];
  weekly_progress: ProgressPoint[];
  monthly_progress: ProgressPoint[];
  heat_map: HeatMapCell[];
  radar_chart: RadarMetric[];
  weakness_trends: TrendPoint[];
  strength_trends: TrendPoint[];
  interview_history: InterviewHistoryAnalyticsItem[];
  performance_graphs: PerformanceGraphPoint[];
  generated_at: string;
};

export type ApiEnvelope<T> = {
  data: T | null;
  errors: Array<{ code: string; message: string; field?: string }>;
};
