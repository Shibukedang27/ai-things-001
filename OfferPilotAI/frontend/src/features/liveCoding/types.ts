export type CodingLanguage = "python" | "java" | "sql";

export type CodeRunStatus = "success" | "failed" | "timeout" | "unsupported" | "skipped";

export type CodeIssue = {
  severity: "info" | "warning" | "error";
  message: string;
  line: number | null;
  rule: string;
};

export type CodeRunResult = {
  language: CodingLanguage;
  status: CodeRunStatus;
  stdout: string;
  stderr: string;
  exit_code: number | null;
  execution_time_ms: number | null;
  memory_kb: number | null;
  passed: boolean | null;
};

export type CodeAnalysisResult = {
  language: CodingLanguage;
  time_complexity: string;
  space_complexity: string;
  bugs: CodeIssue[];
  optimized_code: string;
  improvement_explanation: string;
  improvement_suggestions: string[];
  quality_score: string;
  observations: string[];
  analyzer_version: string;
};

export type CodeSubmission = {
  id: string;
  language: CodingLanguage;
  prompt_title: string;
  status: CodeRunStatus;
  time_complexity: string;
  space_complexity: string;
  execution_time_ms: number | null;
  submitted_at: string;
};

export type CodeTemplate = {
  language: CodingLanguage;
  label: string;
  promptTitle: string;
  prompt: string;
  sourceCode: string;
  stdin: string;
  expectedOutput: string;
};

export type ApiEnvelope<T> = {
  data: T | null;
  errors: Array<{ code: string; message: string; field?: string }>;
};
