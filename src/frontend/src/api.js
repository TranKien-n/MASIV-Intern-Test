// Small API helper module for talking to the Flask backend.

const API_BASE =
  process.env.REACT_APP_API_BASE || "http://127.0.0.1:5000";

/**
 * Fetch the full building list from the backend.
 *
 * @returns {Promise<Array>} list of building objects
 */
export async function fetchBuildings() {
  const res = await fetch(`${API_BASE}/api/buildings`);
  if (!res.ok) {
    throw new Error("Failed to fetch buildings");
  }
  return res.json();
}

/**
 * Run a natural-language query against the backend.
 *
 * @param {string} query - user input text
 * @returns {Promise<{ids: string[], filter: object|null}>}
 */
export async function runQuery(query) {
  const res = await fetch(`${API_BASE}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    throw new Error("Failed to run query");
  }

  // Backend contract: { ids: [...], filter: {...} | null }
  return res.json();
}
