# 🌍 EnerScopeAI ☀️💨

### AI-Powered Multi-Renewable Decision Intelligence Platform

> **From feasibility scores to confident decisions.**
> EnerScopeAI helps you answer the real question:
> **“Which renewable energy source should I choose — and how confident can I be?”**

---

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat\&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat\&logo=react)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat\&logo=postgresql)](https://postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat\&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

# 🎯 What is EnerScopeAI?

EnerScopeAI is an AI-powered renewable energy recommendation platform that transforms renewable site evaluation from:

> ❌ “How much energy can I generate?”
> ✅ “Which renewable source should I choose, and how confident is that recommendation?”

It compares **Solar ☀️ and Wind 💨** (extensible to hydro & biomass) and provides:

* 🔄 Multi-renewable comparison
* 🎯 Decision Confidence Index (0–100%)
* 🚦 GO / CAUTION / NO-GO recommendations
* ⚠️ Risk-aware reasoning by category
* 🏆 Ranked renewable options
* 🤖 Plain-language AI explanation
* 🔀 Hybrid feasibility assessment

---

# 🆕 Evolution: From HelioScopeAI → EnerScopeAI

| Feature        | HelioScopeAI       | EnerScopeAI                         |
| -------------- | ------------------ | ----------------------------------- |
| Energy Scope   | Solar Only         | Solar + Wind                        |
| Output         | Suitability Score  | **Decision + Confidence**           |
| Recommendation | Letter Grades      | **GO / CAUTION / NO-GO**            |
| Risk Awareness | Implicit           | **Explicit & Categorized**          |
| Comparison     | N/A                | **Ranked Renewable Options**        |
| AI Layer       | Descriptive        | **Decision-Focused Guidance**       |
| User Question  | “Is solar viable?” | **“Solar or wind? How confident?”** |

EnerScopeAI shifts from **simulation-first thinking** to **decision-first intelligence**.

---

# ⚡ Quick Start

### 🔌 Run Backend

```bash
uvicorn main:app --reload
```

### 🧪 Test Multi-Renewable Endpoint

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

### 📦 Response Includes:

* Solar suitability + confidence + recommendation
* Wind suitability + confidence + recommendation
* Ranked best renewable option
* Overall Decision Confidence Index
* AI-generated decision summary

---

# 🏗️ System Architecture

```
User → React Frontend → FastAPI Backend
                            ↓
        ┌──────────────────────────────────────┐
        │   Multi-Renewable Analysis Engine    │
        ├──────────────────────────────────────┤
        │  ☀️ Solar Suitability Engine        │
        │  💨 Wind Suitability Engine         │
        │  🎯 Decision Confidence Calculator  │
        │  🚦 GO/CAUTION/NO-GO Engine         │
        │  ⚠️ Risk Analyzer                   │
        │  🔄 Comparison & Ranking Engine     │
        │  🤖 Decision AI Layer (Gemini)     │
        └──────────────────────────────────────┘
                            ↓
        Ranked recommendations + Risk-aware reasoning
```

---

# 🧠 Core Innovation: Decision Confidence Index (DCI)

### What is DCI?

A 0–100% metric representing how reliable and trustworthy the recommendation is.

### DCI Considers:

* Data quality & completeness
* Weather variability
* Economic clarity (ROI stability)
* Suitability margin (clear winner vs borderline case)
* Constraint severity

### Interpretation:

| Confidence | Meaning                                           |
| ---------- | ------------------------------------------------- |
| 80–100%    | High confidence — proceed                         |
| 60–79%     | Moderate confidence — professional review advised |
| <60%       | Low confidence — site-specific study required     |

EnerScopeAI doesn't just give answers.
It tells you **how much to trust them.**

---

# 🚦 GO / CAUTION / NO-GO Framework

### 🟢 GO

* Suitability ≥ 65
* Confidence ≥ 60%
* ROI ≤ 7 years
  → *Proceed with quotes and planning.*

### 🟡 CAUTION

* Moderate suitability OR moderate confidence
  → *Professional feasibility study recommended.*

### 🔴 NO-GO

* Suitability < 40 OR critical constraints
  → *Explore alternative energy options.*

This eliminates ambiguity for non-experts.

---

# ⚠️ Risk Awareness Layer

EnerScopeAI categorizes risks into:

1. **Technical / Environmental**
2. **Economic / Financial**
3. **Policy / Regulatory**
4. **Operational / Maintenance**
5. **Data / Uncertainty**

Each includes:

* Risk severity
* Explanation
* Mitigation suggestions
* Show-stoppers identification

Transparency builds trust.

---

# 📊 Composite Viability Formula

```text
Viability Score =
  (Suitability × 0.40) +
  (Confidence × 0.30) +
  (Economic Score × 0.20) +
  (Recommendation Bonus × 0.10)
```

This allows meaningful ranking across renewable types.

---

# 👥 Target Users

* 🏠 Homeowners
* 💼 Small Investors
* 🎓 Students & Researchers
* 📊 Infrastructure Planners

---

# 📌 Example Output (Rajasthan Desert)

| Renewable | Score | Confidence | Recommendation |
| --------- | ----- | ---------- | -------------- |
| ☀️ Solar  | 92    | 94%        | GO             |
| 💨 Wind   | 48    | 62%        | CAUTION        |

🏆 Best Option: Solar
🎯 Overall Confidence: 88%
💡 AI Guidance: *“Proceed with solar installation. Excellent resource availability and economic viability.”*

---

# 🛠️ Tech Stack

### Frontend

* React 19
* Map-based location selection
* Comparison dashboard

### Backend

* FastAPI (Python 3.12)
* PostgreSQL 16
* Pydantic models

### Data Sources

* NASA POWER API
* Open-Meteo API
* OpenStreetMap
* Sentinel-2 (NDVI proxy)

### AI Layer

* Gemini / LLM API
* Structured output prompting
* Constraint-aware generation

---

# 📂 Project Structure

```
backend/
frontend/
docs/
models/
services/
routes/
```

Modular architecture for easy extension:

* Add Hydro
* Add Biomass
* Add Battery Optimization
* Add City-scale heatmaps

---

# 🎓 Why This Project Stands Out (Hackathon Angle)

✅ Novel shift from simulation to decision intelligence
✅ Clear real-world user problem
✅ Risk-aware & honest AI design
✅ Modular & scalable
✅ Strong product thinking + system design

This is not just a model.
It’s a **renewable decision platform.**

---

# ⚠️ Disclaimer

EnerScopeAI is:

✔ A decision-support tool
✔ A pre-feasibility screening system
✔ A confidence-aware AI assistant

It is NOT:

✘ Engineering-grade design software
✘ Financial investment advice
✘ A replacement for certified feasibility studies

For projects >50 kW or confidence <70%, professional assessment is recommended.

---

# 🚀 Future Roadmap

* 🌊 Micro-Hydro Integration
* 🌿 Biomass Analysis
* 🔋 Battery Optimization Engine
* 🏙️ City-Scale Renewable Heatmaps
* 📈 Real-time energy pricing integration
* 🧠 Advanced ML scoring models

---

# 📜 License

MIT License

---

# 👨‍💻 Built With Vision

EnerScopeAI represents the evolution of renewable feasibility tools into intelligent decision platforms.

> Clean energy decisions should be simple, transparent, and confident.
