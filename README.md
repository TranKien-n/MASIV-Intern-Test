# MASIV Internship Technical Assessment – 3D Calgary City Dashboard

## Author
| Name | GitHub | Email |
|------|--------|--------|
| **Kien Tran** | `TranKien-n` | trankien421@gmail.com |

---

## Project Description

This project implements an interactive **3D building visualization dashboard** for a region of downtown Calgary.

The system retrieves real building footprints and attributes from **OpenStreetMap (OSM)** using the Overpass API, processes them in a **Flask backend**, and visualizes them through a **Three.js** rendering engine housed inside a React frontend.

A natural-language query interface enables users to perform operations such as:

- "highlight buildings over $1,000,000"
- "tallest 3 buildings"
- "commercial buildings"
- "buildings between 30 and 60 meters"

Queries are parsed into structured filter objects by the backend and then used to highlight buildings in the 3D scene.

---

## Key Features

### 1. Real OSM Building Data Integration
- Building footprints retrieved via the Overpass API
- Offline caching using `buildings_cache.json` for reliability
- Normalization of height, zoning, value, and type attributes

### 2. 3D Visualization (Three.js + React)
- Buildings extruded based on footprint geometry and height
- Clean lighting and shading for improved readability
- Smooth camera transitions:
  - Focus on clicked buildings  
  - Focus on single-result queries  
  - Reset camera view when clearing highlights
- Hover tooltips for instant building information
- Click-to-select building details panel
- Highlighting of query results

### 3. Natural-Language Query Engine
- Converts plain English text into structured filters
- Supports:
  - Numeric comparisons (`>`, `<`)
  - Ranges (`between X and Y`)
  - Ranking (`tallest`, `cheapest`, `top 3`)
  - Zoning and type-based filters
  - Value-based queries using currency expressions
- Returns building IDs + parsed filter JSON for debugging

### 4. User Interface Enhancements
- Preset query buttons for quick demo interaction
- "Reset Highlights" functionality
- Debug panel showing parsed filter objects
- Responsive UI design suitable for desktop usage

---

## Architecture Overview

```
frontend (React) ----------------------> backend (Flask)
     |                                        |
     |   GET /api/buildings                   |
     |   POST /api/query                      |
     |                                        |
 Three.js Scene                        Query Interpreter
 Extruded Buildings                    Natural-Language Parsing
 Highlight Rendering                   Filter Engine (TOP, >, <, BETWEEN)
 Camera Controls                       OSM Data Loader + Cache
```

---

## Setup Instructions

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Backend will start on:

```
http://localhost:5000
```

---

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend will start on:

```
http://localhost:3000
```

---

## Documentation

| Resource | Link |
|---------|------|
| Class UML Diagram | [View Class UML](https://github.com/TranKien-n/MASIV-Intern-Test/blob/main/uml/ClassDiagram.png) |
| Sequence UML Diagram | [View Sequence UML](https://github.com/TranKien-n/MASIV-Intern-Test/blob/main/uml/SequenceDiagram.png) |
| Backend API | `/api/buildings`, `/api/query` |
| OSM Query Definition | See `data_loader.py` |
| Natural-Language Engine | `llm.py` |
| Filter Logic | `filters.py` |
| 3D Rendering Logic | `Map3D.js` |

---

## Example Queries

| Query | Interpretation |
|-------|----------------|
| "tallest building" | TOP 1 by height |
| "tallest 3 buildings" | TOP 3 by height |
| "over $1,000,000" | `value > 1,000,000` |
| "commercial buildings" | zoning/type match |
| "between 30 and 50 meters" | height range |
| "reset" | clear all highlights |

---

## Project Structure

```
src/
  backend/
    app.py
    data_loader.py
    filters.py
    llm.py
    buildings_cache.json
    requirements.txt
  frontend/
    src/
      App.js
      Map3D.js
      api.js
      App.css
    ...
uml/
  ClassDiagram.png
  SequenceDiagram.png
README.md
```

---

## Deployment

This project can be deployed using any free hosting service:

**Frontend**
- Vercel  
- Netlify  

**Backend**
- Render.com  
- Railway.app  

---

## Status

Core requirements implemented:

- Real OSM data ingestion  
- 3D building visualization  
- Natural language query interpretation  
- Highlighting and building selection  
- Smoothed camera transitions  
- Full UI integration  

Optional revisions that can be added:

- Full HuggingFace LLM integration  
- UML diagram export  
- Cloud deployment instructions  

---

## License

This project is submitted as part of the MASIV Internship Technical Assessment and is intended solely for evaluation.

