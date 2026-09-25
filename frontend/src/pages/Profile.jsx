import { useEffect, useState } from "react";
import api from "../api";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

export default function Profile() {
  const { user, updateUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [phoneNumber, setPhoneNumber] = useState(user?.phone_number || "");
  const [dataSharing, setDataSharing] = useState(user?.data_sharing_opt_in || false);
  const [aiChatEnabled, setAiChatEnabled] = useState(user?.ai_chat_enabled ?? true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const { theme, toggleTheme } = useTheme();
  const [safetyInfo, setSafetyInfo] = useState(null);

  useEffect(() => {
    api.get("/safety-info").then((res) => setSafetyInfo(res.data));
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const res = await api.put("/auth/me", {
        full_name: fullName,
        phone_number: phoneNumber || null,
        data_sharing_opt_in: dataSharing,
        ai_chat_enabled: aiChatEnabled,
      });
      updateUser(res.data);
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div>
      <h1 style={{ fontWeight: 700, fontSize: 26, marginBottom: 6 }}>Profile & Settings</h1>

      <div className="card mt-16" style={{ maxWidth: 560 }}>
        <h3>Account</h3>
        <div className="field">
          <label>Full name</label>
          <input value={fullName} onChange={(e) => setFullName(e.target.value)} />
        </div>
        <div className="field">
          <label>Email</label>
          <input value={user?.email} disabled />
          {user?.email_verified ? (
            <span style={{ color: "var(--neu-primary-dark)", fontSize: 12 }}>✓ Verified</span>
          ) : (
            <span style={{ color: "var(--neu-danger)", fontSize: 12 }}>Not verified</span>
          )}
        </div>
        <div className="field">
          <label>Phone number</label>
          <input type="tel" value={phoneNumber} onChange={(e) => setPhoneNumber(e.target.value)} placeholder="+91 98765 43210" />
          {user?.phone_verified ? (
            <span style={{ color: "var(--neu-primary-dark)", fontSize: 12 }}>✓ Verified</span>
          ) : user?.phone_number ? (
            <span style={{ color: "var(--neu-danger)", fontSize: 12 }}>Not verified</span>
          ) : null}
        </div>

        <h3 className="mt-24">Appearance</h3>
        <button className="btn btn-secondary" onClick={toggleTheme} style={{ marginBottom: 20 }}>
          {theme === "dark" ? "☀️ Switch to Light Mode" : "🌙 Switch to Dark Mode"}
        </button>

        <h3 className="mt-24">Privacy Controls</h3>
        <label className="flex gap-8" style={{ alignItems: "center", fontWeight: 500, marginBottom: 12 }}>
          <input type="checkbox" style={{ width: "auto" }} checked={aiChatEnabled} onChange={(e) => setAiChatEnabled(e.target.checked)} />
          Enable AI Chat Companion
        </label>
        <label className="flex gap-8" style={{ alignItems: "center", fontWeight: 500 }}>
          <input type="checkbox" style={{ width: "auto" }} checked={dataSharing} onChange={(e) => setDataSharing(e.target.checked)} />
          Allow anonymized data to help improve MindMate (optional, off by default)
        </label>

        <button className="btn btn-primary mt-24" onClick={handleSave} disabled={saving}>
          {saving ? "Saving…" : "Save Changes"}
        </button>
        {saved && <span className="text-soft" style={{ marginLeft: 12 }}>✓ Saved</span>}
      </div>

      {safetyInfo && (
        <div className="card mt-24" style={{ maxWidth: 560 }}>
          <h3>Safety & Crisis Resources</h3>
          <p className="text-soft" style={{ fontSize: 14 }}>{safetyInfo.disclaimer}</p>
          <div className="crisis-banner mt-16">
            <p style={{ fontSize: 14 }}>
              <strong>{safetyInfo.resources.hotline_name}:</strong> {safetyInfo.resources.hotline_number}<br />
              <strong>Text support:</strong> {safetyInfo.resources.text_line}
            </p>
            <a href={safetyInfo.resources.international_resources_url} target="_blank" rel="noreferrer">
              Find international crisis resources →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
