import type { ResumeAnalysis } from "./types";

export const sampleResumeAnalysis: ResumeAnalysis = {
  id: "RES-1042",
  filename: "sample-backend-resume.pdf",
  file_size: 184000,
  extracted_skills: [
    { name: "Python", category: "Programming", evidence_count: 4, confidence: "100.00" },
    { name: "SQL", category: "Data", evidence_count: 3, confidence: "94.00" },
    { name: "AWS", category: "Cloud", evidence_count: 2, confidence: "82.00" },
    { name: "Docker", category: "DevOps", evidence_count: 2, confidence: "82.00" },
    { name: "Observability", category: "Operations", evidence_count: 2, confidence: "82.00" },
    { name: "Leadership", category: "Leadership", evidence_count: 2, confidence: "82.00" },
  ],
  matched_skills: [
    { name: "Python", category: "Programming", evidence_count: 2, confidence: "82.00" },
    { name: "SQL", category: "Data", evidence_count: 1, confidence: "70.00" },
    { name: "AWS", category: "Cloud", evidence_count: 1, confidence: "70.00" },
    { name: "Observability", category: "Operations", evidence_count: 1, confidence: "70.00" },
  ],
  missing_skills: [
    {
      name: "Kubernetes",
      category: "DevOps",
      priority: "medium",
      reason: "The target role mentions Kubernetes, but the resume does not show deployment ownership.",
    },
    {
      name: "Security",
      category: "Security",
      priority: "medium",
      reason: "The job description asks for security experience; add OAuth, JWT, or OWASP evidence if accurate.",
    },
    {
      name: "CI/CD",
      category: "DevOps",
      priority: "low",
      reason: "CI/CD appears in the job description but is not explicit in the resume.",
    },
  ],
  ats_score: "84.50",
  resume_suggestions: [
    "Add Kubernetes deployment evidence if applicable.",
    "Mirror job-description keywords in the skills section.",
    "Quantify reliability, latency, and scale outcomes in two more bullets.",
    "Add a concise summary aligned to the target backend role.",
  ],
  interview_questions: [
    {
      question: "Walk me through a project where you used Python. What tradeoffs did you make?",
      category: "Programming",
      difficulty: "medium",
      signal: "evidence_depth",
    },
    {
      question: "How did you design observability for one production system listed on your resume?",
      category: "Operations",
      difficulty: "hard",
      signal: "operational_judgment",
    },
    {
      question: "The role mentions Kubernetes. How would you ramp up and apply it in the first 30 days?",
      category: "DevOps",
      difficulty: "medium",
      signal: "skill_gap_reasoning",
    },
  ],
  skill_gap_report: {
    match_rate: "66.67",
    strongest_categories: ["Programming", "Data", "Operations"],
    weakest_categories: ["DevOps", "Security"],
    priority_gaps: [
      {
        name: "Kubernetes",
        category: "DevOps",
        priority: "medium",
        reason: "Add direct deployment, Helm, or cluster operations evidence.",
      },
    ],
    recommended_focus: ["Kubernetes", "Security", "CI/CD"],
    summary: "Skill match rate is 66.67%. Infrastructure and security gaps should be addressed before applying.",
  },
  analysis_summary:
    "ATS score is 84.50. The resume has strong backend alignment with a few infrastructure and security gaps.",
  analyzer_version: "heuristic-resume-analyzer-v1",
  analyzed_at: "Today",
};

export const sampleJobDescription =
  "Senior Backend Engineer role requiring Python, SQL, AWS, Kubernetes, system design, observability, security, CI/CD, and strong communication.";
