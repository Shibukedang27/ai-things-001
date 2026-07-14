import type { ApiEnvelope, ResumeAnalysis } from "../features/resumeAnalyzer/types";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

function authHeaders() {
  const token =
    window.localStorage.getItem("offerpilot-ai-access-token") ??
    window.localStorage.getItem("offerpilot_ai_access_token") ??
    window.localStorage.getItem("access_token");

  return token ? { Authorization: `Bearer ${token}` } : {};
}

class ApiRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiRequestError";
  }
}

export async function analyzeResumePdf(file: File, jobDescription: string) {
  const formData = new FormData();
  formData.append("resume_file", file);
  if (jobDescription.trim()) {
    formData.append("job_description", jobDescription.trim());
  }

  const headers = new Headers();
  Object.entries(authHeaders()).forEach(([key, value]) => headers.set(key, value));

  const response = await fetch(`${apiBaseUrl}/resume-analyzer/analyze`, {
    method: "POST",
    headers,
    body: formData,
  });
  const envelope = (await response.json()) as ApiEnvelope<ResumeAnalysis>;
  if (!response.ok || envelope.errors.length) {
    throw new ApiRequestError(envelope.errors[0]?.message ?? "Resume analysis failed.");
  }
  if (!envelope.data) {
    throw new ApiRequestError("Resume analysis response did not include data.");
  }
  return envelope.data;
}
