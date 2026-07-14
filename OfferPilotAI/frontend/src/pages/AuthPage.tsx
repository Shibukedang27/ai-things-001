import { FormEvent, useMemo, useState } from "react";
import {
  ArrowRight,
  BadgeCheck,
  BriefcaseBusiness,
  Eye,
  EyeOff,
  KeyRound,
  LockKeyhole,
  Mail,
  Moon,
  RotateCcw,
  ShieldCheck,
  Sparkles,
  Sun,
  UserRound,
} from "lucide-react";

import {
  AuthResponse,
  forgotPassword,
  login,
  persistAuth,
  resetPassword,
  signup,
} from "../services/authApi";

type AuthMode = "login" | "signup" | "forgot";

type AuthPageProps = {
  theme: "dark" | "light";
  onToggleTheme: () => void;
  onAuthenticated: (auth: AuthResponse) => void;
  onViewLanding: () => void;
};

const demoCredentials = {
  email: "candidate@example.com",
  password: "OfferPilotAI!2026",
};

export function AuthPage({ theme, onToggleTheme, onAuthenticated, onViewLanding }: AuthPageProps) {
  const [mode, setMode] = useState<AuthMode>("login");
  const [fullName, setFullName] = useState("Alex Candidate");
  const [email, setEmail] = useState(demoCredentials.email);
  const [password, setPassword] = useState(demoCredentials.password);
  const [resetToken, setResetToken] = useState("");
  const [newPassword, setNewPassword] = useState("OfferPilotAI!2026");
  const [showPassword, setShowPassword] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const heading = useMemo(() => {
    if (mode === "signup") {
      return "Create your readiness workspace";
    }
    if (mode === "forgot") {
      return "Recover your account";
    }
    return "Sign in to OfferPilot AI";
  }, [mode]);

  const submitAuth = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setIsSubmitting(true);

    try {
      if (mode === "login") {
        const auth = await login({ email, password });
        persistAuth(auth);
        onAuthenticated(auth);
        return;
      }

      if (mode === "signup") {
        const auth = await signup({ full_name: fullName, email, password });
        persistAuth(auth);
        onAuthenticated(auth);
        return;
      }

      const response = await forgotPassword(email);
      setMessage(response.reset_token ? `${response.message} Reset token generated below.` : response.message);
      if (response.reset_token) {
        setResetToken(response.reset_token);
      }
    } catch (authError) {
      const fallback =
        "Could not reach the auth service. Start the full stack with ./scripts/start.sh, then try again.";
      setError(authError instanceof Error ? authError.message : fallback);
    } finally {
      setIsSubmitting(false);
    }
  };

  const submitReset = async () => {
    setError(null);
    setMessage(null);
    setIsSubmitting(true);

    try {
      await resetPassword({ token: resetToken, new_password: newPassword });
      setMessage("Password reset complete. Sign in with your new password.");
      setMode("login");
      setPassword(newPassword);
    } catch (resetError) {
      setError(resetError instanceof Error ? resetError.message : "Password reset failed.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const useDemoAccount = () => {
    setMode("login");
    setEmail(demoCredentials.email);
    setPassword(demoCredentials.password);
    setMessage("Demo credentials loaded. Sign in to continue.");
    setError(null);
  };

  return (
    <main className="auth-page">
      <section className="auth-brand-panel">
        <div className="auth-brand-top">
          <span className="brand-mark">OP</span>
          <div>
            <strong>OfferPilot AI</strong>
            <small>Interview Intelligence</small>
          </div>
        </div>

        <div className="auth-brand-copy">
          <p className="landing-eyebrow">
            <Sparkles size={16} />
            Offer readiness starts here
          </p>
          <h1>Practice, evaluate, improve, and walk into interviews with signal.</h1>
          <p>
            Secure login, role-based sessions, AI scoring, live coding, resume analysis, and personalized roadmaps
            are wired behind one production-ready product flow.
          </p>
        </div>

        <div className="auth-proof-grid" aria-label="Platform readiness">
          <span>
            <BadgeCheck size={18} />
            JWT auth
          </span>
          <span>
            <BriefcaseBusiness size={18} />
            Role workflows
          </span>
          <span>
            <ShieldCheck size={18} />
            Protected APIs
          </span>
        </div>
      </section>

      <section className="auth-form-panel" aria-label="Authentication">
        <div className="auth-form-top">
          <button className="secondary-action" type="button" onClick={onViewLanding}>
            View landing
          </button>
          <button className="icon-button" type="button" aria-label="Toggle theme" title="Toggle theme" onClick={onToggleTheme}>
            {theme === "dark" ? <Sun size={19} /> : <Moon size={19} />}
          </button>
        </div>

        <div className="auth-card">
          <div className="auth-card-heading">
            <p className="landing-eyebrow">
              <LockKeyhole size={16} />
              Secure access
            </p>
            <h2>{heading}</h2>
            <p>
              Use the seeded demo account or create a new account when the backend stack is running.
            </p>
          </div>

          <div className="auth-tabs" role="tablist" aria-label="Authentication mode">
            {(["login", "signup", "forgot"] as AuthMode[]).map((item) => (
              <button
                className={mode === item ? "active" : ""}
                key={item}
                type="button"
                onClick={() => {
                  setMode(item);
                  setError(null);
                  setMessage(null);
                }}
              >
                {item === "login" ? "Login" : item === "signup" ? "Signup" : "Forgot"}
              </button>
            ))}
          </div>

          <form className="auth-form" onSubmit={submitAuth}>
            {mode === "signup" && (
              <label>
                <span>Full name</span>
                <div className="auth-input">
                  <UserRound size={18} />
                  <input
                    autoComplete="name"
                    minLength={2}
                    onChange={(event) => setFullName(event.target.value)}
                    required
                    type="text"
                    value={fullName}
                  />
                </div>
              </label>
            )}

            <label>
              <span>Email</span>
              <div className="auth-input">
                <Mail size={18} />
                <input
                  autoComplete="email"
                  onChange={(event) => setEmail(event.target.value)}
                  required
                  type="email"
                  value={email}
                />
              </div>
            </label>

            {mode !== "forgot" && (
              <label>
                <span>Password</span>
                <div className="auth-input">
                  <KeyRound size={18} />
                  <input
                    autoComplete={mode === "login" ? "current-password" : "new-password"}
                    minLength={mode === "signup" ? 12 : 1}
                    onChange={(event) => setPassword(event.target.value)}
                    required
                    type={showPassword ? "text" : "password"}
                    value={password}
                  />
                  <button
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    type="button"
                    onClick={() => setShowPassword((current) => !current)}
                  >
                    {showPassword ? <EyeOff size={17} /> : <Eye size={17} />}
                  </button>
                </div>
              </label>
            )}

            {mode === "signup" && (
              <p className="auth-hint">Use at least 12 characters with uppercase, lowercase, number, and symbol.</p>
            )}

            {message && <div className="auth-message status-success">{message}</div>}
            {error && <div className="auth-message status-failed">{error}</div>}

            <button className="primary-action auth-submit" disabled={isSubmitting} type="submit">
              {isSubmitting ? "Working..." : mode === "login" ? "Login" : mode === "signup" ? "Create account" : "Send reset link"}
              <ArrowRight size={18} />
            </button>
          </form>

          {mode === "forgot" && resetToken && (
            <div className="reset-box">
              <label>
                <span>Reset token</span>
                <textarea onChange={(event) => setResetToken(event.target.value)} value={resetToken} />
              </label>
              <label>
                <span>New password</span>
                <input
                  minLength={12}
                  onChange={(event) => setNewPassword(event.target.value)}
                  type="password"
                  value={newPassword}
                />
              </label>
              <button className="secondary-action" disabled={isSubmitting} type="button" onClick={submitReset}>
                <RotateCcw size={17} />
                Reset password
              </button>
            </div>
          )}

          <div className="demo-credentials">
            <div>
              <strong>Demo account</strong>
              <span>{demoCredentials.email}</span>
              <span>{demoCredentials.password}</span>
            </div>
            <button className="secondary-action" type="button" onClick={useDemoAccount}>
              Use demo
            </button>
          </div>
        </div>
      </section>
    </main>
  );
}
