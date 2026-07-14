export type ResumeSkill = {
  name: string;
  category: string;
  evidence_count: number;
  confidence: string;
};

export type MissingSkill = {
  name: string;
  category: string;
  priority: "high" | "medium" | "low";
  reason: string;
};

export type ResumeInterviewQuestion = {
  question: string;
  category: string;
  difficulty: "easy" | "medium" | "hard";
  signal: string;
};

export type SkillGapReport = {
  match_rate: string;
  strongest_categories: string[];
  weakest_categories: string[];
  priority_gaps: MissingSkill[];
  recommended_focus: string[];
  summary: string;
};

export type ResumeAnalysis = {
  id: string;
  filename: string;
  file_size: number;
  extracted_skills: ResumeSkill[];
  matched_skills: ResumeSkill[];
  missing_skills: MissingSkill[];
  ats_score: string;
  resume_suggestions: string[];
  interview_questions: ResumeInterviewQuestion[];
  skill_gap_report: SkillGapReport;
  analysis_summary: string;
  analyzer_version: string;
  analyzed_at: string;
};

export type ApiEnvelope<T> = {
  data: T | null;
  errors: Array<{ code: string; message: string; field?: string }>;
};
