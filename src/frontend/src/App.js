/**
 * Top-level React application component.
 *
 * Responsibilities:
 *  - Load building data from the backend
 *  - Handle natural-language queries and preset queries
 *  - Track currently highlighted and selected buildings
 *  - Render MASIV-style layout, map, info panel, and debug panel
 */

import { useEffect, useState } from "react";
import Map3D from "./Map3D";
import { fetchBuildings, runQuery } from "./api";
import "./App.css";

const PRESET_QUERIES = [
  { label: "Tallest building", query: "highlight the tallest building" },
  { label: "Tallest 3", query: "highlight the tallest 3 buildings" },
  { label: "Over $1M", query: "highlight buildings over $1000000" },
  { label: "Commercial", query: "highlight commercial buildings" },
  { label: "Cheapest building", query: "highlight the cheapest building" },
];

function App() {
  // Raw building data from backend
  const [buildings, setBuildings] = useState([]);
  // IDs currently highlighted by a query
  const [filteredIds, setFilteredIds] = useState([]);
  // Currently selected building (clicked in 3D view)
  const [selected, setSelected] = useState(null);

  // Loading flags
  const [loadingQuery, setLoadingQuery] = useState(false);
  const [loadingBuildings, setLoadingBuildings] = useState(true);

  // Last parsed filter (for debug panel)
  const [lastFilter, setLastFilter] = useState(null);
  const [showDebug, setShowDebug] = useState(false);

  const totalCount = buildings.length;
  const highlightedCount = filteredIds.length;

  // ----------------------------------------------------
  // Load buildings from backend on initial mount
  // ----------------------------------------------------
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

  // ----------------------------------------------------
  // Query helpers
  // ----------------------------------------------------

  /**
   * Run a query against the backend and update highlight state.
   */
  async function runAndApplyQuery(query) {
    if (!query) return;
    setLoadingQuery(true);

    try {
      const { ids, filter } = await runQuery(query);
      setFilteredIds(ids);
      setLastFilter(filter);

      // If the previously selected building is no longer highlighted,
      // we clear the selection to avoid showing stale info.
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

  function handleResetHighlights() {
    setFilteredIds([]);
    setLastFilter(null);
    setSelected(null);
  }

  // ----------------------------------------------------
  // Render
  // ----------------------------------------------------
  return (
    <div className="App">
      {/* MASIV-style header */}
      <header className="ms-header">
        <div className="ms-nav">
          <div className="ms-logo">MERCEDES + SINGH</div>
        </div>

        <div className="ms-hero">
          <div className="ms-hero-grid" />
          <div className="ms-hero-content">
            <h1>CALGARY 3D CITY</h1>
            <p>
              Data-driven, design-led visualization of Calgary&apos;s built
              form.
            </p>
          </div>
        </div>
      </header>

      <main className="ms-main">
        <section className="ms-content">
          <div className="ms-intro">
            <h2>3D City Dashboard</h2>
            <p>
              This prototype maps real Calgary buildings in three dimensions and
              lets you query them using natural language. Type a question, or
              use one of the preset queries below, to highlight buildings by
              height, value, or zoning.
            </p>
          </div>

          {/* Query input */}
          <form className="query-form" onSubmit={handleQuerySubmit}>
            <input
              name="query"
              placeholder='Try: "highlight the tallest building" or "highlight buildings over $1000000"'
            />
            <button type="submit" disabled={loadingBuildings}>
              {loadingQuery ? "Running…" : "Run query"}
            </button>
          </form>

          {/* Preset query shortcuts */}
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

          {/* Simple stats + reset */}
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
                onClick={handleResetHighlights}
              >
                Reset highlights
              </button>
            )}
          </div>

          {/* Debug panel toggle */}
          <div className="debug-toggle-row">
            <button
              type="button"
              className="debug-toggle"
              onClick={() => setShowDebug((v) => !v)}
            >
              {showDebug ? "Hide debug" : "Show debug"}
            </button>
          </div>

          {/* Parsed filter debug view */}
          {showDebug && (
            <div className="debug-panel">
              <h3>Parsed filter</h3>
              {lastFilter ? (
                <pre>{JSON.stringify(lastFilter, null, 2)}</pre>
              ) : (
                <p>No parsed filter yet, or query could not be interpreted.</p>
              )}
            </div>
          )}

          {/* Main layout: map + info panel */}
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
              <h2>Building details</h2>
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
        </section>
      </main>

      <footer className="ms-footer">
        <div className="ms-footer-inner">
          <div className="ms-footer-column">
            <div className="ms-footer-title">Mercedes and Singh</div>
            <div className="ms-footer-text">Calgary, Alberta</div>
          </div>
          <div className="ms-footer-column">
            <div className="ms-footer-title">MASIV Group</div>
            <div className="ms-footer-text">H.O.M.E AI</div>
            <div className="ms-footer-text">MASIVX</div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
