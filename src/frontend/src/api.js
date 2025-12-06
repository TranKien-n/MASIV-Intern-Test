// src/api.js
const API_BASE =
  process.env.REACT_APP_API_BASE || "http://127.0.0.1:5000";

export async function fetchBuildings() {
  const res = await fetch(`${API_BASE}/api/buildings`);
  if (!res.ok) throw new Error("Failed to fetch buildings");
  return res.json();
}

export async function runQuery(query) {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
  if (!res.ok) throw new Error("Failed to run query");
  // assuming backend returns { ids: [...], filter: {...} }
  return res.json();
}
