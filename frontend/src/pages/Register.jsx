import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      const result = await register(fullName, email, password, phoneNumber || undefined);
      navigate(`/verify-email?email=${encodeURIComponent(result.email || email)}&method=email`);
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Registration failed. Please check your details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-split">
      {/* Left side - Registration Form */}
      <div className="auth-split-form" style={{ background: "linear-gradient(135deg, #e8ecf1 0%, #f0f4f3 50%, #e4eaf0 100%)" }}>
        <div className="card" style={{ width: 420, boxShadow: "var(--neu-shadow-raised)" }}>
          <h2 style={{ fontWeight: 700, fontSize: 24, marginBottom: 6 }}>Create your account</h2>
          <p className="text-soft" style={{ marginBottom: 24, fontSize: 14 }}>Start tracking your wellness today — it's free.</p>

          {error && (
            <div style={{ background: "linear-gradient(135deg, #fdeceb, #fbe5e3)", borderRadius: "var(--radius-md)", padding: "14px 18px", marginBottom: 20, color: "var(--neu-danger)", fontSize: 13.5, boxShadow: "var(--neu-shadow-soft)" }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="field">
              <label>Full name</label>
              <input required value={fullName} onChange={(e) => setFullName(e.target.value)} placeholder="Jordan Lee" />
            </div>
            <div className="field">
              <label>Email</label>
              <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
            </div>
            <div className="field">
              <label>Phone number (optional)</label>
              <input type="tel" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} placeholder="+91 98765 43210" />
            </div>
            <div className="field">
              <label>Password</label>
              <input type="password" required minLength={8} value={password} onChange={(e) => setPassword(e.target.value)} placeholder="At least 8 characters" />
            </div>
            <button className="btn btn-primary btn-block" type="submit" disabled={loading}>
              {loading ? "Creating account…" : "Create Account"}
            </button>
          </form>

          <p className="text-soft mt-16" style={{ textAlign: "center", fontSize: 14 }}>
            Already have an account? <Link to="/login" style={{ color: "var(--neu-primary-dark)", fontWeight: 600 }}>Log in</Link>
          </p>
        </div>
      </div>

      {/* Right side - Branding */}
      <div className="auth-split-branding" style={{ background: "linear-gradient(135deg, #e8ecf1 0%, #f0f4f3 50%, #e4eaf0 100%)" }}>
        <div style={{ position: "relative", zIndex: 1, maxWidth: 480 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
            <img src="/image1.png" alt="MindMate AI" style={{ width: 36, height: 36, objectFit: "contain" }} />
            <h2 style={{ color: "var(--neu-primary-dark)", fontWeight: 700, fontSize: 20, margin: 0 }}>MindMate AI</h2>
          </div>
          <h1 style={{ fontSize: 42, fontWeight: 700, lineHeight: 1.2, marginBottom: 20, color: "var(--neu-text)" }}>
            Your calm companion for a <span style={{ color: "var(--neu-primary-dark)" }}>healthier mind</span>
          </h1>
          <p style={{ fontSize: 16, color: "var(--neu-text-soft)", marginBottom: 40, lineHeight: 1.7 }}>
            Join thousands of students and young adults who are building healthier habits, tracking their mood, and finding support with MindMate AI.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {[
              { icon: "💬", title: "AI Chat Support", desc: "A judgment-free space to talk through your day and feelings." },
              { icon: "🌤️", title: "Mood & Habits", desc: "Track your mood, sleep, water, exercise, and screen time." },
              { icon: "🧘", title: "Mindful Activities", desc: "Breathing exercises, meditation timers, and gratitude prompts." },
            ].map((feature, i) => (
              <div key={i} style={{ display: "flex", gap: 16, alignItems: "flex-start" }}>
                <div style={{
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
                }}>
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
