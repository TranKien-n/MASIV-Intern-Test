const BASE_URL = "http://127.0.0.1:5000";

export async function fetchBuildings() {
  const res = await fetch(`${BASE_URL}/api/buildings`);
  if (!res.ok) {
    throw new Error(`Failed to fetch buildings: ${res.status}`);
  }
  const data = await res.json();
  console.log("Fetched buildings:", data.length);
  return data;
}

export async function runQuery(query) {
  const res = await fetch(`${BASE_URL}/api/query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });

  if (!res.ok) {
    console.error("Query request failed with status", res.status);
    return { ids: [], filter: null };
  }

  const data = await res.json();
  console.log("Query response raw:", data);

  // Accept either an array OR { ids, filter }
  const ids = Array.isArray(data) ? data : (data.ids || []);
  const filter = Array.isArray(data) ? null : (data.filter || null);

  console.log("Highlighting IDs:", ids);
  return { ids, filter };
}
