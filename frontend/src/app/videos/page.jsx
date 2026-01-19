"use client";
import { useEffect, useState } from "react";
import { api } from "../../lib/api";

export default function VideosPage() {
  const [items, setItems] = useState([]);
  const [err, setErr] = useState("");

  useEffect(() => {
    api.videos()
      .then(d => setItems(d.items || []))
      .catch(e => { setErr(e.message); window.location.href="/login"; });
  }, []);

  return (
    <div>
      <h2>My Videos</h2>
      <a href="/create">← Back to Create</a>
      {err && <div style={{ color: "#b00" }}>{err}</div>}
      <div style={{ marginTop: 12 }}>
        {items.map(v => (
          <div key={v.job_id} style={{ padding: 12, border: "1px solid #eee", marginBottom: 10 }}>
            <div><b>{v.job_id}</b></div>
            <div>Status: {v.status}</div>
            {v.output_url && (
              <div style={{ marginTop: 8 }}>
                <a href={`http://localhost:8000${v.output_url}`} target="_blank">Open video</a>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
