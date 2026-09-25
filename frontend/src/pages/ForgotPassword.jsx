import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../api";

export default function ForgotPassword() {
  const [step, setStep] = useState("email");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSendReset = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await api.post("/auth/forgot-password", { email });
      setStep("otp");
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (newPassword !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      await api.post("/auth/reset-password", {
        email,
        otp_code: otp,
        new_password: newPassword,
      });
      setSuccess("Your password has been reset successfully! Redirecting to login…");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setError(err.response?.data?.detail || "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split">
      <div className="auth-split-form" style={{ background: "linear-gradient(135deg, #e8ecf1 0%, #f0f4f3 50%, #e4eaf0 100%)" }}>
        <div className="card" style={{ width: 420, boxShadow: "var(--neu-shadow-raised)" }}>
          <h2 style={{ fontWeight: 700, fontSize: 24, marginBottom: 6 }}>
            {step === "email" ? "Forgot password?" : "Reset password"}
          </h2>
          <p className="text-soft" style={{ marginBottom: 24, fontSize: 14 }}>
            {step === "email"
              ? "Enter your email and we'll send you a 6-digit reset code."
              : "Enter the reset code we sent to your email along with your new password."}
          </p>

          {error && (
            <div
              style={{
                background: "linear-gradient(135deg, #fdeceb, #fbe5e3)",
                borderRadius: "var(--radius-md)",
                padding: "14px 18px",
                marginBottom: 20,
                color: "var(--neu-danger)",
                fontSize: 13.5,
                boxShadow: "var(--neu-shadow-soft)",
              }}
            >
              {error}
            </div>
          )}

          {success && (
            <div
              style={{
                background: "linear-gradient(135deg, #e4f2ec, #d4e8de)",
                borderRadius: "var(--radius-md)",
                padding: "14px 18px",
                marginBottom: 20,
                color: "var(--neu-primary-dark)",
                fontSize: 13.5,
                boxShadow: "var(--neu-shadow-soft)",
              }}
            >
              {success}
            </div>
          )}

          {step === "email" && (
            <form onSubmit={handleSendReset}>
              <div className="field">
                <label>Email address</label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                />
              </div>
              <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
                {loading ? "Sending…" : "Send Reset Code"}
              </button>
            </form>
          )}

          {step === "otp" && (
            <form onSubmit={handleResetPassword}>
              <div className="field">
                <label>Reset code</label>
                <input
                  type="text"
                  required
                  maxLength={6}
                  inputMode="numeric"
                  pattern="[0-9]{6}"
                  value={otp}
                  onChange={(e) => setOtp(e.target.value.replace(/\D/g, "").slice(0, 6))}
                  placeholder="123456"
                  style={{ textAlign: "center", fontSize: 22, letterSpacing: 8, fontWeight: 600 }}
                />
              </div>
              <div className="field">
                <label>New password</label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </div>
              <div className="field">
                <label>Confirm new password</label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </div>
              <button className="btn btn-primary btn-block" type="submit" disabled={loading || otp.length !== 6}>
                {loading ? "Resetting…" : "Reset Password"}
              </button>
            </form>
          )}

          <p className="text-soft" style={{ textAlign: "center", marginTop: 24, fontSize: 14 }}>
            <Link to="/login" style={{ color: "var(--neu-primary-dark)", fontWeight: 600 }}>
              Back to login
            </Link>
          </p>
        </div>
      </div>

      <div
        className="auth-split-branding"
        style={{ background: "linear-gradient(135deg, #e8ecf1 0%, #f0f4f3 50%, #e4eaf0 100%)" }}
      >
        <div style={{ position: "relative", zIndex: 1, maxWidth: 480 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
            <img src="/image1.png" alt="MindMate AI" style={{ width: 36, height: 36, objectFit: "contain" }} />
            <h2 style={{ color: "var(--neu-primary-dark)", fontWeight: 700, fontSize: 20, margin: 0 }}>MindMate AI</h2>
          </div>
          <h1 style={{ fontSize: 42, fontWeight: 700, lineHeight: 1.2, marginBottom: 20, color: "var(--neu-text)" }}>
            Your calm companion for a <span style={{ color: "var(--neu-primary-dark)" }}>healthier mind</span>
          </h1>
          <p style={{ fontSize: 16, color: "var(--neu-text-soft)", marginBottom: 40, lineHeight: 1.7 }}>
            MindMate AI helps you track your mood, journal your thoughts, build healthy habits, and chat with a supportive AI companion — built for students and young adults.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {[
              { icon: "💬", title: "AI Chat Support", desc: "A judgment-free space to talk through your day and feelings." },
              { icon: "🌤️", title: "Mood & Habits", desc: "Track your mood, sleep, water, exercise, and screen time." },
              { icon: "🧘", title: "Mindful Activities", desc: "Breathing exercises, meditation timers, and gratitude prompts." },
            ].map((feature, i) => (
              <div key={i} style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
                <div
                  style={{
                    width: 48,
                    height: 48,
                    borderRadius: "var(--radius-sm)",
                    background: "var(--neu-surface)",
                    boxShadow: "var(--neu-shadow-soft)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    fontSize: 22,
                    flexShrink: 0,
                  }}
                >
                  {feature.icon}
                </div>
                <div>
                  <h3 style={{ fontSize: 16, fontWeight: 600, marginBottom: 4, color: "var(--neu-text)" }}>{feature.title}</h3>
                  <p style={{ fontSize: 14, color: "var(--neu-text-soft)", lineHeight: 1.5 }}>{feature.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
