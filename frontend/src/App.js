import { useEffect, useState } from "react";
import Map3D from "./Map3D";
import { fetchBuildings, runQuery } from "./api";
import "./App.css";

const PRESET_QUERIES = [
  { label: "Highest building", query: "highlight the highest building" },
  { label: "Tallest 3", query: "highlight the tallest 3 buildings" },
  { label: "Over $1M", query: "highlight buildings over $1000000" },
  { label: "Commercial only", query: "highlight commercial buildings" },
  { label: "Cheapest building", query: "highlight the cheapest building" },
];

function App() {
  const [buildings, setBuildings] = useState([]);
  const [filteredIds, setFilteredIds] = useState([]);
  const [selected, setSelected] = useState(null);
  const [loadingQuery, setLoadingQuery] = useState(false);

  const [loadingBuildings, setLoadingBuildings] = useState(true);
  const [lastFilter, setLastFilter] = useState(null);
  const [showDebug, setShowDebug] = useState(false);

  const totalCount = buildings.length;
  const highlightedCount = filteredIds.length;

  // Load buildings at startup
  useEffect(() => {
    async function load() {
      try {
        setLoadingBuildings(true);
        const data = await fetchBuildings();
        setBuildings(data);
      } catch (err) {
        console.error("Failed to load buildings", err);
      } finally {
        setLoadingBuildings(false);
      }
    }
    load();
  }, []);

  // Shared runner for both manual + preset queries
  async function runAndApplyQuery(query) {
    if (!query) return;
    setLoadingQuery(true);
    try {
      const { ids, filter } = await runQuery(query);
      setFilteredIds(ids);
      setLastFilter(filter);
      // clear selected building if the new filter doesn't include it
      if (ids.length > 0 && selected && !ids.includes(selected.id)) {
        setSelected(null);
      }
    } catch (err) {
      console.error(err);
      setFilteredIds([]);
      setLastFilter(null);
    } finally {
      setLoadingQuery(false);
    }
  }

  async function handleQuerySubmit(e) {
    e.preventDefault();
    const query = e.target.elements.query.value;
    await runAndApplyQuery(query);
  }

  async function handleRunPreset(query) {
    await runAndApplyQuery(query);
  }

  return (
    <div className="App">
      <header>
        <h1>Calgary 3D City Dashboard</h1>
        <div className="header-subtitle">
          Explore real building footprints, heights, zoning and value with
          natural-language queries.
        </div>
      </header>

      <form className="query-form" onSubmit={handleQuerySubmit}>
        <input
          name="query"
          placeholder='Try: "highlight the highest building" or "highlight buildings over $1000000"'
        />
        <button type="submit" disabled={loadingBuildings}>
          {loadingQuery ? "Running…" : "Run query"}
        </button>
      </form>

      {/* Preset queries row */}
      <div className="preset-queries">
        {PRESET_QUERIES.map((p) => (
          <button
            key={p.label}
            type="button"
            className="preset-button"
            onClick={() => handleRunPreset(p.query)}
            disabled={loadingBuildings || loadingQuery}
          >
            {p.label}
          </button>
        ))}
      </div>

      <div className="stats-bar">
        <span className="stats-pill">
          Total buildings: <b>{totalCount || "…"}</b>
        </span>

        <span className="stats-pill">
          Highlighted: <b>{highlightedCount}</b>
        </span>

        {selected && (
          <span className="stats-pill">
            Selected: <b>{selected.name || selected.id}</b>
          </span>
        )}

        {highlightedCount > 0 && (
          <button
            type="button"
            className="reset-button"
            onClick={() => {
              setFilteredIds([]);
              setLastFilter(null);
              setSelected(null);
            }}
          >
            Reset highlights
          </button>
        )}
      </div>


      {/* Debug toggle + panel */}
      <div className="debug-toggle-row">
        <button
          type="button"
          className="debug-toggle"
          onClick={() => setShowDebug((v) => !v)}
        >
          {showDebug ? "Hide debug" : "Show debug"}
        </button>
      </div>

      {showDebug && (
        <div className="debug-panel">
          <h3>Debug · Parsed filter</h3>
          {lastFilter ? (
            <pre>{JSON.stringify(lastFilter, null, 2)}</pre>
          ) : (
            <p>No parsed filter yet, or query could not be interpreted.</p>
          )}
        </div>
      )}

      <div className="layout">
        <div className="map-column">
          {loadingBuildings ? (
            <div className="map-loading-box">
              <div className="spinner" />
              <div>Loading buildings…</div>
            </div>
          ) : (
            <Map3D
              buildings={buildings}
              filteredIds={filteredIds}
              selectedBuilding={selected}
              onSelectBuilding={setSelected}
            />
          )}
        </div>

        <div className="info-column">
          <h2>Building info</h2>
          <div className="info-card">
            {selected ? (
              <>
                {selected.name && (
                  <p>
                    <b>Name:</b> {selected.name}
                  </p>
                )}
                <p>
                  <b>ID:</b> {selected.id}
                </p>
                <p>
                  <b>Height:</b> {selected.height} m
                </p>
                <p>
                  <b>Zoning:</b> {selected.zoning}
                </p>
                {selected.type && (
                  <p>
                    <b>Type:</b> {selected.type}
                  </p>
                )}
                <p>
                  <b>Assessed value:</b> ${selected.value}
                </p>
              </>
            ) : (
              <p className="info-placeholder">
                Click a building in the 3D view to see its details here.
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
