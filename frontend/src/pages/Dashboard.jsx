import { useEffect, useState } from "react";
import api from "../api";
import MoodChart from "../components/MoodChart";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .get("/dashboard/summary")
      .then((res) => setSummary(res.data))
      .catch(() => setError("Couldn't load your dashboard right now."));
  }, []);

  if (error) return <p className="text-soft">{error}</p>;
  if (!summary) return <p className="text-soft">Loading your dashboard…</p>;

  return (
    <div>
      <h1 style={{ fontWeight: 700, fontSize: 28, marginBottom: 6 }}>Your Wellness Dashboard</h1>
      <p className="text-soft" style={{ marginBottom: 28, fontSize: 14 }}>A quick look at how you've been doing this week.</p>

      <div className="grid-3 mt-24">
        <div className="card" style={{ textAlign: "center", boxShadow: "var(--neu-shadow-raised)" }}>
          <div className="text-soft" style={{ fontSize: 13, fontWeight: 500, letterSpacing: "0.3px" }}>7-day mood average</div>
          <div style={{ fontSize: 36, fontWeight: 700, color: "var(--neu-primary-dark)", marginTop: 8 }}>
            {summary.mood_average_7d ?? "—"} {summary.mood_average_7d && "/ 5"}
          </div>
        </div>
        <div className="card" style={{ textAlign: "center", boxShadow: "var(--neu-shadow-raised)" }}>
          <div className="text-soft" style={{ fontSize: 13, fontWeight: 500, letterSpacing: "0.3px" }}>Current streak</div>
          <div style={{ fontSize: 36, fontWeight: 700, color: "var(--neu-primary-dark)", marginTop: 8 }}>
            {summary.current_streak || 0} 🔥
          </div>
          <div className="text-soft" style={{ fontSize: 12, marginTop: 4 }}>Best: {summary.best_streak || 0} days</div>
        </div>
        <div className="card" style={{ textAlign: "center", boxShadow: "var(--neu-shadow-raised)" }}>
          <div className="text-soft" style={{ fontSize: 13, fontWeight: 500, letterSpacing: "0.3px" }}>Active habits</div>
          <div style={{ fontSize: 36, fontWeight: 700, color: "var(--neu-primary-dark)", marginTop: 8 }}>
            {summary.habit_progress.length}
          </div>
        </div>
      </div>

      <div className="grid-2 mt-24">
        <div className="card">
          <h3>Mood Trend (7 days)</h3>
          <MoodChart data={summary.mood_trend} />
        </div>

        <div className="card">
          <h3>Habit Progress</h3>
          {summary.habit_progress.length === 0 && (
            <p className="text-soft">No habits set up yet — add one on the Habits page.</p>
          )}
          {summary.habit_progress.map((h) => (
            <div key={h.habit_type} className="flex-between" style={{ padding: "12px 0", borderBottom: "1px solid var(--neu-border)" }}>
              <div>
                <strong style={{ textTransform: "capitalize", fontWeight: 600 }}>{h.habit_type.replace("_", " ")}</strong>
                <div className="text-soft" style={{ fontSize: 13 }}>🔥 {h.current_streak}-day streak (best {h.best_streak})</div>
              </div>
              <div style={{ fontWeight: 700, color: "var(--neu-primary-dark)", fontSize: 15 }}>{h.completion_rate_7d}%</div>
            </div>
          ))}
        </div>
      </div>

      <div className="card mt-24">
        <h3>Personalized Insights</h3>
        <ul style={{ paddingLeft: 20 }}>
          {summary.insights.map((insight, i) => (
            <li key={i} style={{ marginBottom: 8 }}>{insight}</li>
          ))}
        </ul>
        <p className="text-soft mt-8" style={{ fontSize: 12.5 }}>
          These insights are generated from your own logged data and are not medical advice.
        </p>
      </div>
    </div>
  );
}
