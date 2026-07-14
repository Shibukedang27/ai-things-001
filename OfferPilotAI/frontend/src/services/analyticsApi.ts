import type { AnalyticsOverview, ApiEnvelope } from "../features/analytics/types";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

function authHeaders() {
  const token =
    window.localStorage.getItem("offerpilot-ai-access-token") ??
    window.localStorage.getItem("offerpilot_ai_access_token") ??
    window.localStorage.getItem("access_token");

  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function fetchAnalyticsOverview() {
  const headers = new Headers();
  Object.entries(authHeaders()).forEach(([key, value]) => headers.set(key, value));

  const response = await fetch(`${apiBaseUrl}/analytics/overview`, { headers });
  const envelope = (await response.json()) as ApiEnvelope<AnalyticsOverview>;
  if (!response.ok || envelope.errors.length) {
    throw new Error(envelope.errors[0]?.message ?? "Analytics request failed.");
  }
  if (!envelope.data) {
    throw new Error("Analytics response did not include data.");
  }
  return envelope.data;
}
