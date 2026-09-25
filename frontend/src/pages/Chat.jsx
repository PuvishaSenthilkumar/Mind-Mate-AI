import { useEffect, useRef, useState } from "react";
import api from "../api";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [crisisInfo, setCrisisInfo] = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    api.get("/chat/history").then((res) => setMessages(res.data));
  }, []);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim() || sending) return;

    const userMessage = { role: "user", content: input, id: `local-${Date.now()}` };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setSending(true);

    try {
      const res = await api.post("/chat", { message: userMessage.content });
      setMessages((prev) => [...prev, res.data.reply]);
      setCrisisInfo(res.data.crisis_resources || null);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't respond just now. Please try again.", id: `err-${Date.now()}` },
      ]);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "calc(100vh - 64px)" }}>
      <h1 style={{ fontWeight: 700, fontSize: 26, marginBottom: 16 }}>AI Chat Companion</h1>
      <div className="disclaimer-banner">
        MindMate is here to listen and support you — it's not a therapist and can't
        diagnose or treat conditions. In a crisis, please contact emergency services
        or a crisis line right away.
      </div>

      <div className="card" style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 14, background: "var(--neu-surface)" }}>
        {messages.length === 0 && (
          <p className="text-soft">Say hello — MindMate is here to listen. 🌱</p>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            style={{
              alignSelf: m.role === "user" ? "flex-end" : "flex-start",
              background: m.role === "user" ? "linear-gradient(145deg, var(--neu-primary), var(--neu-primary-dark))" : "var(--neu-surface)",
              color: m.role === "user" ? "white" : "var(--neu-text)",
              padding: "14px 20px",
              borderRadius: m.role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
              maxWidth: "70%",
              fontSize: 14.5,
              boxShadow: m.role === "user" 
                ? "6px 6px 12px rgba(95, 138, 122, 0.35), -6px -6px 12px rgba(143, 191, 174, 0.25)"
                : "var(--neu-shadow-soft)",
              lineHeight: 1.5,
            }}
          >
            {m.content}
          </div>
        ))}
        <div ref={bottomRef} />
      </div>

      {crisisInfo && (
        <div className="crisis-banner">
          <h4>You're not alone</h4>
          <p style={{ fontSize: 14 }}>{crisisInfo.message}</p>
          <p style={{ fontSize: 14 }}>
            <strong>{crisisInfo.hotline_name}:</strong> {crisisInfo.hotline_number} &nbsp;|&nbsp;
            <strong>Text support:</strong> {crisisInfo.text_line}
          </p>
          <a href={crisisInfo.international_resources_url} target="_blank" rel="noreferrer">
            Find international crisis resources →
          </a>
        </div>
      )}

      <form onSubmit={sendMessage} className="flex gap-12 mt-16">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Share what's on your mind…"
          disabled={sending}
        />
        <button className="btn btn-primary" type="submit" disabled={sending}>
          {sending ? "…" : "Send"}
        </button>
      </form>
    </div>
  );
}
