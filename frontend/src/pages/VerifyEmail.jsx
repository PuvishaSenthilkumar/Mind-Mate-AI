import { useEffect, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const email = searchParams.get("email") || "";
  const [otp, setOtp] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const [resending, setResending] = useState(false);
  const { verifyOtp, requestOtp, pendingEmail } = useAuth();
  const navigate = useNavigate();

  const targetEmail = email || pendingEmail || "";

  useEffect(() => {
    if (!email && pendingEmail) {
      window.location.replace(`/verify-email?email=${encodeURIComponent(pendingEmail)}&method=email`);
    }
  }, [email, pendingEmail]);

  const handleVerify = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      await verifyOtp(targetEmail, otp, null, "email");
      setSuccess("Verified successfully! Redirecting…");
      setTimeout(() => navigate("/dashboard"), 800);
    } catch (err) {
      setError(err.response?.data?.detail || "Invalid or expired OTP. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setError("");
    setResending(true);
    try {
      await requestOtp(targetEmail, null, "email");
      setSuccess("A new OTP has been sent.");
    } catch (err) {
      setError(err.response?.data?.detail || "Could not resend OTP. Please try again.");
    } finally {
      setResending(false);
    }
  };

  return (
     <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div className="card" style={{ width: 420, boxShadow: "var(--neu-shadow-raised)" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10, marginBottom: 16 }}>
          <img src="/image1.png" alt="MindMate AI" style={{ width: 32, height: 32, objectFit: "contain" }} />
        </div>
        <h2 style={{ fontWeight: 700, fontSize: 24, marginBottom: 6, textAlign: "center" }}>Verify your email</h2>
        <p className="text-soft" style={{ marginBottom: 24, fontSize: 14 }}>
          We sent a 6-digit code to <strong>{targetEmail}</strong>. Enter it below to activate your account.
        </p>

        {error && <div style={{ background: "linear-gradient(135deg, #fdeceb, #fbe5e3)", borderRadius: "var(--radius-md)", padding: "14px 18px", marginBottom: 20, color: "var(--neu-danger)", fontSize: 13.5, boxShadow: "var(--neu-shadow-soft)" }}>{error}</div>}
        {success && <div style={{ background: "linear-gradient(135deg, #e4f2ec, #d4e8de)", borderRadius: "var(--radius-md)", padding: "14px 18px", marginBottom: 20, color: "var(--neu-primary-dark)", fontSize: 13.5, boxShadow: "var(--neu-shadow-soft)" }}>{success}</div>}

        <form onSubmit={handleVerify}>
          <div className="field">
            <label>Verification code</label>
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
          <button className="btn btn-primary btn-block" type="submit" disabled={loading || otp.length !== 6}>
            {loading ? "Verifying…" : "Verify Email"}
          </button>
        </form>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16 }}>
          <button className="btn btn-secondary" onClick={handleResend} disabled={resending} style={{ padding: "10px 18px", fontSize: 13.5 }}>
            {resending ? "Resending…" : "Resend OTP"}
          </button>
        </div>
        <div style={{ textAlign: "center", marginTop: 12 }}>
          <Link to="/login" style={{ fontSize: 13.5, color: "var(--neu-primary-dark)" }}>Back to login</Link>
        </div>
      </div>
    </div>
  );
}
