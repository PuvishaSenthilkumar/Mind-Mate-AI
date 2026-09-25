import { useEffect, useState } from "react";
import api from "../api";

const sentimentBadge = (s) => {
  if (s === "positive") return "badge-positive";
  if (s === "negative") return "badge-negative";
  return "badge-neutral";
};

export default function Journal() {
  const [entries, setEntries] = useState([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState(null);

  const load = () => api.get("/journal").then((res) => setEntries(res.data));
  useEffect(() => { load(); }, []);

  const resetForm = () => {
    setTitle("");
    setContent("");
    setEditingId(null);
  };

  const handleSave = async () => {
    if (!content.trim()) return;
    setSaving(true);
    try {
      if (editingId) {
        await api.put(`/journal/${editingId}`, { title, content });
      } else {
        await api.post("/journal", { title, content });
      }
      resetForm();
      load();
    } finally {
      setSaving(false);
    }
  };

  const handleEdit = (entry) => {
    setEditingId(entry.id);
    setTitle(entry.title || "");
    setContent(entry.content);
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleDelete = async (id) => {
    await api.delete(`/journal/${id}`);
    if (editingId === id) resetForm();
    load();
  };

  return (
    <div>
      <h1 style={{ fontWeight: 700, fontSize: 26, marginBottom: 6 }}>Smart Journal</h1>
      <p className="text-soft" style={{ marginBottom: 24, fontSize: 14 }}>Write freely — MindMate will gently summarize and reflect your entry.</p>

      <div className="card mt-16">
        <div className="field">
          <label>Title (optional)</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Give this entry a title" />
        </div>
        <div className="field">
          <label>What's on your mind?</label>
          <textarea rows={6} value={content} onChange={(e) => setContent(e.target.value)} placeholder="Write about your day, thoughts, or feelings…" />
        </div>
        <div className="flex gap-12">
          <button className="btn btn-primary" onClick={handleSave} disabled={saving || !content.trim()}>
            {saving ? "Saving…" : editingId ? "Update Entry" : "Save Entry"}
          </button>
          {editingId && (
            <button className="btn btn-secondary" onClick={resetForm}>Cancel</button>
          )}
        </div>
      </div>

      <div className="mt-24" style={{ display: "flex", flexDirection: "column", gap: 16 }}>
        {entries.length === 0 && <p className="text-soft">No journal entries yet.</p>}
        {entries.map((e) => (
          <div key={e.id} className="card">
            <div className="flex-between">
              <h3>{e.title || "Untitled entry"}</h3>
              <span className={`badge ${sentimentBadge(e.sentiment)}`}>{e.sentiment || "neutral"}</span>
            </div>
            <p style={{ whiteSpace: "pre-wrap" }}>{e.content}</p>
            {e.ai_summary && (
              <div className="card" style={{ background: "var(--neu-surface)", marginTop: 14, padding: 16, boxShadow: "var(--neu-shadow-soft)" }}>
                <strong style={{ fontSize: 13 }}>✨ AI Reflection</strong>
                <p style={{ fontSize: 14, marginTop: 6 }}>{e.ai_summary}</p>
              </div>
            )}
            {e.flagged_concern && (
              <div className="crisis-banner mt-16">
                <p style={{ fontSize: 13.5 }}>
                  This entry contains language that may reflect real distress. If you're
                  struggling, please reach out to someone you trust or a crisis line —
                  you don't have to go through this alone.
                </p>
              </div>
            )}
            <div className="flex gap-12 mt-16">
              <button className="btn btn-secondary" style={{ padding: "6px 14px", fontSize: 13 }} onClick={() => handleEdit(e)}>Edit</button>
              <button className="btn btn-danger" style={{ padding: "6px 14px", fontSize: 13 }} onClick={() => handleDelete(e.id)}>Delete</button>
            </div>
            <div className="text-soft mt-8" style={{ fontSize: 12 }}>{new Date(e.created_at).toLocaleString()}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
