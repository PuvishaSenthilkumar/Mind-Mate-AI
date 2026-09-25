import { createContext, useContext, useState, useEffect } from "react";
import api from "../api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("mindmate_user");
    return stored ? JSON.parse(stored) : null;
  });
  const [loading, setLoading] = useState(true);
  const [pendingEmail, setPendingEmail] = useState(() => localStorage.getItem("mindmate_pending_email") || null);
  const [pendingPhone, setPendingPhone] = useState(() => localStorage.getItem("mindmate_pending_phone") || null);

  useEffect(() => {
    const token = localStorage.getItem("mindmate_token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .get("/auth/me")
      .then((res) => {
        setUser(res.data);
        localStorage.setItem("mindmate_user", JSON.stringify(res.data));
      })
      .catch(() => {
        localStorage.removeItem("mindmate_token");
        localStorage.removeItem("mindmate_user");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  const login = async (email, password) => {
    const res = await api.post("/auth/login", { email, password });
    localStorage.setItem("mindmate_token", res.data.access_token);
    localStorage.setItem("mindmate_user", JSON.stringify(res.data.user));
    setUser(res.data.user);
    setPendingEmail(null);
    setPendingPhone(null);
    localStorage.removeItem("mindmate_pending_email");
    localStorage.removeItem("mindmate_pending_phone");
    return res.data.user;
  };

  const register = async (full_name, email, password, phone_number) => {
    const payload = { full_name, email, password };
    if (phone_number) payload.phone_number = phone_number;
    const res = await api.post("/auth/register", payload);
    setPendingEmail(email);
    localStorage.setItem("mindmate_pending_email", email);
    if (phone_number) {
      setPendingPhone(phone_number);
      localStorage.setItem("mindmate_pending_phone", phone_number);
    }
    return res.data;
  };

  const verifyOtp = async (email, otp_code, phone_number, method) => {
    const payload = { otp_code, method: method || "email" };
    if (method === "phone" && phone_number) {
      payload.phone_number = phone_number;
    } else if (email) {
      payload.email = email;
    }
    const res = await api.post("/auth/verify-otp", payload);
    localStorage.setItem("mindmate_token", res.data.access_token);
    localStorage.setItem("mindmate_user", JSON.stringify(res.data.user));
    setUser(res.data.user);
    setPendingEmail(null);
    setPendingPhone(null);
    localStorage.removeItem("mindmate_pending_email");
    localStorage.removeItem("mindmate_pending_phone");
    return res.data.user;
  };

  const requestOtp = async (email, phone_number, method) => {
    const payload = { method: method || "email" };
    if (method === "phone" && phone_number) {
      payload.phone_number = phone_number;
    } else if (email) {
      payload.email = email;
    }
    const res = await api.post("/auth/request-otp", payload);
    return res.data;
  };

  const logout = () => {
    localStorage.removeItem("mindmate_token");
    localStorage.removeItem("mindmate_user");
    localStorage.removeItem("mindmate_pending_email");
    localStorage.removeItem("mindmate_pending_phone");
    setUser(null);
    setPendingEmail(null);
    setPendingPhone(null);
  };

  const updateUser = (updated) => {
    setUser(updated);
    localStorage.setItem("mindmate_user", JSON.stringify(updated));
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, verifyOtp, requestOtp, logout, updateUser, pendingEmail, setPendingEmail, pendingPhone, setPendingPhone }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
