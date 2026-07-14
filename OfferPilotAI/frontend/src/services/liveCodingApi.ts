import type {
  ApiEnvelope,
  CodeAnalysisResult,
  CodeRunResult,
  CodeSubmission,
  CodingLanguage,
} from "../features/liveCoding/types";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

type RunPayload = {
  language: CodingLanguage;
  source_code: string;
  stdin: string;
  expected_output?: string;
  timeout_seconds: number;
};

type AnalyzePayload = {
  language: CodingLanguage;
  source_code: string;
  prompt?: string;
};

type SubmitPayload = RunPayload & {
  prompt_title: string;
  prompt?: string;
  run_code: boolean;
  metadata?: Record<string, unknown>;
};

class ApiRequestError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "ApiRequestError";
  }
}

function authHeaders() {
  const token =
    window.localStorage.getItem("offerpilot-ai-access-token") ??
    window.localStorage.getItem("offerpilot_ai_access_token") ??
    window.localStorage.getItem("access_token");

  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  Object.entries(authHeaders()).forEach(([key, value]) => headers.set(key, value));

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers,
  });
  const envelope = (await response.json()) as ApiEnvelope<T>;
  if (!response.ok || envelope.errors.length) {
    throw new ApiRequestError(envelope.errors[0]?.message ?? "Live coding request failed.");
  }
  if (envelope.data == null) {
    throw new ApiRequestError("Live coding response did not include data.");
  }
  return envelope.data;
}

export async function runCode(payload: RunPayload) {
  return request<CodeRunResult>("/live-coding/run", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function analyzeCode(payload: AnalyzePayload) {
  return request<CodeAnalysisResult>("/live-coding/analyze", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function submitCode(payload: SubmitPayload) {
  return request<CodeSubmission>("/live-coding/submissions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
