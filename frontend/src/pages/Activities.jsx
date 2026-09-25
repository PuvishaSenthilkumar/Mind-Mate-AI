import { useEffect, useRef, useState } from "react";
import api from "../api";

function BreathingExercise({ onComplete }) {
  const [phase, setPhase] = useState("Get ready…");
  const [running, setRunning] = useState(false);
  const timerRef = useRef(null);
  const secondsRef = useRef(0);

  const start = () => {
    setRunning(true);
    secondsRef.current = 0;
    const cycle = ["Breathe in…", "Hold…", "Breathe out…", "Hold…"];
    let i = 0;
    setPhase(cycle[0]);
    timerRef.current = setInterval(() => {
      i = (i + 1) % cycle.length;
      setPhase(cycle[i]);
      secondsRef.current += 4;
    }, 4000);
  };

  const stop = () => {
    clearInterval(timerRef.current);
    setRunning(false);
    setPhase("Get ready…");
    onComplete(secondsRef.current);
  };

  useEffect(() => () => clearInterval(timerRef.current), []);

  return (
    <div className="card" style={{ textAlign: "center" }}>
      <h3>Breathing Exercise</h3>
      <div
        style={{
          width: 140, height: 140, borderRadius: "50%",
          background: "linear-gradient(145deg, var(--neu-secondary), var(--neu-primary))",
          margin: "20px auto", display: "flex", alignItems: "center",
          justifyContent: "center", color: "white", fontWeight: 600,
          transform: running ? "scale(1.1)" : "scale(1)",
          transition: "transform 3.8s ease-in-out",
          boxShadow: "8px 8px 16px rgba(163, 177, 198, 0.5), -8px -8px 16px rgba(255, 255, 255, 0.8)",
        }}
      >
        {phase}
      </div>
      {!running ? (
        <button className="btn btn-primary" onClick={start}>Start 4-4-4-4 Breathing</button>
      ) : (
        <button className="btn btn-secondary" onClick={stop}>Stop</button>
      )}
    </div>
  );
}

function MeditationTimer({ onComplete }) {
  const [duration, setDuration] = useState(300);
  const [remaining, setRemaining] = useState(300);
  const [running, setRunning] = useState(false);
  const timerRef = useRef(null);

  const start = () => {
    setRemaining(duration);
    setRunning(true);
    timerRef.current = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          clearInterval(timerRef.current);
          setRunning(false);
          onComplete(duration);
          return 0;
        }
        return r - 1;
      });
    }, 1000);
  };

  const stop = () => {
    clearInterval(timerRef.current);
    setRunning(false);
    onComplete(duration - remaining);
  };

  useEffect(() => () => clearInterval(timerRef.current), []);

  const mm = String(Math.floor(remaining / 60)).padStart(2, "0");
  const ss = String(remaining % 60).padStart(2, "0");

  return (
    <div className="card" style={{ textAlign: "center" }}>
      <h3>Meditation Timer</h3>
      <div style={{ fontSize: 44, fontWeight: 700, margin: "16px 0", color: "var(--neu-primary-dark)" }}>
        {mm}:{ss}
      </div>
      {!running && (
        <select value={duration} onChange={(e) => setDuration(Number(e.target.value))} style={{ marginBottom: 12 }}>
          <option value={60}>1 minute</option>
          <option value={300}>5 minutes</option>
          <option value={600}>10 minutes</option>
          <option value={900}>15 minutes</option>
        </select>
      )}
      <div>
        {!running ? (
          <button className="btn btn-primary" onClick={start}>Start Meditation</button>
        ) : (
          <button className="btn btn-secondary" onClick={stop}>Stop</button>
        )}
      </div>
    </div>
  );
}

function GratitudeJournal() {
  const [entry, setEntry] = useState("");
  const [saved, setSaved] = useState(false);

  const save = async () => {
    if (!entry.trim()) return;
    await api.post("/activities", { activity_type: "gratitude", duration_seconds: 0, notes: entry });
    setEntry("");
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <div className="card">
      <h3>Gratitude Journal</h3>
      <p className="text-soft" style={{ fontSize: 14 }}>What's one small thing you're grateful for today?</p>
      <textarea rows={3} value={entry} onChange={(e) => setEntry(e.target.value)} placeholder="I'm grateful for…" />
      <button className="btn btn-primary mt-16" onClick={save}>Save Gratitude Note</button>
      {saved && <p className="text-soft mt-8">✓ Saved — nice reflection!</p>}
    </div>
  );
}

function StressRelief() {
  const tips = [
    "Unclench your jaw and drop your shoulders.",
    "Step outside for 2 minutes of fresh air.",
    "Drink a glass of water slowly and mindfully.",
    "Write down one thing you can control right now.",
    "Stretch your arms overhead and hold for 10 seconds.",
  ];
  const [tip, setTip] = useState(tips[0]);

  return (
    <div className="card">
      <h3>Quick Stress Relief</h3>
      <p style={{ fontSize: 15, minHeight: 40 }}>{tip}</p>
      <button className="btn btn-secondary" onClick={() => setTip(tips[Math.floor(Math.random() * tips.length)])}>
        Give me another tip
      </button>
    </div>
  );
}

export default function Activities() {
  const logActivity = async (type, duration) => {
    if (duration <= 0) return;
    await api.post("/activities", { activity_type: type, duration_seconds: duration });
  };

  return (
    <div>
      <h1 style={{ fontWeight: 700, fontSize: 26, marginBottom: 6 }}>Wellness Activities</h1>
      <p className="text-soft" style={{ marginBottom: 28, fontSize: 14 }}>Small, science-informed practices to help you reset.</p>

      <div className="grid-2 mt-16">
        <BreathingExercise onComplete={(sec) => logActivity("breathing", sec)} />
        <MeditationTimer onComplete={(sec) => logActivity("meditation", sec)} />
        <GratitudeJournal />
        <StressRelief />
      </div>
    </div>
  );
}
