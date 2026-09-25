import { useEffect, useState } from "react";
import api from "../api";

const HABIT_PRESETS = [
  { type: "sleep", label: "Sleep", unit: "hours", defaultTarget: 8 },
  { type: "water", label: "Water", unit: "glasses", defaultTarget: 8 },
  { type: "exercise", label: "Exercise", unit: "minutes", defaultTarget: 30 },
  { type: "screen_time", label: "Screen Time (max)", unit: "hours", defaultTarget: 4 },
];

export default function Habits() {
  const [habits, setHabits] = useState([]);
  const [logValues, setLogValues] = useState({});

  const load = () => api.get("/habits").then((res) => setHabits(res.data));
  useEffect(() => { load(); }, []);

  const addHabit = async (preset) => {
    if (habits.some((h) => h.habit_type === preset.type)) return;
    await api.post("/habits", {
      habit_type: preset.type,
      target_value: preset.defaultTarget,
      unit: preset.unit,
    });
    load();
  };

  const removeHabit = async (id) => {
    await api.delete(`/habits/${id}`);
    load();
  };

  const submitLog = async (habitId) => {
    const value = parseFloat(logValues[habitId]);
    if (isNaN(value)) return;
    await api.post(`/habits/${habitId}/log`, { value });
    setLogValues((prev) => ({ ...prev, [habitId]: "" }));
    load();
  };

  return (
    <div>
      <h1 style={{ fontWeight: 700, fontSize: 26, marginBottom: 6 }}>Habit Tracker</h1>
      <p className="text-soft" style={{ marginBottom: 24, fontSize: 14 }}>Build consistency, one day at a time.</p>

      <div className="card mt-16">
        <h3>Add a habit to track</h3>
        <div className="flex gap-12" style={{ flexWrap: "wrap" }}>
          {HABIT_PRESETS.map((p) => {
            const already = habits.some((h) => h.habit_type === p.type);
            return (
              <button
                key={p.type}
                className="btn btn-secondary"
                disabled={already}
                onClick={() => addHabit(p)}
              >
                {already ? `✓ ${p.label} added` : `+ ${p.label}`}
              </button>
            );
          })}
        </div>
      </div>

      <div className="grid-2 mt-24">
        {habits.map((h) => {
          const preset = HABIT_PRESETS.find((p) => p.type === h.habit_type);
          return (
            <div key={h.id} className="card">
              <div className="flex-between">
                <h3>{preset?.label || h.habit_type}</h3>
                <button className="btn btn-danger" style={{ padding: "4px 10px", fontSize: 12 }} onClick={() => removeHabit(h.id)}>Remove</button>
              </div>
              <p className="text-soft" style={{ fontSize: 13 }}>Target: {h.target_value} {h.unit}</p>
              <p style={{ fontWeight: 600 }}>🔥 {h.current_streak}-day streak <span className="text-soft" style={{ fontWeight: 400 }}>(best: {h.best_streak})</span></p>

              <div className="flex gap-12 mt-16">
                <input
                  type="number"
                  step="0.1"
                  placeholder={`Today's ${h.unit}`}
                  value={logValues[h.id] || ""}
                  onChange={(e) => setLogValues((prev) => ({ ...prev, [h.id]: e.target.value }))}
                />
                <button className="btn btn-primary" onClick={() => submitLog(h.id)}>Log</button>
              </div>
            </div>
          );
        })}
      </div>

      {habits.length === 0 && (
        <p className="text-soft mt-16">Add your first habit above to start building streaks.</p>
      )}
    </div>
  );
}
