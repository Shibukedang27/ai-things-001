import type { DashboardData } from "./types";

export const dashboardData: DashboardData = {
  metrics: [
    { label: "Average Score", value: "82.4", delta: "+6.8 this month", trend: "up" },
    { label: "Highest Score", value: "96", delta: "System Design", trend: "up" },
    { label: "Interview Count", value: "38", delta: "9 this week", trend: "up" },
    { label: "Daily Streak", value: "14", delta: "Personal best", trend: "up" },
  ],
  weakTopics: [
    { topic: "Dynamic Programming", score: 54, category: "DSA" },
    { topic: "SQL Query Planning", score: 61, category: "SQL" },
    { topic: "Model Evaluation", score: 64, category: "Machine Learning" },
    { topic: "Prompt Grounding", score: 68, category: "Prompt Engineering" },
  ],
  strongTopics: [
    { topic: "System Design", score: 96, category: "Architecture" },
    { topic: "Python APIs", score: 92, category: "Backend" },
    { topic: "Behavioral STAR", score: 89, category: "Communication" },
    { topic: "NLP Concepts", score: 87, category: "AI" },
  ],
  recentInterviews: [
    { id: "INT-1048", role: "Senior Backend Engineer", type: "System Design", score: 96, date: "Today", status: "Completed" },
    { id: "INT-1047", role: "ML Engineer", type: "Machine Learning", score: 78, date: "Yesterday", status: "Needs Review" },
    { id: "INT-1046", role: "Data Engineer", type: "SQL", score: 81, date: "Jul 12", status: "Completed" },
    { id: "INT-1045", role: "Frontend Engineer", type: "Behavioral", score: 86, date: "Jul 11", status: "Completed" },
  ],
  performance: [
    { label: "Mon", score: 71, accuracy: 66, communication: 78 },
    { label: "Tue", score: 74, accuracy: 70, communication: 77 },
    { label: "Wed", score: 80, accuracy: 76, communication: 83 },
    { label: "Thu", score: 77, accuracy: 73, communication: 79 },
    { label: "Fri", score: 84, accuracy: 82, communication: 86 },
    { label: "Sat", score: 88, accuracy: 86, communication: 89 },
    { label: "Sun", score: 91, accuracy: 90, communication: 92 },
  ],
  learningProgress: [
    { title: "DSA Recovery Plan", progress: 62, detail: "18 of 29 tasks" },
    { title: "SQL Optimization", progress: 48, detail: "7 of 15 drills" },
    { title: "ML Interview Pack", progress: 74, detail: "11 of 15 modules" },
    { title: "System Design Mastery", progress: 86, detail: "6 of 7 simulations" },
  ],
  leaderboard: [
    { rank: 1, name: "Avery Chen", score: 965, streak: 21 },
    { rank: 2, name: "Maya Shah", score: 942, streak: 17 },
    { rank: 3, name: "You", score: 928, streak: 14, currentUser: true },
    { rank: 4, name: "Jordan Lee", score: 907, streak: 12 },
    { rank: 5, name: "Rina Patel", score: 889, streak: 11 },
  ],
};
