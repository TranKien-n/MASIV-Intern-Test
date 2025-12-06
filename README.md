# MASIV Internship Technical Assessment – 3D Calgary City Dashboard

## Author
| Name | GitHub | Email |
|------|--------|--------|
| **Kien Tran** | `TranKien-n` | trankien421@gmail.com |

---

## Project Description

This project implements an interactive **3D building visualization dashboard** for a section of downtown Calgary.

A Flask backend loads real-world building footprints and attributes from OpenStreetMap (OSM) (via cached Overpass-derived data), while a React + Three.js frontend renders the city in 3D with smooth navigation, building selection, and natural-language search.

A built-in natural-language query engine enables users to type queries such as:
  -“highlight buildings over $1,000,000”
  -“tallest 3 buildings”
  -“second tallest building”
  -“commercial zoning”
  -“buildings between 30 and 60 meters”
The backend interprets these queries (using a hybrid LLM + rule-based approach) and returns matched building IDs for highlighting in the 3D view.

---

## Key Features

### 1. Real OSM Building Data Integration
- Building footprints retrieved via the Overpass API
- Offline caching using `buildings_cache.json` for reliability
- Normalization of height, zoning, value, and type attributes

### 2. 3D Visualization (React + Three.js)
- Extruded buildings based on footprint geometry and height  
- Ambient/directional lighting for depth clarity  
- Smooth camera transitions:  
  - Auto-focus on clicked buildings  
  - Auto-focus when exactly one building matches a query  
  - Reset view when clearing highlights  
- Interaction features:  
  - Hover tooltip with building metadata  
  - Click-to-select information panel  
  - Dynamic highlighting of filtered buildings
  

### 3. Natural-Language Query Engine (Hybrid LLM + Rule-Based)
The backend uses a **hybrid query interpretation pipeline**:

#### 🔹 Hugging Face LLM Integration (implemented)

The backend attempts to parse the user query using a free-tier model from the **Hugging Face Inference API**, configured via environment variables:
  - HF_API_KEY
  - HF_MODEL_ID
- The LLM is instructed to output JSON in this exact schema:
```json
{
  "attribute": "height" | "value" | "zoning" | "type",
  "operator": ">" | "<" | "=" | "BETWEEN" | "TOP" | "BOTTOM",
  "value": number | string | [number, number]
}
```
If the model returns valid JSON, the backend uses it directly.

If the LLM request fails (e.g., free-tier model unavailable), the backend logs:
```bash
[HF_LLM] Error calling Hugging Face: ...
```
and switches to the rule-based interpreter.

#### 🔹 Rule-Based Interpreter (Guaranteed Fallback)
Converts plain English text into structured filters
- Supports:
  - Numeric comparisons (`>`, `<`)
  - Ranges (`between X and Y`)
  - Ranking (`tallest`, `cheapest`, `top 3`)
  - Zoning and type-based filters
  - Value-based queries using currency expressions
- Returns building IDs + parsed filter JSON for debugging

Together, this ensures consistent behavior and complete reliability, even when the LLM cannot be reached.

### 4. User Interface Enhancements
- Preset query buttons for quick demo interaction
- "Reset Highlights" button
- Hover tooltip for quick inspection
- Click-to-select details sidebar
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
 Extruded Buildings                    LLM Integration (HuggingFace API)
 Highlight Rendering                   Filter Engine (TOP, >, <, BETWEEN)
 Camera Controls                       OSM Data Loader + Cache
```

---

## Setup Instructions

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # For Windows: .\venv\Scripts\Activate.ps1
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
| OSM Data Loader | See `data_loader.py` |
| Natural-Language Engine | `llm.py` |
| Filter Logic | `filters.py` |
| 3D Rendering | `Map3D.js` |

---

## Example Queries

| Query | Interpretation |
|-------|----------------|
| "tallest building" | TOP 1 by height |
| "tallest 3 buildings" | TOP 3 by height |
| "over $1,000,000" | `value > 1,000,000` |
| "commercial buildings" | zoning/type = commercial |
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

This project can be deployed using any free hosting service. The sites that were used for this assessment are noted below.

**Frontend**
- Vercel  

**Backend**
- Render.com

Both backend and frontend have been deployed successfully.

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

- More capable HuggingFace model
- Additional UI polish

---

## License

This project is submitted as part of the MASIV Internship Technical Assessment and is intended solely for evaluation.

