"use client";
import { useState } from "react";
import { api, setToken } from "../../lib/api";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [pw, setPw] = useState("");
  const [msg, setMsg] = useState("");
  const [busy, setBusy] = useState(false);

  async function doLogin(mode) {
    if (busy) return;
    if (!email || !pw) {
      setMsg("Email and password are required.");
      return;
    }
    setBusy(true);
    setMsg("...");
    try {
      const data = mode === "signup"
        ? await api.signup(email, pw)
        : await api.login(email, pw);

      setToken(data.token);
      window.location.href = "/create";
    } catch (e) {
      setMsg(e?.message || "Request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div style={{ maxWidth: 420 }} suppressHydrationWarning>
      <h2>Login / Signup</h2>
      <input
        placeholder="Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        style={{ width: "100%", padding: 10, marginBottom: 8 }}
        suppressHydrationWarning
        autoComplete="off"
      />
      <input
        placeholder="Password"
        type="password"
        value={pw}
        onChange={(e) => setPw(e.target.value)}
        style={{ width: "100%", padding: 10, marginBottom: 12 }}
        suppressHydrationWarning
        autoComplete="off"
      />

      <button
        type="button"
        onClick={() => doLogin("login")}
        style={{ padding: 10, marginRight: 8 }}
        disabled={busy}
        suppressHydrationWarning
      >
        {busy ? "..." : "Login"}
      </button>
      <button
        type="button"
        onClick={() => doLogin("signup")}
        style={{ padding: 10 }}
        disabled={busy}
        suppressHydrationWarning
      >
        {busy ? "..." : "Signup"}
      </button>

      <div style={{ marginTop: 12, color: "#b00" }}>{msg}</div>
    </div>
  );
}
