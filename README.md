Calgary 3D City Dashboard

A fully interactive 3D urban analytics dashboard built with:

React + Three.js for the 3D map

Flask backend for data + natural language interpretation

OSM Overpass API for real-world building footprints

Custom NL Interpreter that turns English into filters

Automated highlighting, smooth camera transitions, and tooltips

This project allows users to explore real Calgary buildings and run natural-language queries like:

“highlight buildings over $1,000,000”
“show the tallest 3 buildings”
“highlight commercial buildings”
“cheapest building”

🚀 Features
🗺 Interactive 3D Map

Real Calgary building footprints from OpenStreetMap

Extruded 3D forms with realistic height scaling

OrbitControls (pan, zoom, rotate)

Smooth camera transitions (to selected building or one-result queries)

Hover tooltips with building name + height

Click buildings to view details

💬 Natural-Language Building Queries

Powered by a custom interpreter (llm.py):

✔ “highlight buildings over $1000000”
✔ “highlight the highest building”
✔ “tallest 3 buildings”
✔ “buildings between 30 and 60 meters”
✔ “commercial buildings” / “residential”
✔ “zoning C-COR”

Your query transforms into a filter dict:

{
  "attribute": "height",
  "operator": "TOP",
  "value": 3
}


Used by backend filters.py to select buildings.

🧭 Camera Intelligence

Smooth ease into:

clicked buildings

queries that return exactly 1 result

No movement for multi-result queries (good UX)

Auto-reset when nothing is selected

🎨 Polished UI

Gradient background

Rounded cards, subtle shadows

Preset query buttons

Debug panel toggle

Reset Highlights button

Responsive layout

🗂 Backend Resilience

OSM Overpass fetch with fallback caching

If Overpass is down (504/429), app still runs using buildings_cache.json

Consistent building schema:

id

name

footprint

height

value

zoning

type

🛠 Getting Started
Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py

Frontend
cd frontend
npm install
npm start


Then open:
👉 http://localhost:3000

📝 Example Queries
Query	Meaning
“highlight the tallest 3 buildings”	TOP 3 heights
“highlight buildings over $800000”	value > 800k
“highlight commercial buildings”	zoning/type filter
“between 30 and 50 meters”	height range
“reset”	Clear highlights
🤝 Credits

OSM Overpass data

Three.js for 3D rendering

React + Flask

Custom NL-to-filter interpreter

📌 Notes for Evaluators

This project demonstrates:

Data ingestion + cleaning from third-party APIs

Natural language interpretation

Backend business logic

Frontend visualization + 3D rendering

Interactive UX design

Robust error handling & caching

Clean architecture

All pieces work together to provide an intuitive, interactive, and insightful 3D urban data explorer.