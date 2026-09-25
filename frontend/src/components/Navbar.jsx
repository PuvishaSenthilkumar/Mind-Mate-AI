import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: "🏠" },
  { to: "/chat", label: "AI Chat", icon: "💬" },
  { to: "/mood", label: "Mood Tracker", icon: "🌤️" },
  { to: "/journal", label: "Journal", icon: "📔" },
  { to: "/habits", label: "Habits", icon: "✅" },
  { to: "/activities", label: "Wellness", icon: "🧘" },
  { to: "/profile", label: "Profile", icon: "⚙️" },
];

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  return (
    <nav
      style={{
        width: 230,
        background: "var(--neu-surface)",
        borderRight: "none",
        padding: "24px 16px",
        display: "flex",
        flexDirection: "column",
        boxShadow: "4px 0 16px rgba(163, 177, 198, 0.25)",
      }}
    >
      <div style={{ padding: "0 8px 24px 8px", display: "flex", alignItems: "center", gap: 12 }}>
        <img src="/image1.png" alt="MindMate AI" style={{ width: 32, height: 32, objectFit: "contain" }} />
        <h2 style={{ color: "var(--neu-primary-dark)", fontSize: 20, fontWeight: 700, margin: 0 }}>MindMate AI</h2>
        <div className="text-soft" style={{ fontSize: 12 }}>Hi, {user?.full_name?.split(" ")[0]}</div>
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1 }}>
        <button className="theme-toggle" onClick={toggleTheme} style={{ marginBottom: 8 }}>
          {theme === "dark" ? "☀️ Light" : "🌙 Dark"}
        </button>
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            style={({ isActive }) => ({
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "12px 14px",
              borderRadius: "var(--radius-sm)",
              color: isActive ? "var(--neu-primary-dark)" : "var(--neu-text)",
              background: isActive ? "var(--neu-surface)" : "transparent",
              fontWeight: isActive ? 600 : 500,
              fontSize: 14.5,
              boxShadow: isActive ? "var(--neu-shadow-pressed)" : "none",
              transition: "all 0.2s ease",
            })}
          >
            <span>{l.icon}</span> {l.label}
          </NavLink>
        ))}
      </div>
      <button
        className="btn btn-secondary btn-block"
        onClick={() => {
          logout();
          navigate("/login");
        }}
      >
        Log out
      </button>
    </nav>
  );
}
