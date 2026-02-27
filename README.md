# EnerScopeAI ☀️💨
**Multi-Renewable Energy Decision Intelligence Platform**

> **Evolution of HelioScopeAI:** From solar-only feasibility to multi-renewable decision intelligence with confidence scoring, GO/CAUTION/NO-GO recommendations, and risk awareness.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat&logo=react)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat&logo=postgresql)](https://postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 What is EnerScopeAI?

EnerScopeAI transforms renewable energy site selection from **"how much energy?"** to **"which renewable source should I choose, and how confident should I be?"**

### Key Innovation: Decision-First, Not Simulation-First

EnerScopeAI compares **solar and wind energy** for any location, providing:
- 🔄 **Multi-Renewable Comparison** — Side-by-side solar vs. wind analysis
- 🎯 **Decision Confidence Index** — 0-100% confidence score with explainability
- 🚦 **GO/CAUTION/NO-GO Recommendations** — Clear decision framework
- ⚠️ **Risk Awareness Layer** — Transparent risk identification by category
- 🏆 **Ranked Options** — Best renewable source with reasoning
- 🤖 **Decision-Focused AI** — Plain-language guidance on what to do next
- 🔀 **Hybrid Assessment** — Evaluates solar+wind hybrid potential

### 🆕 What's New in EnerScopeAI v1.0?

| Feature | HelioScopeAI (v0) | EnerScopeAI (v1.0) |
|---------|-------------------|---------------------|
| Energy Sources | ☀️ Solar only | ☀️ Solar + 💨 Wind comparison |
| Output Focus | Suitability score | **Decision Confidence + Recommendation** |
| Recommendations | A-F grades | **GO / CAUTION / NO-GO** |
| Risk Awareness | Implicit | **Explicit risk analysis by category** |
| Comparison | N/A | **Ranked renewable options** |
| AI Summary | Site description | **Decision-focused guidance** |
| User Question | "Is solar viable?" | **"Solar or wind? How confident?"** |

---

## ⚡ Quick Start

### Test the New Multi-Renewable Endpoint

```bash
curl -X POST http://localhost:8000/api/enerscopeai/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "lat": 26.92,
    "lng": 70.90,
    "plant_size_kw": 10,
    "electricity_rate": 8.0,
    "include_solar": true,
    "include_wind": true
  }'
```

**Response includes:**
- Solar suitability score + confidence + GO/CAUTION/NO-GO + risk analysis
- Wind suitability score + confidence + GO/CAUTION/NO-GO + risk analysis
- Best renewable option (ranked)
- Overall decision confidence index (0-100%)
- AI decision summary in plain language

📖 **Full Quick Start:** See [QUICKSTART.md](QUICKSTART.md)  
📚 **Complete Documentation:** See [ENERSCOPEAI.md](ENERSCOPEAI.md)

---

## 🏗️ EnerScopeAI Architecture

```
User → React Frontend → FastAPI Backend
                            ↓
        ┌──────────────────────────────────────┐
        │   Multi-Renewable Analysis Engine    │
        ├──────────────────────────────────────┤
        │  ☀️ Solar Suitability (v3)          │
        │  💨 Wind Suitability (v1)           │
        │  🎯 Decision Confidence Calculator   │
        │  🚦 GO/CAUTION/NO-GO Engine         │
        │  ⚠️  Risk Analyzer                   │
        │  🔄 Comparison & Ranking Engine      │
        │  🤖 Decision-Focused AI (Gemini)    │
        └──────────────────────────────────────┘
                            ↓
        → Ranked renewable options with confidence
        → Risk-aware recommendations
        → Plain-language decision guidance
```

---

## 🎯 Philosophy: Decision Intelligence

### Traditional Tools vs. EnerScopeAI

**Traditional Renewable Tools:**
- ❌ Simulate energy output with high precision
- ❌ Require expert knowledge to interpret
- ❌ Focus on "how much?" not "which?"
- ❌ Don't acknowledge uncertainty

**EnerScopeAI Approach:**
- ✅ Help non-experts confidently DECIDE
- ✅ Compare multiple renewable sources
- ✅ Quantify and explain confidence
- ✅ Transparent about uncertainty and risk
- ✅ Provide actionable next steps

### Target Users

- 🏠 **Homeowners** — "Should I install solar or wind?"
- 💼 **Small Investors** — "Which renewable source is best for my budget?"
- 🎓 **Students** — "Learn about renewable decision-making"
- 📊 **Planners** — "Pre-feasibility screening for projects"

---

## 🚀 Key Features Explained

### 1. Decision Confidence Index (DCI)

**What is it?** A 0-100% score representing how reliable the recommendation is.

**Factors considered:**
- Data quality (completeness, freshness)
- Weather stability (variability, seasonal patterns)
- Score clarity (clearly good vs. borderline)
- Economic viability (ROI certainty)
- Constraint certainty (hard blockers)

**Example:**
- **85% confidence:** "High confidence - proceed with standard due diligence"
- **62% confidence:** "Moderate confidence - professional assessment recommended"
- **43% confidence:** "Low confidence - site-specific measurements required"

### 2. GO/CAUTION/NO-GO Recommendations

**Clear decision framework:**

- 🟢 **GO:** High suitability (≥65) + high confidence (≥60%) + good ROI (≤7 years)
  - *Action: Proceed with detailed planning and quotes*

- 🟡 **CAUTION:** Moderate suitability OR moderate confidence OR marginal ROI
  - *Action: Get professional feasibility study before major investment*

- 🔴 **NO-GO:** Low suitability (<40) OR critical constraints OR poor ROI (>15 years)
  - *Action: Explore alternative locations or energy sources*

### 3. Risk Awareness Layer

**Transparent risk identification in 5 categories:**

1. **Technical/Environmental** — Resource quality, terrain, weather variability
2. **Economic/Financial** — Payback uncertainty, cost sensitivity, price changes
3. **Policy/Regulatory** — Subsidies, permits, net metering changes
4. **Operational/Maintenance** — Component failures, degradation, servicing
5. **Data/Uncertainty** — Measurement gaps, microclimate unknowns

Each risk includes **mitigation suggestions** and identifies **show-stoppers**.

### 4. Multi-Renewable Comparison

**Side-by-side analysis:**
- Solar and wind evaluated independently
- Ranked by composite viability score
- Key strengths and weaknesses identified
- Hybrid system potential assessed

**Composite Viability Formula:**
```
Viability = (
    suitability_score × 0.40 +
    confidence_index × 0.30 +
    economic_score × 0.20 +
    recommendation_bonus × 0.10
)
```

---

## 📊 Example Use Cases

### Case 1: Clear Solar Winner (Rajasthan Desert)

**Input:** Jodhpur, India (26.92°N, 70.90°E), 10 kW system

**Output:**
- ☀️ **Solar:** 92/100, 94% confidence, **GO** recommendation
- 💨 **Wind:** 48/100, 62% confidence, **CAUTION** recommendation
- 🏆 **Best Option:** Solar (clearly superior)
- 🎯 **Overall Confidence:** 88% (Very High)
- 💡 **AI Guidance:** "Proceed with solar — excellent resource and high confidence. Get quotes from 3 installers."

### Case 2: Marginal Site (Urban + High Clouds)

**Input:** Mumbai suburbs, 10 kW system

**Output:**
- ☀️ **Solar:** 56/100, 71% confidence, **CAUTION** recommendation
- 💨 **Wind:** 42/100, 58% confidence, **CAUTION** recommendation
- 🏆 **Best Option:** Solar (marginally better)
- 🎯 **Overall Confidence:** 61% (Moderate)
- 💡 **AI Guidance:** "Solar slightly better, but neither option is strong. Professional feasibility study required before investment."

### Case 3: Poor Site (Dense Urban)

**Input:** Central Delhi, 10 kW system

**Output:**
- ☀️ **Solar:** 34/100, 78% confidence, **NO-GO** recommendation
- 💨 **Wind:** 29/100, 71% confidence, **NO-GO** recommendation
- 🏆 **Best Option:** Neither
- 🎯 **Overall Confidence:** 75% (High - confident it's not viable)
- 💡 **AI Guidance:** "Renewable energy not recommended at this location. Explore alternative sites or grid renewable programs."

---

## 🎓 Educational Value & Hackathon Relevance

### Why EnerScopeAI Stands Out

1. **Novel Approach:** Shifts from simulation to decision intelligence
2. **Practical Impact:** Addresses real user pain point ("which renewable?")
3. **Honest About Limitations:** Conservative, transparent about uncertainty
4. **Modular Architecture:** Easy to extend (add hydro, geothermal, etc.)
5. **Well-Scoped:** Realistic for hackathon (24h implementation)

### Technical Highlights

- **New Services:** 4 new decision intelligence modules
- **Enhanced Models:** 7 new Pydantic data models
- **API Design:** RESTful with clear semantics
- **Frontend:** React comparison component with visual hierarchy
- **AI Integration:** Decision-focused prompting strategy

---

## 📚 Documentation

- 📘 **[ENERSCOPEAI.md](ENERSCOPEAI.md)** — Complete technical documentation
- 🚀 **[QUICKSTART.md](QUICKSTART.md)** — Get started in 5 minutes
- 📖 **[DOCUMENTATION.md](DOCUMENTATION.md)** — Original HelioScopeAI docs
- 🎤 **[PITCHDECK.md](PITCHDECK.md)** — Investor pitch (HelioScope AI)

---

## ⚠️ Important Disclaimers

### What EnerScopeAI IS:
✅ Decision intelligence tool for comparing renewable options  
✅ Confidence-aware recommendations for non-experts  
✅ Transparent about uncertainty and risk  
✅ Hackathon-scale proof-of-concept

### What EnerScopeAI IS NOT:
❌ Engineering-grade simulation tool  
❌ Replacement for professional site assessment  
❌ Full wind turbine design software  
❌ Financial investment advice  

**Recommendation:** Use EnerScopeAI for preliminary screening and decision-making. Follow up with professional feasibility studies for projects > 50 kW or when confidence < 70%.

---

# HelioScope AI 🌞 (Original Platform)
**Renewable Energy Placement Intelligence Platform**

> Foundation platform: Hybrid multi-factor renewable energy placement optimization engine using Gaussian-sigmoid scoring, economic feasibility modeling, plant capacity planning, and adaptive regional calibration.

---

## 🚀 What was HelioScope AI?

HelioScope AI is the production-grade solar energy site selection platform that serves as the foundation for EnerScopeAI. It combines real-time satellite data, an 8-factor machine learning-inspired scoring engine, and AI-generated financial analysis to help find optimal solar locations.

**Core HelioScope AI features (retained in EnerScopeAI):**
- 🛰️ **Real NASA + Open-Meteo data** — not static tables
- 🧮 **8-factor Gaussian-sigmoid algorithm** — calibrated to real-world solar performance
- 🏭 **Plant-size capacity planning** — 10/20/30/50 kW or custom
- 🤖 **Gemini AI analysis** — human-readable site reports
- 📈 **Adaptive regional calibration** — learns from historical analysis data
- 💰 **PM Surya Ghar subsidy calculator** — MNRE 2026 CFA rates

---

## 🖼️ Screenshots

| Map View | Analysis Results | Energy Dashboard |
|----------|-----------------|-----------------|
| Satellite map with area drawing | 8-factor score + confidence | 7-tab Smart Energy Dashboard |

---

## 🏗️ Original Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    React Frontend                        │
│  Map (Leaflet) → AnalysisPanel → ResultsPanel → Charts  │
└────────────────────────┬────────────────────────────────┘
                         │ REST API (FastAPI)
┌────────────────────────▼────────────────────────────────┐
│                   FastAPI Backend                        │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │  NASA    │  │Open-Meteo│  │Elevation │  ← Concurrent │
│  │  POWER   │  │ Weather  │  │ +Slope   │    fetch      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘              │
│       └─────────────┴─────────────┘                     │
│                      ↓                                   │
│         ┌──────────────────────┐                        │
│         │  8-Factor Scoring v3 │                        │
│         │  Gaussian + Sigmoid  │                        │
│         │  + EMA Calibrator    │                        │
│         └──────────┬───────────┘                        │
│                    ↓                                     │
│         ┌──────────────────────┐                        │
│         │   ROI Engine v2      │                        │
│         │   Plant-size first   │                        │
│         │   PM Surya Ghar CFA  │                        │
│         └──────────┬───────────┘                        │
│                    ↓                                     │
│         ┌──────────────────────┐                        │
│         │   Gemini AI LLM      │                        │
│         └──────────────────────┘                        │
└─────────────────────────────────────────────────────────┘
                         │
                  PostgreSQL DB
          (analyses stored for EMA calibration)
```
## 🏗️ Architecture of System

```mermaid
flowchart TB

%% =========================
%% USER LAYER
%% =========================

User[User]

%% =========================
%% FRONTEND LAYER
%% =========================

subgraph Frontend["Frontend Layer (React + Leaflet + Mapbox)"]

MapComponent[Map Component\nPolygon Selection]
AnalysisPanel[Analysis Panel\nPlant Capacity + Config]
ResultsPanel[Results Panel\nScore + Heatmap]
ROIComponent[ROI Dashboard]
SummaryComponent[AI Summary Panel]

APIService[API Service Layer]

MapComponent --> APIService
AnalysisPanel --> APIService
ResultsPanel --> APIService
ROIComponent --> APIService
SummaryComponent --> APIService

end

User --> MapComponent

%% =========================
%% API GATEWAY LAYER
%% =========================

subgraph APIGateway["API Gateway Layer"]

FastAPI[FastAPI Gateway\nAuth + Routing + Validation]

end

APIService --> FastAPI

%% =========================
%% BACKEND MICROSERVICES
%% =========================

subgraph Backend["Backend Microservices Layer"]

PlacementController[Placement Controller]
ROIController[ROI Controller]
SummaryController[Summary Controller]
AuthController[Auth Controller]

FastAPI --> PlacementController
FastAPI --> ROIController
FastAPI --> SummaryController
FastAPI --> AuthController

end

%% =========================
%% CORE ALGORITHM ENGINE
%% =========================

subgraph AlgorithmEngine["Hybrid Renewable Placement Optimization Engine (HRPOE)"]

GridEngine[Grid Division Engine\nPolygon → Grid Cells]

SolarService[Solar Irradiance Service]
WindService[Wind Speed Service]
ElevationService[Elevation Service]
WeatherService[Temperature + Cloud Service]
GridProximityService[Grid Infrastructure Service]

GaussianNormalizer[Gaussian Normalization Engine]
SigmoidNormalizer[Sigmoid Normalization Engine]

WeightedScoring[Weighted Multi-Factor Scoring Engine]

FeasibilityEngine[Plant Capacity Feasibility Engine]

ROIEngine[ROI Calculation Engine]

ConfidenceEngine[Confidence Score Engine]

HeatmapEngine[Heatmap Generator]

BestLocationEngine[Optimal Placement Selector]

end

PlacementController --> GridEngine

GridEngine --> SolarService
GridEngine --> WindService
GridEngine --> ElevationService
GridEngine --> WeatherService
GridEngine --> GridProximityService

SolarService --> GaussianNormalizer
WindService --> GaussianNormalizer
ElevationService --> GaussianNormalizer

WeatherService --> SigmoidNormalizer
GridProximityService --> SigmoidNormalizer

GaussianNormalizer --> WeightedScoring
SigmoidNormalizer --> WeightedScoring

WeightedScoring --> FeasibilityEngine

FeasibilityEngine --> ROIEngine

ROIEngine --> ConfidenceEngine

ConfidenceEngine --> HeatmapEngine

HeatmapEngine --> BestLocationEngine

BestLocationEngine --> PlacementController

ROIController --> ROIEngine

%% =========================
%% LLM SERVICE
%% =========================

subgraph LLMService["AI Explanation Service"]

LLMEngine[LLM Service\nGemini / OpenAI]

end

SummaryController --> LLMEngine

%% =========================
%% DATABASE
%% =========================

subgraph Database["Database Layer"]

PostgreSQL[(PostgreSQL\nUser Data\nAnalysis Data\nCache)]

end

PlacementController --> PostgreSQL
ROIController --> PostgreSQL
SummaryController --> PostgreSQL
AuthController --> PostgreSQL

%% =========================
%% EXTERNAL APIs
%% =========================

subgraph ExternalAPIs["External Data Providers"]

NASA[NASA POWER API\nSolar Irradiance]
OpenMeteo[Open-Meteo API\nWeather Data]
ElevationAPI[Open Elevation API]
OSM[OpenStreetMap API\nGrid Infrastructure]

end

SolarService --> NASA
WindService --> OpenMeteo
WeatherService --> OpenMeteo
ElevationService --> ElevationAPI
GridProximityService --> OSM



%% =========================
%% SECURITY LAYER
%% =========================

subgraph Security["Security Layer"]

JWT[JWT Authentication]
RateLimit[Rate Limiting]
APISecurity[API Validation]
Secrets[Secrets Management]

end

AuthController --> JWT
FastAPI --> RateLimit
FastAPI --> APISecurity
BackendPod --> Secrets

%% =========================
%% FINAL OUTPUT FLOW
%% =========================

PlacementController --> ResultsPanel
ROIController --> ROIComponent
SummaryController --> SummaryComponent

ResultsPanel --> User
ROIComponent --> User
SummaryComponent --> User
```

---

## ⚡ Scoring Algorithm — 8 Factors

| Factor | Weight | Method | What it measures |
|--------|--------|--------|-----------------|
| ☀️ Solar Irradiance | 30% | Gaussian (optimal 5.5 kWh/m²/d) | Primary energy potential |
| 🌡️ Temperature | 10% | Gaussian (optimal 22°C) | Panel efficiency factor |
| ⛰️ Elevation | 10% | Gaussian (optimal 600m) | Atmospheric clarity |
| 💨 Wind Speed | 8% | Gaussian (optimal 3.5 m/s) | Convective cooling |
| ☁️ Cloud Cover | 10% | Sigmoid (inverted) | Yield reduction |
| 📐 Terrain Slope | 10% | Step function (<5°/5-15°/>15°) | Installation feasibility |
| ⚡ Grid Proximity | 12% | Sigmoid (0-50km) | Connection cost |
| 🏭 Plant Feasibility | 10% | Sigmoid (area ratio + irradiance) | Capacity viability |

**+ Adaptive EMA Calibration**: Regional bias correction using exponential moving average on historical analysis data (±10 points max).

---

## 🛠️ Tech Stack

### Backend
| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI 0.115 |
| Scoring Engine | Pure Python (custom Gaussian-sigmoid) |
| Solar Data | NASA POWER API (ALLSKY_SFC_SW_DWN) |
| Weather Data | Open-Meteo API (wind, temp, humidity, cloud cover) |
| Elevation + Slope | Google Maps / Open-Elevation (5-point stencil) |
| AI Summary | Google Gemini 2.0 Flash |
| Database | PostgreSQL 16 + SQLAlchemy |
| Auth | JWT (HS256) + bcrypt |
| Rate Limiting | SlowAPI |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 19 + Vite 7 |
| Map | Leaflet.js + react-leaflet |
| Geocoding | Nominatim (OpenStreetMap) |
| Charts | Recharts |
| Styling | Vanilla CSS (dark mode, glassmorphism) |

---

## 🚦 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- PostgreSQL 16+

### 1. Clone & setup environment
```bash
git clone https://github.com/tejasbargujepatil/HelioScopeAI.git
cd HelioScopeAI
cp .env.example .env
# Fill in your API keys in .env
```

### 2. Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Start the API server
uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Frontend
```bash
cd frontend
npm install
echo "VITE_API_URL=http://localhost:8001" > .env.local
npm run dev
```

Open **http://localhost:5173**



---

## 🔑 Environment Variables

```env
# Backend (.env)
DATABASE_URL=postgresql://user:pass@localhost:5432/helioscope
JWT_SECRET=your-super-secret-key
GEMINI_API_KEY=your-gemini-api-key
GOOGLE_ELEVATION_API_KEY=your-google-key  # optional (falls back to Open-Elevation)

# Frontend (.env.local)
VITE_API_URL=http://localhost:8001
```

---

## 📡 API Reference

### `POST /api/analyze`
Main pipeline endpoint — single call returns everything.

**Request:**
```json
{
  "lat": 26.92,
  "lng": 70.90,
  "plant_size_kw": 20,
  "electricity_rate": 8.0,
  "installation_cost": 0
}
```

**Response:**
```json
{
  "score": 90,
  "grade": "A+",
  "confidence": 96.0,
  "suitability_class": "Excellent",
  "solar_irradiance": 6.5,
  "slope_degrees": 1.2,
  "cloud_cover_pct": 18.0,
  "plant_size_kw": 20,
  "required_land_area_m2": 160,
  "annual_savings_inr": 672000,
  "payback_years": 1.5,
  "subsidy_amount_inr": 78000,
  "ai_summary": "This location in Rajasthan..."
}
```

Full API docs: **http://localhost:8001/docs**

---

## 💰 Subscription Tiers

| Feature | Free | Pro | Enterprise |
|---------|------|-----|-----------|
| Analyses/month | 3 | 50 | Unlimited |
| Smart Energy Dashboard | ❌ | ✅ | ✅ |
| AI Summaries | ❌ | ✅ | ✅ |
| Export Reports | ❌ | ❌ | ✅ |

---

## 🌍 Data Sources

| Data | Source | Lag |
|------|--------|-----|
| Solar irradiance | NASA POWER API | ~2 days |
| Wind, temp, humidity, cloud | Open-Meteo | Real-time |
| Elevation + slope | Google Maps / Open-Elevation | N/A |
| Geocoding | Nominatim (OpenStreetMap) | Real-time |
| Subsidy rates | MNRE PM Surya Ghar portal | Manually updated |

---

## 📄 License

MIT License — see [LICENSE](LICENSE)

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit: `git commit -m 'feat: add my feature'`
4. Push: `git push origin feature/my-feature`
5. Open a Pull Request

---

*Built with ☀️ for India's solar future*
