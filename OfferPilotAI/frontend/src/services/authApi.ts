export type UserProfile = {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_verified: boolean;
  roles: string[];
  created_at: string;
  updated_at: string;
};

export type TokenPair = {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  refresh_expires_at: string;
};

export type AuthResponse = {
  user: UserProfile;
  tokens: TokenPair;
};

export type ForgotPasswordResponse = {
  message: string;
  reset_token?: string | null;
  expires_at?: string | null;
};

type ApiEnvelope<T> = {
  data: T | null;
  errors: Array<{ code: string; message: string; field?: string }>;
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "/api/v1";

export const authStorageKeys = {
  accessToken: "offerpilot-ai-access-token",
  refreshToken: "offerpilot-ai-refresh-token",
  user: "offerpilot-ai-user",
};

class AuthApiError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "AuthApiError";
  }
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");

  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    headers,
  });
  const envelope = (await response.json()) as ApiEnvelope<T>;

  if (!response.ok || envelope.errors.length) {
    throw new AuthApiError(envelope.errors[0]?.message ?? "Authentication request failed.");
  }
  if (envelope.data == null) {
    throw new AuthApiError("Authentication response did not include data.");
  }
  return envelope.data;
}

export async function login(payload: { email: string; password: string }) {
  return request<AuthResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function signup(payload: { full_name: string; email: string; password: string }) {
  return request<AuthResponse>("/auth/signup", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function forgotPassword(email: string) {
  return request<ForgotPasswordResponse>("/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export async function resetPassword(payload: { token: string; new_password: string }) {
  return request<{ password_reset: boolean }>("/auth/reset-password", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function logout(refreshToken: string | null) {
  const accessToken = window.localStorage.getItem(authStorageKeys.accessToken);
  const headers = new Headers();
  headers.set("Content-Type", "application/json");
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  await fetch(`${apiBaseUrl}/auth/logout`, {
    method: "POST",
    headers,
    body: JSON.stringify({ refresh_token: refreshToken }),
  }).catch(() => undefined);
}

export function persistAuth(auth: AuthResponse) {
  window.localStorage.setItem(authStorageKeys.accessToken, auth.tokens.access_token);
  window.localStorage.setItem("offerpilot_ai_access_token", auth.tokens.access_token);
  window.localStorage.setItem("access_token", auth.tokens.access_token);
  window.localStorage.setItem(authStorageKeys.refreshToken, auth.tokens.refresh_token);
  window.localStorage.setItem(authStorageKeys.user, JSON.stringify(auth.user));
}

export function clearAuth() {
  window.localStorage.removeItem(authStorageKeys.accessToken);
  window.localStorage.removeItem("offerpilot_ai_access_token");
  window.localStorage.removeItem("access_token");
  window.localStorage.removeItem(authStorageKeys.refreshToken);
  window.localStorage.removeItem(authStorageKeys.user);
}

export function readStoredUser(): UserProfile | null {
  const rawUser = window.localStorage.getItem(authStorageKeys.user);
  if (!rawUser) {
    return null;
  }

  try {
    return JSON.parse(rawUser) as UserProfile;
  } catch {
    clearAuth();
    return null;
  }
}
