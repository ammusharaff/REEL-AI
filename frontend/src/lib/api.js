const API_BASE = "http://localhost:8000";

export function setToken(t) {
  localStorage.setItem("token", t);
}

export function getToken() {
  return localStorage.getItem("token");
}

async function request(path, { method = "GET", body, timeoutMs = 10000 } = {}) {
  const token = getToken();
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {})
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: controller.signal
    });
  } catch (err) {
    if (err && err.name === "AbortError") {
      throw new Error("Request timed out. Is the backend running?");
    }
    throw new Error("Request failed. Is the backend running?");
  } finally {
    clearTimeout(timer);
  }

  const contentType = res.headers.get("content-type") || "";
  const data = contentType.includes("application/json")
    ? await res.json().catch(() => ({}))
    : { detail: await res.text().catch(() => "") };

  if (!res.ok) {
    let detail = data.detail || "Request failed";
    if (Array.isArray(detail)) {
      detail = detail.map((d) => d?.msg || d?.message || "Invalid input").join(", ");
    }
    throw new Error(detail);
  }
  return data;
}

export const api = {
  signup: (email, password) => request("/auth/signup", { method: "POST", body: { email, password } }),
  login: (email, password) => request("/auth/login", { method: "POST", body: { email, password } }),
  me: () => request("/me"),
  generate: (text) => request("/generate-video", { method: "POST", body: { text } }),
  job: (jobId) => request(`/jobs/${jobId}`),
  videos: () => request("/videos")
};
