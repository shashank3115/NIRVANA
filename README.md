# 🌍 EnerScopeAI ☀️💨

### AI-Powered Multi-Renewable Decision Intelligence Platform

> Smart renewable energy decisions powered by AI, climate data, and confidence scoring.

EnerScopeAI helps users answer the real-world question:

> **“Which renewable energy source should I choose — and how confident can I be?”**

It compares renewable options like **Solar ☀️ and Wind 💨**, ranks them, evaluates risk, and provides confidence-aware recommendations with AI explanations.

---

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat\&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat\&logo=react)](https://react.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791?style=flat\&logo=postgresql)](https://postgresql.org)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat\&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

# 🎯 What is EnerScopeAI?

EnerScopeAI is a renewable energy decision intelligence platform that transforms site analysis from:

❌ “How much energy can I generate?”
➡
✅ “Which renewable source should I choose — and how reliable is that decision?”

It provides:

* 🔄 Multi-renewable comparison
* 🎯 Decision Confidence Index (0–100%)
* 🚦 GO / CAUTION / NO-GO recommendations
* ⚠️ Structured risk awareness
* 🏆 Ranked renewable options
* 🤖 Plain-language AI explanation
* 🔀 Hybrid feasibility assessment

---

# 🚀 Getting Started

## 📥 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/enerscopeai.git
cd enerscopeai
```

---

# 🖥️ Backend Setup (FastAPI)

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

**Mac / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Environment Variables

Create a `.env` file in the backend root:

```env
OPENAI_API_KEY=your_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/enerscope
NASA_POWER_BASE_URL=https://power.larc.nasa.gov/api
OPEN_METEO_BASE_URL=https://api.open-meteo.com
```

---

## 5️⃣ Run Backend Server

```bash
uvicorn main:app --reload
```

Backend runs at:

```
http://localhost:8000
```

Interactive API Docs:

```
http://localhost:8000/docs
```

---

# 🌐 Frontend Setup (React)

Navigate to frontend directory:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```
http://localhost:5173
```

Make sure backend is running before testing analysis.

---

# 🧪 Test the Analysis API

Example API test:

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

---

# 📦 Sample Response Includes

* Solar suitability score + confidence + recommendation
* Wind suitability score + confidence + recommendation
* Ranked best renewable option
* Decision Confidence Index
* Risk analysis by category
* AI-generated explanation

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
        │  🤖 AI Reasoning Layer              │
        └──────────────────────────────────────┘
                            ↓
        Ranked recommendations + Confidence-aware insights
```

---

# 🧠 Decision Confidence Index (DCI)

A 0–100% score representing how reliable the recommendation is.

### Factors Considered

* Data completeness
* Weather variability
* Economic stability
* Score separation
* Constraint severity

### Interpretation

| Confidence | Meaning                                           |
| ---------- | ------------------------------------------------- |
| 80–100%    | High confidence — proceed                         |
| 60–79%     | Moderate confidence — professional review advised |
| <60%       | Low confidence — site-specific study required     |

EnerScopeAI doesn’t just give answers.
It tells you how much to trust them.

---

# 🚦 GO / CAUTION / NO-GO Framework

### 🟢 GO

High suitability + High confidence + Strong ROI
→ Proceed with detailed planning.

### 🟡 CAUTION

Moderate metrics
→ Conduct professional feasibility study.

### 🔴 NO-GO

Low suitability or severe constraints
→ Explore alternative energy solutions.

---

# ⚠️ Risk Awareness Layer

EnerScopeAI categorizes risks into:

1. Technical / Environmental
2. Economic / Financial
3. Policy / Regulatory
4. Operational / Maintenance
5. Data / Uncertainty

Each risk includes severity, explanation, and mitigation suggestions.

---

# 🛠️ Tech Stack

### Frontend

* React
* Map-based UI
* Interactive comparison dashboard

### Backend

* FastAPI (Python 3.12)
* PostgreSQL
* Pydantic models

### Data Sources

* NASA POWER API
* Open-Meteo API
* OpenStreetMap
* Satellite-derived indicators

### AI Layer

* LLM reasoning engine
* Structured output prompting
* Constraint-aware explanation

---

# 🔮 Future Scope

* Micro-hydro integration
* Biomass analysis
* Battery storage optimization
* City-scale renewable heatmaps
* Real-time pricing models

---

# ⚠️ Disclaimer

EnerScopeAI is:

✔ A decision-support tool
✔ A pre-feasibility screening platform
✔ A confidence-aware AI assistant

It is NOT:

✘ Engineering-grade simulation software
✘ Financial investment advice
✘ A replacement for certified site surveys

For large-scale projects or confidence <70%, professional feasibility studies are recommended.

---

# 📜 License

MIT License

---

# 🚀 Vision

Clean energy decisions should be:

* Transparent
* Data-driven
* Confidence-aware
* Accessible to everyone

EnerScopeAI brings clarity, intelligence, and trust to renewable energy decision-making.
