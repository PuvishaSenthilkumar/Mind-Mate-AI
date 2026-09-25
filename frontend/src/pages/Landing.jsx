import { Link } from "react-router-dom";

export default function Landing() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <header className="flex-between" style={{ padding: "24px 48px" }}>
        <div className="flex gap-12" style={{ alignItems: "center" }}>
          <img src="/image1.png" alt="MindMate AI" style={{ width: 32, height: 32, objectFit: "contain" }} />
          <h2 style={{ color: "var(--neu-primary-dark)", fontWeight: 700, margin: 0 }}>MindMate AI</h2>
        </div>
        <div className="flex gap-12">
          <Link to="/login" className="btn btn-secondary">Log in</Link>
          <Link to="/register" className="btn btn-primary">Get Started</Link>
        </div>
      </header>

      <main style={{ flex: 1, display: "flex", alignItems: "center", padding: "0 48px" }}>
        <div style={{ maxWidth: 640, margin: "0 auto", textAlign: "center" }}>
          <h1 style={{ fontSize: 44, lineHeight: 1.2 }}>
            Your calm companion for a healthier mind
          </h1>
          <p className="text-soft" style={{ fontSize: 18, marginTop: 12 }}>
            Track your mood, journal your thoughts, build healthy habits, and chat
            with a supportive AI companion — built for students and young adults.
          </p>
          <div className="flex gap-12" style={{ justifyContent: "center", marginTop: 28 }}>
            <Link to="/register" className="btn btn-primary">Start your journey</Link>
            <Link to="/login" className="btn btn-secondary">I already have an account</Link>
          </div>

          <div className="grid-3 mt-24" style={{ textAlign: "left" }}>
            <div className="card">
              <h4>💬 AI Chat Support</h4>
              <p className="text-soft" style={{ fontSize: 14 }}>
                A judgment-free space to talk through your day and feelings.
              </p>
            </div>
            <div className="card">
              <h4>🌤️ Mood & Habits</h4>
              <p className="text-soft" style={{ fontSize: 14 }}>
                Track your mood, sleep, water, exercise, and screen time.
              </p>
            </div>
            <div className="card">
              <h4>🧘 Mindful Activities</h4>
              <p className="text-soft" style={{ fontSize: 14 }}>
                Breathing exercises, meditation timers, and gratitude prompts.
              </p>
            </div>
          </div>

          <div className="disclaimer-banner mt-24" style={{ textAlign: "left" }}>
            <strong>Important:</strong> MindMate AI is a wellness support tool, not a
            medical device, diagnostic tool, or replacement for therapy or professional
            mental-health care. If you are in crisis, please contact local emergency
            services or a crisis line immediately.
          </div>
        </div>
      </main>
    </div>
  );
}
