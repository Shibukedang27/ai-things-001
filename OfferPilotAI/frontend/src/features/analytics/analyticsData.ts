import type { AnalyticsOverview } from "./types";

export const sampleAnalytics: AnalyticsOverview = {
  summary: {
    average_score: "84.20",
    highest_score: "96.00",
    interview_count: 38,
    strongest_topic: "System Design",
    weakest_topic: "Dynamic Programming",
  },
  topic_wise_accuracy: [
    { topic: "System Design", accuracy: "94.00", attempts: 8, average_score: "92.50", trend: "5.20" },
    { topic: "Python", accuracy: "89.00", attempts: 9, average_score: "88.20", trend: "3.40" },
    { topic: "SQL", accuracy: "76.00", attempts: 7, average_score: "78.10", trend: "1.80" },
    { topic: "Machine Learning", accuracy: "72.00", attempts: 5, average_score: "74.80", trend: "-2.10" },
    { topic: "Dynamic Programming", accuracy: "61.00", attempts: 6, average_score: "64.20", trend: "-4.70" },
  ],
  weekly_progress: [
    { label: "W23", average_score: "72.00", interview_count: 3, accuracy: "68.00" },
    { label: "W24", average_score: "76.00", interview_count: 4, accuracy: "72.00" },
    { label: "W25", average_score: "81.00", interview_count: 5, accuracy: "78.00" },
    { label: "W26", average_score: "84.00", interview_count: 4, accuracy: "82.00" },
    { label: "W27", average_score: "88.00", interview_count: 6, accuracy: "86.00" },
  ],
  monthly_progress: [
    { label: "Mar", average_score: "70.00", interview_count: 8, accuracy: "66.00" },
    { label: "Apr", average_score: "76.00", interview_count: 9, accuracy: "73.00" },
    { label: "May", average_score: "82.00", interview_count: 10, accuracy: "79.00" },
    { label: "Jun", average_score: "87.00", interview_count: 11, accuracy: "85.00" },
  ],
  heat_map: [
    ...["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"].flatMap((day, dayIndex) =>
      [9, 12, 15, 18, 21].map((hour, hourIndex) => {
        const value = (dayIndex + hourIndex) % 5;
        return { day, hour, value, intensity: (value / 4).toFixed(2) };
      }),
    ),
  ],
  radar_chart: [
    { metric: "Technical", score: "86.00", benchmark: "80.00" },
    { metric: "Communication", score: "82.00", benchmark: "80.00" },
    { metric: "Problem Solving", score: "79.00", benchmark: "80.00" },
    { metric: "Explanation", score: "84.00", benchmark: "80.00" },
    { metric: "Overall", score: "84.20", benchmark: "80.00" },
  ],
  weakness_trends: [
    { label: "DP", score: "39.00", topic: "Dynamic Programming" },
    { label: "ML", score: "28.00", topic: "Machine Learning" },
    { label: "SQL", score: "24.00", topic: "SQL" },
    { label: "Python", score: "11.00", topic: "Python" },
  ],
  strength_trends: [
    { label: "System", score: "94.00", topic: "System Design" },
    { label: "Python", score: "89.00", topic: "Python" },
    { label: "Comms", score: "84.00", topic: "Communication" },
    { label: "SQL", score: "76.00", topic: "SQL" },
  ],
  interview_history: [
    {
      id: "INT-1048",
      title: "Senior Backend Mock",
      role_title: "Senior Backend Engineer",
      status: "completed",
      score: "96.00",
      duration_minutes: 60,
      completed_at: "Today",
    },
    {
      id: "INT-1047",
      title: "ML Systems Mock",
      role_title: "ML Engineer",
      status: "completed",
      score: "78.00",
      duration_minutes: 45,
      completed_at: "Yesterday",
    },
    {
      id: "INT-1046",
      title: "SQL Optimization",
      role_title: "Data Engineer",
      status: "completed",
      score: "81.00",
      duration_minutes: 40,
      completed_at: "Jul 12",
    },
  ],
  performance_graphs: [
    { label: "Mon", overall_score: "71.00", technical_accuracy: "66.00", communication: "78.00", problem_solving: "68.00", explanation_quality: "74.00" },
    { label: "Tue", overall_score: "74.00", technical_accuracy: "70.00", communication: "77.00", problem_solving: "72.00", explanation_quality: "76.00" },
    { label: "Wed", overall_score: "80.00", technical_accuracy: "76.00", communication: "83.00", problem_solving: "79.00", explanation_quality: "82.00" },
    { label: "Thu", overall_score: "77.00", technical_accuracy: "73.00", communication: "79.00", problem_solving: "75.00", explanation_quality: "78.00" },
    { label: "Fri", overall_score: "84.00", technical_accuracy: "82.00", communication: "86.00", problem_solving: "83.00", explanation_quality: "85.00" },
    { label: "Sat", overall_score: "88.00", technical_accuracy: "86.00", communication: "89.00", problem_solving: "87.00", explanation_quality: "88.00" },
    { label: "Sun", overall_score: "91.00", technical_accuracy: "90.00", communication: "92.00", problem_solving: "91.00", explanation_quality: "90.00" },
  ],
  generated_at: new Date().toISOString(),
};
