export type ScoreMetric = {
  label: string;
  value: string;
  delta: string;
  trend: "up" | "down" | "flat";
};

export type TopicScore = {
  topic: string;
  score: number;
  category: string;
};

export type InterviewRecord = {
  id: string;
  role: string;
  type: string;
  score: number;
  date: string;
  status: "Completed" | "Needs Review" | "In Progress";
};

export type PerformancePoint = {
  label: string;
  score: number;
  accuracy: number;
  communication: number;
};

export type LearningItem = {
  title: string;
  progress: number;
  detail: string;
};

export type LeaderboardEntry = {
  rank: number;
  name: string;
  score: number;
  streak: number;
  currentUser?: boolean;
};

export type DashboardData = {
  metrics: ScoreMetric[];
  weakTopics: TopicScore[];
  strongTopics: TopicScore[];
  recentInterviews: InterviewRecord[];
  performance: PerformancePoint[];
  learningProgress: LearningItem[];
  leaderboard: LeaderboardEntry[];
};
