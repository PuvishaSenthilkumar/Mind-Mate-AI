import { useEffect, useState } from "react";
import api from "../api";
import MoodChart from "../components/MoodChart";

const MOODS = [
  { score: 5, label: "great", emoji: "😄" },
  { score: 4, label: "good", emoji: "🙂" },
  { score: 3, label: "okay", emoji: "😐" },
  { score: 2, label: "low", emoji: "😔" },
  { score: 1, label: "struggling", emoji: "😢" },
];

export default function MoodTracker() {
  const [entries, setEntries] = useState([]);
  const [selected, setSelected] = useState(null);
  const [note, setNote] = useState("");
  const [saving, setSaving] = useState(false);

  const loadEntries = () => {
    api.get("/mood").then((res) => setEntries(res.data));
  };

  useEffect(() => { loadEntries(); }, []);

  const submitMood = async () => {
    if (!selected) return;
    setSaving(true);
    try {
      await api.post("/mood", {
        mood_score: selected.score,
        mood_label: selected.label,
        note: note || null,
      });
      setNote("");
      setSelected(null);
      loadEntries();
    } finally {
      setSaving(false);
    }
  };

  const deleteEntry = async (id) => {
    await api.delete(`/mood/${id}`);
    loadEntries();
  };

  return (
    <div>
      <h1 style={{ fontWeight: 700, fontSize: 26, marginBottom: 6 }}>Mood Tracker</h1>
      <p className="text-soft" style={{ marginBottom: 24, fontSize: 14 }}>How are you feeling today?</p>

      <div className="card mt-16">
        <div className="flex gap-12" style={{ justifyContent: "center" }}>
          {MOODS.map((m) => (
            <button
              key={m.score}
              onClick={() => setSelected(m)}
              className="btn"
              style={{
                background: selected?.score === m.score ? "linear-gradient(145deg, var(--neu-primary), var(--neu-primary-dark))" : "var(--neu-surface)",
                color: selected?.score === m.score ? "white" : "var(--neu-text)",
                fontSize: 26,
                padding: "18px 22px",
                borderRadius: 18,
                boxShadow: selected?.score === m.score 
                  ? "6px 6px 12px rgba(95, 138, 122, 0.4), -6px -6px 12px rgba(143, 191, 174, 0.3)"
                  : "var(--neu-shadow-soft)",
                transition: "all 0.25s ease",
                minWidth: 80,
              }}
            >
              <div>{m.emoji}</div>
              <div style={{ fontSize: 12, marginTop: 4, textTransform: "capitalize" }}>{m.label}</div>
            </button>
          ))}
        </div>

        <div className="field mt-16">
          <label>Add a note (optional)</label>
          <textarea rows={3} value={note} onChange={(e) => setNote(e.target.value)} placeholder="What's contributing to this mood?" />
        </div>
        <button className="btn btn-primary" disabled={!selected || saving} onClick={submitMood}>
          {saving ? "Saving…" : "Log Mood"}
        </button>
      </div>

      <div className="grid-2 mt-24">
        <div className="card">
          <h3>Mood Trend</h3>
          <MoodChart data={entries.slice(-30)} />
        </div>

        <div className="card" style={{ maxHeight: 340, overflowY: "auto" }}>
          <h3>Recent Entries</h3>
          {entries.length === 0 && <p className="text-soft">No entries yet.</p>}
          {[...entries].reverse().map((e) => (
            <div key={e.id} className="flex-between" style={{ padding: "12px 0", borderBottom: "1px solid var(--neu-border)" }}>
              <div>
                <strong>{MOODS.find((m) => m.score === e.mood_score)?.emoji} {e.mood_label}</strong>
                <div className="text-soft" style={{ fontSize: 12 }}>{e.entry_date}</div>
                {e.note && <div style={{ fontSize: 13, marginTop: 4 }}>{e.note}</div>}
              </div>
              <button className="btn btn-secondary" style={{ padding: "6px 10px", fontSize: 12 }} onClick={() => deleteEntry(e.id)}>
                Delete
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
