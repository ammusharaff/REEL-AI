"use client";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export default function CreatePage() {
  const [text, setText] = useState("Say something powerful in Indian English for a short reel.");
  const [jobId, setJobId] = useState("");
  const [status, setStatus] = useState("");
  const [outputUrl, setOutputUrl] = useState("");
  const [credits, setCredits] = useState(null);

  useEffect(() => {
    api.me().then(d => setCredits(d.credits)).catch(() => (window.location.href = "/login"));
  }, []);

  <select onChange={(e)=>setStyle(e.target.value)}>
    <option value="bold">Bold White</option>
    <option value="yellow">Yellow Meme</option>
  </select>


  async function generate() {
    setStatus("Submitting...");
    setOutputUrl("");
    try {
      const res = await api.generate(text);
      setJobId(res.job_id);
      setCredits(res.credits_left);
      setStatus("Queued. Processing...");
    } catch (e) {
      setStatus(e.message);
    }
  }

  async function poll(job) {
    const j = await api.job(job);
    setStatus(j.status);
    if (j.status === "succeeded") {
      setOutputUrl(`http://localhost:8000${j.output_url}`);
      return true;
    }
    if (j.status === "failed") {
      setStatus(j.error || "failed");
      return true;
    }
    return false;
  }

  useEffect(() => {
    if (!jobId) return;
    let stop = false;
    const timer = setInterval(async () => {
      if (stop) return;
      try {
        const done = await poll(jobId);
        if (done) {
          stop = true;
          clearInterval(timer);
        }
      } catch {}
    }, 2000);

    return () => clearInterval(timer);
  }, [jobId]);

  return (
    <div style={{ maxWidth: 720 }}>
      <h2>Create Video</h2>
      <div style={{ marginBottom: 8 }}>Credits: <b>{credits ?? "..."}</b></div>

      <textarea value={text} onChange={(e) => setText(e.target.value)}
        rows={6} style={{ width: "100%", padding: 10 }} />

      <div style={{ marginTop: 10 }}>
        <button onClick={generate} style={{ padding: 10 }}>Generate Reel</button>
        <a href="/videos" style={{ marginLeft: 12 }}>My Videos</a>
      </div>

      <div style={{ marginTop: 12 }}>Status: <b>{status}</b></div>

      {outputUrl && (
        <div style={{ marginTop: 14 }}>
          <video src={outputUrl} controls style={{ width: 360, border: "1px solid #ddd" }} />
          <div>
            <a href={outputUrl} download style={{ display: "inline-block", marginTop: 10 }}>
              Download MP4
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
