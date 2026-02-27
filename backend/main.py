"""
EnerScopeAI — FastAPI Main Application
Multi-Renewable Energy Decision Intelligence Platform

Transforms HelioScopeAI (solar-only) into EnerScopeAI (multi-renewable comparison).
Provides decision confidence scoring, GO/CAUTION/NO-GO recommendations,
risk awareness, and comparative analysis for solar and wind energy.

Philosophy: Decision-first, not simulation-first. Help users confidently
choose which renewable energy source is best for their location.
"""

import os
import asyncio
import logging
import statistics
from contextlib import asynccontextmanager
from datetime import date, timedelta

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy.orm import Session

from models import (
    LocationRequest,
    PlacementScoreResponse,
    ROIRequest,
    ROIResponse,
    SummaryRequest,
    SummaryResponse,
    HealthResponse,
    AnalyzeRequest,
    AnalyzeResponse,
    MultiRenewableRequest,
    EnerScopeResponse,
    DecisionConfidence,
    RecommendationDetail,
    RiskAnalysis,
    ComparisonSummary,
)
from scoring import calculate_score
from roi import calculate_roi
from solar_service import fetch_solar_irradiance
from wind_service import fetch_weather, fetch_wind_speed
from elevation_service import fetch_elevation_and_slope, fetch_elevation
from llm_service import generate_summary, generate_decision_summary
from database import init_db, get_db, save_analysis
from scoring import calculate_score, get_calibrator

# EnerScopeAI new services
from wind_suitability_service import calculate_wind_suitability_score, estimate_wind_energy_output
from hydro_suitability_service import calculate_hydro_suitability_score, estimate_hydro_energy_output
from decision_engine import calculate_decision_confidence, generate_recommendation, explain_confidence
from comparison_engine import rank_renewable_options
from risk_analyzer import analyze_risks, generate_risk_summary
from ml_suitability_engine import (
    predict_energy_generation,
    predict_renewable_suitability,
    get_feature_importance,
    explain_ml_prediction,
)
from auth import (
    create_access_token, create_user, authenticate_user,
    get_current_user, require_auth, require_pro, require_enterprise,
    check_free_quota, increment_usage, get_usage_this_month,
    FREE_QUOTA,
)
from user_db import User, BillingRecord, SubscriptionTier
import energy_dashboard as ed
from heatmap_service import compute_heatmap
from seasonal_service import fetch_monthly_irradiance
from nationwide_heatmap import compute_nationwide_heatmap
from roi import calculate_tariff_sensitivity
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Tuple

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

# ── Rate Limiter ──────────────────────────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅ EnerScopeAI Backend starting up...")
    init_db()   # Connect to PostgreSQL and create tables
    # Bootstrap adaptive calibrator from historical DB analyses
    try:
        from database import SessionLocal
        with SessionLocal() as _db:
            get_calibrator().load_from_db(_db)
    except Exception as _e:
        logger.warning(f"Calibrator bootstrap skipped: {_e}")
    yield
    logger.info("🛑 EnerScopeAI Backend shutting down...")


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="EnerScopeAI API",
    description="Multi-Renewable Energy Decision Intelligence Platform - Solar, Wind, and Hydro comparison with confidence scoring",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS ──────────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:3000,http://localhost:80,http://localhost:8000,http://127.0.0.1:5176"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # lock down in production via env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Grid Distance Estimator (used in /api/analyze pipeline) ───────────────────
def _estimate_grid_km(lat: float, lng: float) -> float:
    """Heuristic grid proximity estimate when user doesn't provide grid_distance_km."""
    if 8 <= lat <= 37 and 68 <= lng <= 97:
        if 20 <= lat <= 30: return 8.0    # Indo-Gangetic plain — dense
        if lat >= 30:       return 20.0   # Himalayan foothills — sparse
        return 10.0                       # Southern India
    if 35 <= lat <= 72 and -10 <= lng <= 40: return 5.0    # Europe — excellent
    if 25 <= lat <= 60 and -130 <= lng <= -60: return 12.0  # North America
    if -35 <= lat <= 37 and -18 <= lng <= 52: return 25.0   # Africa / remote
    return 15.0  # Global default


def _estimate_water_proximity(lat: float, lng: float) -> float:
    """Heuristic estimate of proximity to water bodies (rivers, lakes, etc.)."""
    # Approximate major river/water regions
    if 10 <= lat <= 32 and 70 <= lng <= 90:
        return 5.0  # Indo-Gangetic plains with rivers
    if 20 <= lat <= 35 and 73 <= lng <= 97:
        return 8.0  # Deccan with water bodies
    if 35 <= lat <= 60 and -130 <= lng <= -60:
        return 4.0  # North America with lakes/rivers
    if 35 <= lat <= 70 and -10 <= lng <= 50:
        return 6.0  # Europe with multiple water bodies
    return 15.0  # Default distance


def _estimate_population_density(lat: float, lng: float) -> float:
    """Heuristic estimate of population density (people per km²)."""
    # Major urban regions
    if 19 <= lat <= 28 and 72 <= lng <= 80:
        return 400  # Mumbai region
    if 28 <= lat <= 29 and 77 <= lng <= 78:
        return 350  # Delhi region
    if 12 <= lat <= 13 and 79 <= lng <= 80:
        return 300  # Chennai region
    if 35 <= lat <= 70 and -100 <= lng <= -70:
        return 50   # North America urban
    if 40 <= lat <= 60 and -10 <= lng <= 40:
        return 100  # Europe urban
    return 10.0  # Default low density


def _clamp(value: float, min_value: float = 0.0, max_value: float = 100.0) -> float:
    return max(min_value, min(max_value, value))


def _norm(value: float, low: float, high: float) -> float:
    if high <= low:
        return 50.0
    return _clamp(((value - low) / (high - low)) * 100.0)


def _cv(values: list[float]) -> float:
    if not values:
        return 1.0
    mean_val = statistics.fmean(values)
    if mean_val == 0:
        return 1.0
    return statistics.pstdev(values) / abs(mean_val)


@app.get('/api/openmeteo/analyze', tags=['OpenMeteo'])
async def analyze_openmeteo_decision(lat: float, lng: float):
    """
    Open-Meteo-first decision endpoint for EnerScopeAI.
    Uses historical hourly climate data to produce explainable decision scores,
    confidence, recommendation, and projection-friendly outputs.
    """
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise HTTPException(status_code=400, detail='Invalid latitude or longitude')

    end_date = date.today() - timedelta(days=3)
    start_date = end_date - timedelta(days=730)

    params = {
        'latitude': round(lat, 4),
        'longitude': round(lng, 4),
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'hourly': 'shortwave_radiation,wind_speed_10m,temperature_2m,cloud_cover,relative_humidity_2m,precipitation',
        'timezone': 'auto',
    }

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.get('https://archive-api.open-meteo.com/v1/archive', params=params)
            resp.raise_for_status()
            payload = resp.json()
    except Exception as error:
        logger.error(f'[OpenMeteoDecision] Failed to fetch archive data: {error}')
        raise HTTPException(status_code=502, detail='Open-Meteo historical data unavailable')

    hourly = payload.get('hourly', {})
    times = hourly.get('time', [])
    if not times:
        raise HTTPException(status_code=502, detail='Open-Meteo returned empty timeseries')

    solar_wm2 = [float(v) for v in hourly.get('shortwave_radiation', []) if v is not None]
    wind_ms = [float(v) for v in hourly.get('wind_speed_10m', []) if v is not None]
    temp_c = [float(v) for v in hourly.get('temperature_2m', []) if v is not None]
    cloud_pct = [float(v) for v in hourly.get('cloud_cover', []) if v is not None]
    humidity_pct = [float(v) for v in hourly.get('relative_humidity_2m', []) if v is not None]
    precipitation_mm = [float(v) for v in hourly.get('precipitation', []) if v is not None]

    if not solar_wm2 or not wind_ms:
        raise HTTPException(status_code=502, detail='Open-Meteo returned insufficient climate variables')

    n_total = len(times)
    completeness_scores = [
        (len(solar_wm2) / n_total) * 100,
        (len(wind_ms) / n_total) * 100,
        (len(temp_c) / n_total) * 100 if temp_c else 0,
        (len(cloud_pct) / n_total) * 100 if cloud_pct else 0,
        (len(humidity_pct) / n_total) * 100 if humidity_pct else 0,
        (len(precipitation_mm) / n_total) * 100 if precipitation_mm else 0,
    ]
    data_completeness = _clamp(statistics.fmean(completeness_scores))

    solar_kwh_m2_day = statistics.fmean(solar_wm2) * 24.0 / 1000.0
    wind_mean = statistics.fmean(wind_ms)
    temp_std = statistics.pstdev(temp_c) if len(temp_c) > 1 else 6.0
    cloud_mean = statistics.fmean(cloud_pct) if cloud_pct else 50.0
    wind_std = statistics.pstdev(wind_ms) if len(wind_ms) > 1 else 2.5
    humidity_mean = statistics.fmean(humidity_pct) if humidity_pct else 55.0
    precipitation_annual_mm = (sum(precipitation_mm) / max(1, len(precipitation_mm)) * 24 * 365) if precipitation_mm else 850.0

    # Seasonal variability from monthly means
    monthly_solar: dict[str, list[float]] = {}
    monthly_wind: dict[str, list[float]] = {}
    for idx, ts in enumerate(times):
        month = ts[5:7] if len(ts) >= 7 else '00'
        if idx < len(hourly.get('shortwave_radiation', [])) and hourly['shortwave_radiation'][idx] is not None:
            monthly_solar.setdefault(month, []).append(float(hourly['shortwave_radiation'][idx]))
        if idx < len(hourly.get('wind_speed_10m', [])) and hourly['wind_speed_10m'][idx] is not None:
            monthly_wind.setdefault(month, []).append(float(hourly['wind_speed_10m'][idx]))

    monthly_solar_means = [statistics.fmean(v) for v in monthly_solar.values() if v]
    monthly_wind_means = [statistics.fmean(v) for v in monthly_wind.values() if v]
    seasonal_variability = _clamp((_cv(monthly_solar_means) + _cv(monthly_wind_means)) * 50.0)

    solar_component = _norm(solar_kwh_m2_day, 1.5, 7.0)
    cloud_component = 100.0 - _norm(cloud_mean, 15.0, 90.0)
    temp_stability = 100.0 - _norm(temp_std, 1.5, 11.0)
    solar_score = _clamp(0.50 * solar_component + 0.30 * cloud_component + 0.20 * temp_stability)

    wind_speed_component = _norm(wind_mean, 2.0, 10.0)
    wind_consistency = 100.0 - _norm(wind_std, 0.6, 5.0)
    wind_score = _clamp(0.60 * wind_speed_component + 0.40 * wind_consistency)

    seasonal_penalty = _clamp(seasonal_variability * 0.35, 0, 30)
    completeness_penalty = _clamp((100.0 - data_completeness) * 0.7, 0, 40)
    sparse_penalty = 15.0 if n_total < 6000 else 0.0
    confidence = _clamp(100.0 - seasonal_penalty - completeness_penalty - sparse_penalty)

    source_scores = {
        'Solar': solar_score,
        'Wind': wind_score,
    }
    best_source = max(source_scores, key=source_scores.get)
    best_score = source_scores[best_source]
    if best_score >= 70 and confidence >= 65:
        recommendation = 'GO'
    elif best_score >= 45 and confidence >= 40:
        recommendation = 'CAUTION'
    else:
        recommendation = 'NO-GO'

    uncertainty_notes = []
    if seasonal_variability >= 45:
        uncertainty_notes.append('Seasonal weather swings are high, so expected performance may vary strongly across the year.')
    if data_completeness < 92:
        uncertainty_notes.append('Some historical weather points are missing, reducing confidence in long-term pattern estimates.')
    if not uncertainty_notes:
        uncertainty_notes.append('Historical weather patterns are relatively stable, supporting stronger confidence in the recommendation.')

    solar_output = max(0.0, solar_kwh_m2_day * 365 * 5 * 0.8)
    wind_output = max(0.0, (wind_mean / 5.0) * 4200)
    hydro_output = max(0.0, (statistics.fmean(cloud_pct) if cloud_pct else 40.0) * 40.0)
    electricity_rate = 8.0

    def _payback(score: float) -> float:
        return round(4.5 + (100.0 - score) * 0.12, 1)

    def _cost(output: float, payback: float) -> float:
        return output * electricity_rate * payback

    comparison = [
        {
            'type': 'Solar',
            'score': round(solar_score),
            'confidence': round(confidence),
            'annual_output_kwh': round(solar_output),
            'payback_years': _payback(solar_score),
            'installation_cost_inr': round(_cost(solar_output, _payback(solar_score))),
            'recommendation': recommendation if best_source == 'Solar' else ('CAUTION' if solar_score >= 45 else 'NO-GO'),
            'risk': 'Medium' if confidence >= 60 else 'High',
        },
        {
            'type': 'Wind',
            'score': round(wind_score),
            'confidence': round(confidence),
            'annual_output_kwh': round(wind_output),
            'payback_years': _payback(wind_score),
            'installation_cost_inr': round(_cost(wind_output, _payback(wind_score))),
            'recommendation': recommendation if best_source == 'Wind' else ('CAUTION' if wind_score >= 45 else 'NO-GO'),
            'risk': 'Medium' if confidence >= 60 else 'High',
        },
        {
            'type': 'Hydro',
            'score': round(_clamp((wind_score * 0.35) + (solar_score * 0.25))),
            'confidence': round(_clamp(confidence - 15)),
            'annual_output_kwh': round(hydro_output),
            'payback_years': 14.0,
            'installation_cost_inr': round(_cost(hydro_output, 14.0)),
            'recommendation': 'CAUTION',
            'risk': 'High',
        },
    ]

    def _net(output: float, cost: float, years: int) -> int:
        return round((output * electricity_rate * years) - cost)

    solar_item = comparison[0]
    wind_item = comparison[1]
    hydro_item = comparison[2]
    projections = [
        {'year': 1, 'solar': _net(solar_item['annual_output_kwh'], solar_item['installation_cost_inr'], 1), 'wind': _net(wind_item['annual_output_kwh'], wind_item['installation_cost_inr'], 1), 'hydro': _net(hydro_item['annual_output_kwh'], hydro_item['installation_cost_inr'], 1)},
        {'year': 3, 'solar': _net(solar_item['annual_output_kwh'], solar_item['installation_cost_inr'], 3), 'wind': _net(wind_item['annual_output_kwh'], wind_item['installation_cost_inr'], 3), 'hydro': _net(hydro_item['annual_output_kwh'], hydro_item['installation_cost_inr'], 3)},
        {'year': 5, 'solar': _net(solar_item['annual_output_kwh'], solar_item['installation_cost_inr'], 5), 'wind': _net(wind_item['annual_output_kwh'], wind_item['installation_cost_inr'], 5), 'hydro': _net(hydro_item['annual_output_kwh'], hydro_item['installation_cost_inr'], 5)},
        {'year': 10, 'solar': _net(solar_item['annual_output_kwh'], solar_item['installation_cost_inr'], 10), 'wind': _net(wind_item['annual_output_kwh'], wind_item['installation_cost_inr'], 10), 'hydro': _net(hydro_item['annual_output_kwh'], hydro_item['installation_cost_inr'], 10)},
        {'year': 15, 'solar': _net(solar_item['annual_output_kwh'], solar_item['installation_cost_inr'], 15), 'wind': _net(wind_item['annual_output_kwh'], wind_item['installation_cost_inr'], 15), 'hydro': _net(hydro_item['annual_output_kwh'], hydro_item['installation_cost_inr'], 15)},
    ]

    weather_comparison = [
        {
            'condition': 'Observed historical baseline',
            'solar_irradiance': round(solar_kwh_m2_day, 2),
            'wind_speed': round(wind_mean, 2),
            'cloud_cover': round(cloud_mean, 1),
            'humidity': round(humidity_mean, 1),
            'best_option': best_source,
        },
        {
            'condition': 'High cloud scenario',
            'solar_irradiance': round(solar_kwh_m2_day * 0.8, 2),
            'wind_speed': round(wind_mean * 1.12, 2),
            'cloud_cover': round(min(95.0, cloud_mean + 18), 1),
            'humidity': round(min(95.0, humidity_mean + 8), 1),
            'best_option': 'Wind' if wind_score >= (solar_score - 8) else best_source,
        },
        {
            'condition': 'Clear sky scenario',
            'solar_irradiance': round(solar_kwh_m2_day * 1.12, 2),
            'wind_speed': round(wind_mean * 0.92, 2),
            'cloud_cover': round(max(8.0, cloud_mean - 20), 1),
            'humidity': round(max(25.0, humidity_mean - 8), 1),
            'best_option': 'Solar' if solar_score >= (wind_score - 8) else best_source,
        },
    ]

    explanation = (
        f'Open-Meteo historical data for this exact area indicates solar suitability {round(solar_score)}/100 and '
        f'wind suitability {round(wind_score)}/100. '
        f'Decision confidence is {round(confidence)}% based on '
        f'seasonal variability and data completeness. Recommendation: {recommendation}. '
        f'The strongest influencing factors were solar radiation ({solar_kwh_m2_day:.2f} kWh/m²/day), '
        f'cloud cover ({cloud_mean:.1f}%), wind speed ({wind_mean:.2f} m/s), humidity ({humidity_mean:.1f}%), '
        f'and temperature stability '
        f'(std {temp_std:.2f}°C). EnerScopeAI optimizes decision quality, not production engineering, '
        f'and this output is designed to communicate uncertainty transparently.'
    )

    return {
        'analysis_source': 'Open-Meteo historical hourly archive',
        'lat': lat,
        'lng': lng,
        'solar_suitability_score': round(solar_score),
        'wind_suitability_score': round(wind_score),
        'decision_confidence_index': round(confidence),
        'recommendation': recommendation,
        'recommended_source': best_source,
        'factors': {
            'avg_solar_kwh_m2_day': round(solar_kwh_m2_day, 2),
            'avg_wind_speed_ms': round(wind_mean, 2),
            'avg_cloud_cover_pct': round(cloud_mean, 1),
            'avg_humidity_pct': round(humidity_mean, 1),
            'annual_precipitation_mm': round(precipitation_annual_mm, 1),
            'temperature_stability_std_c': round(temp_std, 2),
            'wind_consistency_std_ms': round(wind_std, 2),
            'seasonal_variability_index': round(seasonal_variability, 1),
            'data_completeness_pct': round(data_completeness, 1),
        },
        'comparison': comparison,
        'projections': projections,
        'weather_comparison': weather_comparison,
        'uncertainty_notes': uncertainty_notes,
        'explanation': explanation,
    }



# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/api/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """Health check endpoint for load balancer / Kubernetes probes."""
    return HealthResponse(
        status="healthy",
        version="2.0.0-enerscopeai",
        services={
            "solar_scoring_engine": "v3-production",
            "wind_suitability_engine": "v1-feasibility",
            "hydro_suitability_engine": "v1-feasibility",
            "decision_confidence_engine": "v1-active",
            "risk_analyzer": "v1-active",
            "comparison_engine": "v1-active",
            "roi_engine": "v2-plant-size",
            "gemini_ai": "configured" if os.getenv("GEMINI_API_KEY") else "not_configured",
            "elevation_api": "google" if os.getenv("GOOGLE_ELEVATION_API_KEY") else "open-elevation",
            "database": "connected" if (os.getenv("SUPABASE_URL") or os.getenv("DATABASE_URL")) else "stateless",
        },
    )


# =========================================================================
# ┌────────────────────────────────────────────┐
# |           UNIFIED EXECUTION PIPELINE                        |
# |  User → React → FastAPI → NASA+Open-Meteo → Algorithm →    |
# |           ROI Engine → LLM → React → User                  |
# └────────────────────────────────────────────┘
# =========================================================================
@app.post("/api/analyze", response_model=AnalyzeResponse, tags=["Pipeline"])
@limiter.limit("20/minute")
async def analyze_full_pipeline(request: Request, body: AnalyzeRequest, db: Session = Depends(get_db)):
    """
    UNIFIED PIPELINE v3 — 8-factor Gaussian-sigmoid production engine.

    Step 1 → React sends coordinates + plant_size_kw to FastAPI
    Step 2 → Concurrent fetch: NASA Solar + Open-Meteo Weather + Elevation+Slope
    Step 3 → 8-factor scoring: solar/wind/temp/elev/cloud/slope/grid/plant-size
    Step 4 → ROI Engine: capacity-first (kW × irradiance × 365)
    Step 5 → LLM generates AI explanation
    Step 6 → Return ALL results: score, confidence, ROI, sub-scores, constraints
    """
    plant_kw = body.plant_size_kw or 10.0
    logger.info(
        f"[PIPELINEv3] lat={body.lat:.4f}, lng={body.lng:.4f} "
        f"plant={plant_kw}kW grid_dist={body.grid_distance_km}km"
    )

    # ── STEP 2: Concurrent fetch (solar + weather + elevation/slope) ──────
    logger.info("[PIPELINEv3] Step 2: Fetching NASA solar + Open-Meteo weather + elevation/slope concurrently...")
    solar, weather, elev_data = await asyncio.gather(
        fetch_solar_irradiance(body.lat, body.lng),
        fetch_weather(body.lat, body.lng),
        fetch_elevation_and_slope(body.lat, body.lng),
    )
    wind        = weather["wind_speed"]
    temp_c      = weather["temperature_c"]
    humidity    = weather["humidity_pct"]
    cloud_pct   = weather["cloud_cover_pct"]
    data_src    = weather.get("data_sources", 3)
    elevation   = elev_data["elevation"]
    slope_deg   = elev_data["slope_degrees"]
    grid_km     = body.grid_distance_km if body.grid_distance_km is not None else _estimate_grid_km(body.lat, body.lng)
    avail_m2    = body.available_area_m2 or (plant_kw * 8 * 2)  # generous default

    logger.info(
        f"[PIPELINEv3] solar={solar:.3f} wind={wind:.1f} elev={elevation:.0f}m "
        f"temp={temp_c:.1f}°C hum={humidity:.0f}% cloud={cloud_pct:.0f}% "
        f"slope={slope_deg:.1f}° grid={grid_km:.0f}km plant={plant_kw}kW"
    )

    # ── STEP 3: 8-factor scoring engine v3 ────────────────────────────────
    logger.info("[PIPELINEv3] Step 3: Running 8-factor Gaussian+sigmoid scoring engine v3...")
    score_result = calculate_score(
        solar_irradiance=solar,
        wind_speed=wind,
        elevation=elevation,
        temperature=temp_c,
        humidity=humidity,
        lat=body.lat,
        cloud_cover_pct=cloud_pct,
        slope_degrees=slope_deg,
        grid_distance_km=grid_km,
        plant_size_kw=plant_kw,
        available_area_m2=avail_m2,
        data_sources=data_src,
    )
    logger.info(
        f"[PIPELINEv3] Score={score_result['score']}/100 Grade={score_result['grade']} "
        f"Confidence={score_result['confidence']}% "
        f"Suitability={score_result['suitability_class']} "
        f"Adj={score_result['calibration_adjustment']:+.1f} "
        f"Violations={len(score_result['constraint_violations'])}"
    )

    # ── STEP 4: ROI Engine — capacity-first ────────────────────────────────
    logger.info("[PIPELINEv3] Step 4: ROI engine (capacity-first, plant_size_kw mode)...")
    roi_result = calculate_roi(
        solar_irradiance=solar,
        panel_area=body.panel_area,
        efficiency=body.efficiency,
        electricity_rate=body.electricity_rate,
        installation_cost=body.installation_cost if body.installation_cost > 0 else None,
        plant_size_kw=plant_kw,
    )
    logger.info(
        f"[PIPELINEv3] ROI: {roi_result['system_size_kwp']:.1f}kWp "
        f"area={roi_result['required_land_area_m2']:.0f}m² "
        f"cost=₹{roi_result['installation_cost_inr']:,.0f} "
        f"payback={roi_result['payback_years']}yr "
        f"annual=₹{roi_result['annual_savings_inr']:,.0f}"
    )

    # ── STEP 5: LLM AI explanation ─────────────────────────────────────────
    logger.info("[PIPELINEv3] Step 5: LLM generating AI explanation...")
    summary_result = await generate_summary(
        score=score_result["score"],
        roi_years=roi_result["payback_years"],
        lat=body.lat,
        lng=body.lng,
        solar_irradiance=solar,
        wind_speed=wind,
        elevation=elevation,
        annual_savings=roi_result["annual_savings_inr"],
    )

    # ── Persist to DB ──────────────────────────────────────────────────────
    save_analysis(db, {
        "lat": body.lat, "lng": body.lng,
        "panel_area": roi_result["required_land_area_m2"],
        "efficiency": body.efficiency,
        "solar_irradiance": solar, "wind_speed": wind, "elevation": elevation,
        "score": score_result["score"], "grade": score_result["grade"],
        "solar_score": score_result["solar_score"],
        "wind_score": score_result["wind_score"],
        "elevation_score": score_result["elevation_score"],
        "recommendation": score_result["recommendation"],
        "energy_output_kwh_per_year": roi_result["energy_output_kwh_per_year"],
        "annual_savings_inr": roi_result["annual_savings_inr"],
        "payback_years": roi_result["payback_years"],
        "lifetime_profit_inr": roi_result["lifetime_profit_inr"],
        "ai_summary": summary_result["summary"],
        "ai_provider": summary_result["generated_by"],
    })

    # ── STEP 6: Return full v3 response ────────────────────────────────────
    logger.info("[PIPELINEv3] Step 6: Returning full v3 response to React.")
    return AnalyzeResponse(
        # Location
        lat=body.lat, lng=body.lng,
        # Climate
        solar_irradiance=solar, wind_speed=wind, elevation=elevation,
        temperature_c=temp_c, humidity_pct=humidity,
        cloud_cover_pct=cloud_pct, slope_degrees=slope_deg,
        # Score
        score=score_result["score"],
        grade=score_result["grade"],
        confidence=score_result["confidence"],
        suitability_class=score_result["suitability_class"],
        recommendation=score_result["recommendation"],
        constraint_violations=score_result["constraint_violations"],
        is_suitable=score_result["is_suitable"],
        # Sub-scores
        solar_score=score_result["solar_score"],
        wind_score=score_result["wind_score"],
        elevation_score=score_result["elevation_score"],
        temperature_score=score_result["temperature_score"],
        cloud_score=score_result["cloud_score"],
        slope_score=score_result["slope_score"],
        grid_score=score_result["grid_score"],
        plant_size_score=score_result["plant_size_score"],
        calibration_adjustment=score_result["calibration_adjustment"],
        algorithm_version=score_result["algorithm_version"],
        # Plant sizing
        plant_size_kw=plant_kw,
        required_land_area_m2=roi_result["required_land_area_m2"],
        system_size_kwp=roi_result["system_size_kwp"],
        installation_cost_inr=roi_result["installation_cost_inr"],
        # ROI
        energy_output_kwh_per_year=roi_result["energy_output_kwh_per_year"],
        annual_savings_inr=roi_result["annual_savings_inr"],
        monthly_savings_inr=roi_result["monthly_savings_inr"],
        daily_savings_inr=roi_result["daily_savings_inr"],
        payback_years=roi_result["payback_years"],
        lifetime_profit_inr=roi_result["lifetime_profit_inr"],
        system_lifetime_years=roi_result["system_lifetime_years"],
        subsidy_amount_inr=roi_result["subsidy_amount_inr"],
        net_cost_after_subsidy_inr=roi_result["net_cost_after_subsidy_inr"],
        payback_years_after_subsidy=roi_result["payback_years_after_subsidy"],
        lifetime_profit_after_subsidy_inr=roi_result["lifetime_profit_after_subsidy_inr"],
        # AI
        ai_summary=summary_result["summary"],
        ai_generated_by=summary_result["generated_by"],
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ┌────────────────────────────────────────────┐
# |     ENERSCOPEAI MULTI-RENEWABLE PIPELINE   |
# |  User → React → FastAPI → Solar+Wind →     |
# |  Decision Engine → Risk → Comparison → AI  |
# └────────────────────────────────────────────┘
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/enerscopeai/analyze", response_model=EnerScopeResponse, tags=["EnerScopeAI"])
@limiter.limit("15/minute")
async def analyze_multi_renewable(
    request: Request,
    body: MultiRenewableRequest,
    db: Session = Depends(get_db)
):
    """
    ENERSCOPEAI v1.0 — Multi-Renewable Decision Intelligence Pipeline
    
    Analyzes and compares solar and wind energy for a given location,
    providing decision confidence, GO/CAUTION/NO-GO recommendations,
    risk awareness, and ranked comparison.
    
    This is NOT a simulation tool - it's a DECISION tool that helps users
    confidently choose which renewable energy source is best for their location.
    """
    
    plant_kw = body.plant_size_kw
    logger.info(
        f"[EnerScopeAI] Multi-renewable analysis: lat={body.lat:.4f}, lng={body.lng:.4f}, "
        f"plant={plant_kw}kW, solar={body.include_solar}, wind={body.include_wind}"
    )
    
    # ── STEP 1: Fetch common climate data ─────────────────────────────────
    logger.info("[EnerScopeAI] Step 1: Fetching climate data...")
    solar_irr, weather, elev_data = await asyncio.gather(
        fetch_solar_irradiance(body.lat, body.lng),
        fetch_weather(body.lat, body.lng),
        fetch_elevation_and_slope(body.lat, body.lng),
    )
    
    wind_speed = weather["wind_speed"]
    temp_c = weather["temperature_c"]
    humidity = weather["humidity_pct"]
    cloud_pct = weather["cloud_cover_pct"]
    elevation = elev_data["elevation"]
    slope_deg = elev_data["slope_degrees"]
    grid_km = body.grid_distance_km if body.grid_distance_km is not None else _estimate_grid_km(body.lat, body.lng)
    avail_m2 = body.available_area_m2 or (plant_kw * 8 * 2)
    
    logger.info(
        f"[EnerScopeAI] Climate: solar={solar_irr:.2f} kWh/m²/d, wind={wind_speed:.1f} m/s, "
        f"temp={temp_c:.1f}°C, elev={elevation:.0f}m, slope={slope_deg:.1f}°"
    )
    
    # ── STEP 1.5: ML-Based Feature Extraction & Predictions ────────────────
    logger.info("[EnerScopeAI] Step 1.5: Running ML models for renewable suitability...")
    try:
        # ML Prediction 1: Energy generation using Linear Regression
        ml_solar_output = predict_energy_generation(
            renewable_type="solar",
            solar_irradiance_kwh=solar_irr,
            wind_speed_ms=wind_speed,
            elevation_m=elevation,
            temperature_c=temp_c,
            plant_size_kw=plant_kw,
        )
        
        ml_wind_output = predict_energy_generation(
            renewable_type="wind",
            solar_irradiance_kwh=solar_irr,
            wind_speed_ms=wind_speed,
            elevation_m=elevation,
            temperature_c=temp_c,
            plant_size_kw=plant_kw,
        )
        
        logger.info(
            f"[EnerScopeAI] ML Linear Regression predictions: "
            f"solar={ml_solar_output:.0f} kWh/yr, wind={ml_wind_output:.0f} kWh/yr"
        )
        
        # ML Prediction 2: Renewable suitability using Random Forest
        ml_suitability_scores = predict_renewable_suitability(
            solar_irradiance=solar_irr,
            wind_speed=wind_speed,
            rainfall_mm=weather.get("rainfall_mm", 800),
            elevation_m=elevation,
            latitude=body.lat,
            vegetation_ndvi=0.4,  # Average vegetation - can be enhanced with Sentinel data later
            water_proximity_km=_estimate_water_proximity(body.lat, body.lng),
            population_density=_estimate_population_density(body.lat, body.lng),
            slope_degrees=slope_deg,
            temperature_c=temp_c,
        )
        
        logger.info(f"[EnerScopeAI] ML Random Forest predictions: {ml_suitability_scores}")
        
    except Exception as e:
        logger.warning(f"[EnerScopeAI] ML predictions failed: {e}, continuing with rule-based scoring")
        ml_solar_output = None
        ml_wind_output = None
        ml_suitability_scores = None
    
    # ── STEP 2: Solar Analysis ────────────────────────────────────────────
    logger.info("[EnerScopeAI] Step 2: Analyzing solar energy...")
    solar_score_result = calculate_score(
        solar_irradiance=solar_irr,
        wind_speed=wind_speed,
        elevation=elevation,
        temperature=temp_c,
        humidity=humidity,
        lat=body.lat,
        cloud_cover_pct=cloud_pct,
        slope_degrees=slope_deg,
        grid_distance_km=grid_km,
        plant_size_kw=plant_kw,
        available_area_m2=avail_m2,
        data_sources=weather.get("data_sources", 3),
    )
    
    solar_roi = calculate_roi(
        solar_irradiance=solar_irr,
        panel_area=80.0,
        efficiency=0.20,
        electricity_rate=body.electricity_rate,
        installation_cost=body.installation_cost_solar,
        plant_size_kw=plant_kw,
    )
    
    # Calculate solar decision confidence
    solar_weather_stability = 100 - (cloud_pct / 2)  # More clouds = less stability
    solar_seasonal_stability = 85 if 20 <= body.lat <= 35 else 75  # Rough estimate
    solar_economic_viability = 100 if solar_roi["payback_years"] <= 5 else (80 if solar_roi["payback_years"] <= 8 else 50)
    
    solar_confidence = calculate_decision_confidence(
        suitability_score=solar_score_result["score"],
        constraint_violations=solar_score_result["constraint_violations"],
        weather_variability_score=solar_weather_stability,
        data_completeness=100,
        seasonal_stability=solar_seasonal_stability,
        economic_viability_score=solar_economic_viability,
    )
    
    solar_recommendation = generate_recommendation(
        suitability_score=solar_score_result["score"],
        confidence_index=solar_confidence["confidence_index"],
        constraint_violations=solar_score_result["constraint_violations"],
        payback_years=solar_roi["payback_years"],
        energy_source="solar",
    )
    
    # Solar risk analysis
    solar_risk = analyze_risks(
        energy_source="solar",
        suitability_score=solar_score_result["score"],
        confidence_index=solar_confidence["confidence_index"],
        climate_data={
            "solar_irradiance": solar_irr,
            "cloud_cover_pct": cloud_pct,
            "slope_degrees": slope_deg,
            "temperature_c": temp_c,
            "humidity_pct": humidity,
            "elevation": elevation,
        },
        economic_data={
            "payback_years": solar_roi["payback_years"],
            "installation_cost_inr": solar_roi["installation_cost_inr"],
            "electricity_rate": body.electricity_rate,
        },
        location_data={"lat": body.lat, "lng": body.lng},
    )
    
    logger.info(
        f"[EnerScopeAI] Solar: score={solar_score_result['score']}/100, "
        f"confidence={solar_confidence['confidence_index']}%, "
        f"recommendation={solar_recommendation['recommendation']}"
    )
    
    # ── STEP 3: Wind Analysis ─────────────────────────────────────────────
    logger.info("[EnerScopeAI] Step 3: Analyzing wind energy...")
    wind_suitability = calculate_wind_suitability_score(
        wind_speed=wind_speed,
        elevation=elevation,
        slope_degrees=slope_deg,
        temperature_c=temp_c,
        humidity_pct=humidity,
        lat=body.lat,
        lng=body.lng,
    )
    
    wind_output = estimate_wind_energy_output(
        wind_speed=wind_speed,
        turbine_size_kw=plant_kw,
    )
    
    # Rough wind ROI estimate (wind typically 2-3x more expensive than solar)
    wind_install_cost = body.installation_cost_wind or (solar_roi["installation_cost_inr"] * 2.5)
    wind_annual_savings = wind_output["annual_output_kwh"] * body.electricity_rate
    wind_payback = wind_install_cost / wind_annual_savings if wind_annual_savings > 0 else 999
    
    # Calculate wind decision confidence
    wind_weather_stability = 70  # Wind is inherently more variable
    wind_seasonal_stability = 80  # Wind often more consistent across seasons
    wind_economic_viability = 100 if wind_payback <= 7 else (70 if wind_payback <= 12 else 40)
    
    wind_confidence = calculate_decision_confidence(
        suitability_score=wind_suitability["score"],
        constraint_violations=wind_suitability["constraint_violations"],
        weather_variability_score=wind_weather_stability,
        data_completeness=90,  # Less certain than solar (hub height unknown)
        seasonal_stability=wind_seasonal_stability,
        economic_viability_score=wind_economic_viability,
    )
    
    wind_recommendation = generate_recommendation(
        suitability_score=wind_suitability["score"],
        confidence_index=wind_confidence["confidence_index"],
        constraint_violations=wind_suitability["constraint_violations"],
        payback_years=wind_payback,
        energy_source="wind",
    )
    
    # Wind risk analysis
    wind_risk = analyze_risks(
        energy_source="wind",
        suitability_score=wind_suitability["score"],
        confidence_index=wind_confidence["confidence_index"],
        climate_data={
            "wind_speed": wind_speed,
            "slope_degrees": slope_deg,
            "temperature_c": temp_c,
            "humidity_pct": humidity,
            "elevation": elevation,
        },
        economic_data={
            "payback_years": wind_payback,
            "installation_cost_inr": wind_install_cost,
            "electricity_rate": body.electricity_rate,
        },
        location_data={"lat": body.lat, "lng": body.lng},
    )
    
    logger.info(
        f"[EnerScopeAI] Wind: score={wind_suitability['score']}/100, "
        f"confidence={wind_confidence['confidence_index']}%, "
        f"recommendation={wind_recommendation['recommendation']}"
    )
    
    # ── STEP 4: Hydro Analysis ────────────────────────────────────────────
    logger.info("[EnerScopeAI] Step 4: Analyzing hydro energy...")
    hydro_suitability = calculate_hydro_suitability_score(
        water_proximity_km=_estimate_water_proximity(body.lat, body.lng),
        elevation_gradient=slope_deg * 2,  # Rough gradient estimate
        rainfall_mm=weather.get("rainfall_mm", 800),
        lat=body.lat,
        lng=body.lng,
    )
    
    hydro_output = estimate_hydro_energy_output(
        head_meters=hydro_suitability.get("estimated_head_m", 0),
        flow_l_s=hydro_suitability.get("estimated_flow_l_s", 0),
    )
    
    # Rough hydro ROI estimate (hydro typically 3-5x more expensive than solar)
    hydro_install_cost = body.installation_cost_wind * 3.5 if body.installation_cost_wind else (solar_roi["installation_cost_inr"] * 4.0)
    hydro_annual_savings = hydro_output["annual_output_kwh"] * body.electricity_rate
    hydro_payback = hydro_install_cost / hydro_annual_savings if hydro_annual_savings > 0 else 999
    
    # Calculate hydro decision confidence
    hydro_weather_stability = 85  # Water flow more stable than wind
    hydro_seasonal_stability = hydro_suitability.get("seasonality_factor", 0.5) * 100
    hydro_economic_viability = 100 if hydro_payback <= 10 else (70 if hydro_payback <= 15 else 40)
    
    hydro_confidence = calculate_decision_confidence(
        suitability_score=hydro_suitability["score"],
        constraint_violations=hydro_suitability["constraint_violations"],
        weather_variability_score=hydro_weather_stability,
        data_completeness=70,  # Less certain than solar/wind (no surveys)
        seasonal_stability=hydro_seasonal_stability,
        economic_viability_score=hydro_economic_viability,
    )
    
    hydro_recommendation = generate_recommendation(
        suitability_score=hydro_suitability["score"],
        confidence_index=hydro_confidence["confidence_index"],
        constraint_violations=hydro_suitability["constraint_violations"],
        payback_years=hydro_payback,
        energy_source="hydro",
    )
    
    # Hydro risk analysis
    hydro_risk = analyze_risks(
        energy_source="hydro",
        suitability_score=hydro_suitability["score"],
        confidence_index=hydro_confidence["confidence_index"],
        climate_data={
            "rainfall_mm": weather.get("rainfall_mm", 800),
            "water_proximity_km": _estimate_water_proximity(body.lat, body.lng),
            "estimated_head_m": hydro_suitability.get("estimated_head_m", 0),
            "estimated_flow_l_s": hydro_suitability.get("estimated_flow_l_s", 0),
            "elevation": elevation,
        },
        economic_data={
            "payback_years": hydro_payback,
            "installation_cost_inr": hydro_install_cost,
            "electricity_rate": body.electricity_rate,
        },
        location_data={"lat": body.lat, "lng": body.lng},
    )
    
    logger.info(
        f"[EnerScopeAI] Hydro: score={hydro_suitability['score']}/100, "
        f"confidence={hydro_confidence['confidence_index']}%, "
        f"recommendation={hydro_recommendation['recommendation']}"
    )
    
    # ── STEP 5: Comparison & Ranking ──────────────────────────────────────
    logger.info("[EnerScopeAI] Step 5: Comparing and ranking options...")
    comparison = rank_renewable_options(
        solar_analysis={
            "suitability_score": solar_score_result["score"],
            "confidence_index": solar_confidence["confidence_index"],
            "payback_years": solar_roi["payback_years"],
            "recommendation": solar_recommendation["recommendation"],
            "annual_output_kwh": solar_roi["energy_output_kwh_per_year"],
            "solar_irradiance": solar_irr,
            "cloud_cover_pct": cloud_pct,
            "slope_degrees": slope_deg,
        },
        wind_analysis={
            "suitability_score": wind_suitability["score"],
            "confidence_index": wind_confidence["confidence_index"],
            "payback_years": wind_payback,
            "recommendation": wind_recommendation["recommendation"],
            "annual_output_kwh": wind_output["annual_output_kwh"],
            "wind_speed": wind_speed,
            "elevation": elevation,
            "slope_degrees": slope_deg,
        },
        hydro_analysis={
            "suitability_score": hydro_suitability["score"],
            "confidence_index": hydro_confidence["confidence_index"],
            "payback_years": hydro_payback,
            "recommendation": hydro_recommendation["recommendation"],
            "annual_output_kwh": hydro_output["annual_output_kwh"],
            "estimated_head_m": hydro_suitability.get("estimated_head_m", 0),
            "estimated_flow_l_s": hydro_suitability.get("estimated_flow_l_s", 0),
            "water_proximity_km": _estimate_water_proximity(body.lat, body.lng),
            "seasonality_factor": hydro_suitability.get("seasonality_factor", 0.5),
        },
        location_context={"lat": body.lat, "lng": body.lng},
    )
    
    best_option_name = comparison["best_option"]["energy_source"] if comparison["best_option"] else "Neither"
    
    # Overall decision confidence (aggregated across top options)
    if len(comparison["ranked_options"]) >= 2:
        overall_conf_index = int((comparison["ranked_options"][0]["confidence_index"] + 
                                   comparison["ranked_options"][1]["confidence_index"]) / 2)
    else:
        overall_conf_index = comparison["ranked_options"][0]["confidence_index"] if comparison["ranked_options"] else 50
    
    overall_confidence = calculate_decision_confidence(
        suitability_score=comparison["best_option"]["suitability_score"] if comparison["best_option"] else 0,
        constraint_violations=[],
        weather_variability_score=(solar_weather_stability + wind_weather_stability + hydro_weather_stability) / 3,
        data_completeness=95,
        seasonal_stability=(solar_seasonal_stability + wind_seasonal_stability + hydro_seasonal_stability) / 3,
        economic_viability_score=(solar_economic_viability + wind_economic_viability + hydro_economic_viability) / 3,
    )
    
    logger.info(
        f"[EnerScopeAI] Best option: {best_option_name}, "
        f"overall confidence: {overall_confidence['confidence_index']}%"
    )
    
    # ── STEP 5: Generate AI decision summary ──────────────────────────────
    logger.info("[EnerScopeAI] Step 5: Generating AI decision summary...")
    ai_summary = await generate_decision_summary(
        best_option=best_option_name,
        solar_data={
            "suitability_score": solar_score_result["score"],
            "confidence_index": solar_confidence["confidence_index"],
            "recommendation": solar_recommendation["recommendation"],
            "payback_years": solar_roi["payback_years"],
            "solar_irradiance": solar_irr,
        },
        wind_data={
            "suitability_score": wind_suitability["score"],
            "confidence_index": wind_confidence["confidence_index"],
            "recommendation": wind_recommendation["recommendation"],
            "payback_years": wind_payback,
            "wind_speed": wind_speed,
        },
        hydro_data={
            "suitability_score": hydro_suitability["score"],
            "confidence_index": hydro_confidence["confidence_index"],
            "recommendation": hydro_recommendation["recommendation"],
            "payback_years": hydro_payback,
            "estimated_head_m": hydro_suitability.get("estimated_head_m", 0),
            "estimated_flow_l_s": hydro_suitability.get("estimated_flow_l_s", 0),
        },
        lat=body.lat,
        lng=body.lng,
        comparison_summary=comparison["comparison_summary"],
    )
    
    # ── STEP 6: Compile and return response ───────────────────────────────
    logger.info("[EnerScopeAI] Step 6: Compiling response...")
    
    response = EnerScopeResponse(
        # Metadata
        analysis_type="multi-renewable-comparison",
        platform_version="EnerScopeAI-v1.0",
        
        # Location & Climate
        lat=body.lat,
        lng=body.lng,
        solar_irradiance=solar_irr,
        wind_speed=wind_speed,
        elevation=elevation,
        temperature_c=temp_c,
        humidity_pct=humidity,
        cloud_cover_pct=cloud_pct,
        slope_degrees=slope_deg,
        
        # Solar Analysis
        solar_suitability_score=solar_score_result["score"],
        solar_grade=solar_score_result["grade"],
        solar_suitability_class=solar_score_result["suitability_class"],
        solar_constraint_violations=solar_score_result["constraint_violations"],
        solar_payback_years=solar_roi["payback_years"],
        solar_annual_output_kwh=solar_roi["energy_output_kwh_per_year"],
        solar_confidence_index=solar_confidence["confidence_index"],
        solar_recommendation=RecommendationDetail(**solar_recommendation),
        
        # Wind Analysis
        wind_suitability_score=wind_suitability["score"],
        wind_grade=wind_suitability["grade"],
        wind_suitability_class=wind_suitability["suitability_class"],
        wind_constraint_violations=wind_suitability["constraint_violations"],
        wind_payback_years=wind_payback,
        wind_annual_output_kwh=wind_output["annual_output_kwh"],
        wind_confidence_index=wind_confidence["confidence_index"],
        wind_recommendation=RecommendationDetail(**wind_recommendation),
        wind_class=wind_suitability["wind_class"],
        wind_capacity_factor=wind_suitability["estimated_capacity_factor"],
        
        # Hydro Analysis
        hydro_suitability_score=hydro_suitability["score"],
        hydro_grade=hydro_suitability["grade"],
        hydro_suitability_class=hydro_suitability["suitability_class"],
        hydro_constraint_violations=hydro_suitability["constraint_violations"],
        hydro_payback_years=hydro_payback,
        hydro_annual_output_kwh=hydro_output["annual_output_kwh"],
        hydro_confidence_index=hydro_confidence["confidence_index"],
        hydro_recommendation=RecommendationDetail(**hydro_recommendation),
        hydro_head_meters=hydro_suitability.get("estimated_head_m", 0),
        hydro_flow_l_s=hydro_suitability.get("estimated_flow_l_s", 0),
        
        # Decision Intelligence
        comparison=ComparisonSummary(
            ranked_options=comparison["ranked_options"],
            best_option=comparison["best_option"],
            comparison_text=comparison["comparison_summary"],
            hybrid_potential=comparison["hybrid_potential"],
            total_options_analyzed=comparison["total_options_analyzed"],
        ),
        best_renewable_option=best_option_name,
        overall_decision_confidence=DecisionConfidence(
            **overall_confidence,
            explanation=explain_confidence(
                overall_confidence["confidence_index"],
                overall_confidence["uncertainty_sources"],
                overall_confidence["confidence_factors"],
            ),
        ),
        
        # Risk Awareness
        solar_risk_analysis=RiskAnalysis(
            **solar_risk,
            risk_summary=generate_risk_summary(solar_risk),
        ),
        wind_risk_analysis=RiskAnalysis(
            **wind_risk,
            risk_summary=generate_risk_summary(wind_risk),
        ),
        hydro_risk_analysis=RiskAnalysis(
            **hydro_risk,
            risk_summary=generate_risk_summary(hydro_risk),
        ),
        
        # AI Explanation
        ai_decision_summary=ai_summary["summary"],
        ai_generated_by=ai_summary["generated_by"],
        
        # Economic Summary
        best_option_economics={
            "best_option": best_option_name,
            "payback_years": (
                solar_roi["payback_years"] if best_option_name == "Solar" 
                else hydro_payback if best_option_name == "Hydro"
                else wind_payback
            ),
            "annual_output_kwh": (
                solar_roi["energy_output_kwh_per_year"] if best_option_name == "Solar" 
                else hydro_output["annual_output_kwh"] if best_option_name == "Hydro"
                else wind_output["annual_output_kwh"]
            ),
            "annual_savings": (
                solar_roi["annual_savings_inr"] if best_option_name == "Solar" 
                else hydro_annual_savings if best_option_name == "Hydro"
                else wind_annual_savings
            ),
            "installation_cost": (
                solar_roi["installation_cost_inr"] if best_option_name == "Solar" 
                else hydro_install_cost if best_option_name == "Hydro"
                else wind_install_cost
            ),
        },
    )
    
    logger.info(f"[EnerScopeAI] Analysis complete. Best: {best_option_name}")
    
    return response



# ── Legacy individual endpoints (kept for compatibility) ──────────────────────

@app.post("/api/analyze-placement", response_model=PlacementScoreResponse, tags=["Analysis"])
@limiter.limit("30/minute")
async def analyze_placement(request: Request, body: LocationRequest, db: Session = Depends(get_db)):
    """
    Main analysis endpoint.
    1. Fetches climate data from 3 external APIs in parallel.
    2. Computes placement score using weighted algorithm.
    3. Persists result to PostgreSQL (if DB is available).
    4. Returns score, grade, and breakdown.
    """
    logger.info(f"Analyzing placement for lat={body.lat}, lng={body.lng}")

    # Fetch all climate data concurrently
    solar, wind, elevation = await asyncio.gather(
        fetch_solar_irradiance(body.lat, body.lng),
        fetch_wind_speed(body.lat, body.lng),
        fetch_elevation(body.lat, body.lng),
    )

    # Calculate placement score
    result = calculate_score(solar, wind, elevation)

    # Persist to DB (non-blocking, best-effort)
    save_analysis(db, {
        "lat": body.lat,
        "lng": body.lng,
        "panel_area": body.panel_area,
        "efficiency": body.efficiency,
        "solar_irradiance": solar,
        "wind_speed": wind,
        "elevation": elevation,
        "score": result["score"],
        "grade": result["grade"],
        "solar_score": result["solar_score"],
        "wind_score": result["wind_score"],
        "elevation_score": result["elevation_score"],
        "recommendation": result["recommendation"],
    })

    return PlacementScoreResponse(
        score=result["score"],
        grade=result["grade"],
        solar_irradiance=solar,
        wind_speed=wind,
        elevation=elevation,
        solar_score=result["solar_score"],
        wind_score=result["wind_score"],
        elevation_score=result["elevation_score"],
        lat=body.lat,
        lng=body.lng,
        recommendation=result["recommendation"],
    )


# ── ROI Calculation ───────────────────────────────────────────────────────────
@app.post("/api/calculate-roi", response_model=ROIResponse, tags=["ROI"])
@limiter.limit("30/minute")
async def calculate_roi_endpoint(request: Request, body: ROIRequest):
    """
    Calculate ROI for a solar installation based on irradiance, panel specs,
    cost, and local electricity rate.
    """
    logger.info(f"Calculating ROI: area={body.panel_area}m², efficiency={body.efficiency}")

    result = calculate_roi(
        solar_irradiance=body.solar_irradiance,
        panel_area=body.panel_area,
        efficiency=body.efficiency,
        electricity_rate=body.electricity_rate,
        installation_cost=body.installation_cost,
    )

    return ROIResponse(**result)


# ── AI Summary ────────────────────────────────────────────────────────────────
@app.post("/api/generate-summary", response_model=SummaryResponse, tags=["AI"])
@limiter.limit("20/minute")
async def generate_summary_endpoint(request: Request, body: SummaryRequest):
    """
    Generate an AI-powered placement recommendation using Google Gemini.
    Falls back to template-based response if Gemini API key is not configured.
    """
    logger.info(f"Generating summary for score={body.score}, roi={body.roi_years}")

    result = await generate_summary(
        score=body.score,
        roi_years=body.roi_years,
        lat=body.lat,
        lng=body.lng,
        solar_irradiance=body.solar_irradiance,
        wind_speed=body.wind_speed,
        elevation=body.elevation,
        annual_savings=body.annual_savings,
    )

    return SummaryResponse(**result)


# ── Error Handlers ────────────────────────────────────────────────────────────
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "status_code": exc.status_code},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Please try again.", "status_code": 500},
    )


# ════════════════════════════════════════════════════════════════════════════════
# AUTH ROUTES
# ════════════════════════════════════════════════════════════════════════════════

class RegisterBody(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = ""

class LoginBody(BaseModel):
    email: str
    password: str


@app.post("/api/auth/register", tags=["Auth"])
async def register(body: RegisterBody, db: Session = Depends(get_db)):
    """Create a new account (Free tier by default)."""
    if db is None:
        raise HTTPException(503, "Database unavailable.")
    user = create_user(db, body.email, body.password, body.full_name or "")
    token = create_access_token(user.id, user.email, user.tier.value)
    return {
        "token": token,
        "user": {
            "id": user.id, "email": user.email,
            "full_name": user.full_name, "tier": user.tier.value,
            "analyses_used": 0, "analyses_limit": FREE_QUOTA,
        }
    }


@app.post("/api/auth/login", tags=["Auth"])
async def login(body: LoginBody, db: Session = Depends(get_db)):
    """Authenticate and return a JWT token."""
    if db is None:
        raise HTTPException(503, "Database unavailable.")
    user = authenticate_user(db, body.email, body.password)
    token = create_access_token(user.id, user.email, user.tier.value)
    used = get_usage_this_month(db, user.id)
    return {
        "token": token,
        "user": {
            "id": user.id, "email": user.email,
            "full_name": user.full_name, "tier": user.tier.value,
            "analyses_used": used,
            "analyses_limit": FREE_QUOTA if user.tier == SubscriptionTier.free else None,
        }
    }


@app.get("/api/auth/me", tags=["Auth"])
async def get_me(
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Return current user profile. Returns null if not authenticated."""
    if user is None:
        return {"user": None}
    used = get_usage_this_month(db, user.id) if db else 0
    return {
        "user": {
            "id": user.id, "email": user.email,
            "full_name": user.full_name, "tier": user.tier.value,
            "analyses_used": used,
            "analyses_limit": FREE_QUOTA if user.tier == SubscriptionTier.free else None,
        }
    }


# ── Demo Tier Switcher (for judge/hackathon demos) ────────────────────────────
class DemoTierBody(BaseModel):
    tier: str      # "free" | "pro" | "enterprise"
    demo_key: str  # simple shared secret, not full auth

DEMO_SECRET = os.getenv("DEMO_SECRET_KEY", "enerscopeai-demo-2026")

@app.post("/api/auth/demo-tier", tags=["Auth"])
async def switch_demo_tier(
    body: DemoTierBody,
    user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    🎪 DEMO MODE — instantly switch subscription tier for live demonstrations.
    Requires demo_key (shared secret) + valid JWT.
    """
    if body.demo_key != DEMO_SECRET:
        raise HTTPException(status_code=403, detail="Invalid demo key.")
    if user is None or db is None:
        raise HTTPException(status_code=401, detail="Must be logged in to switch tier.")

    valid_tiers = {"free": SubscriptionTier.free, "pro": SubscriptionTier.pro, "enterprise": SubscriptionTier.enterprise}
    new_tier = valid_tiers.get(body.tier)
    if not new_tier:
        raise HTTPException(status_code=400, detail=f"Invalid tier '{body.tier}'. Use: free/pro/enterprise")

    user.tier = new_tier
    db.commit()
    db.refresh(user)

    # Issue fresh JWT with new tier claim
    new_token = create_access_token(user.id, user.email, new_tier.value)
    logger.info(f"[DEMO] {user.email} switched to tier={new_tier.value}")
    return {
        "message": f"✅ Switched to {new_tier.value} tier",
        "access_token": new_token,
        "token_type": "bearer",
        "user": {
            "id": user.id, "email": user.email,
            "tier": new_tier.value, "full_name": user.full_name,
            "analyses_used": 0, "analyses_limit": FREE_QUOTA if new_tier == SubscriptionTier.free else None,
        }
    }


# ════════════════════════════════════════════════════════════════════════════════
# BILLING ROUTES (Razorpay)
# ════════════════════════════════════════════════════════════════════════════════

TIER_PRICES = {
    "pro":        49900,   # ₹499 × 100 paise
    "enterprise": 199900,  # ₹1,999 × 100 paise
}

class BillingOrderBody(BaseModel):
    tier: str   # "pro" | "enterprise"

class BillingVerifyBody(BaseModel):
    razorpay_order_id:   str
    razorpay_payment_id: str
    razorpay_signature:  str
    tier: str


@app.post("/api/billing/create-order", tags=["Billing"])
async def create_billing_order(
    body: BillingOrderBody,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Create a Razorpay order for subscription upgrade."""
    if body.tier not in TIER_PRICES:
        raise HTTPException(400, "Invalid tier. Choose 'pro' or 'enterprise'.")
    amount = TIER_PRICES[body.tier]

    rzp_key = os.getenv("RAZORPAY_KEY_ID", "")
    rzp_secret = os.getenv("RAZORPAY_KEY_SECRET", "")

    order_id = f"mock_order_{user.id}_{body.tier}"
    if rzp_key and rzp_secret:
        try:
            import razorpay
            client = razorpay.Client(auth=(rzp_key, rzp_secret))
            order = client.order.create({
                "amount": amount, "currency": "INR",
                "notes": {"user_id": str(user.id), "tier": body.tier}
            })
            order_id = order["id"]
        except Exception as e:
            logger.warning(f"Razorpay order creation failed: {e}. Using mock order.")

    # Store pending billing record
    if db:
        record = BillingRecord(
            user_id=user.id,
            razorpay_order_id=order_id,
            amount_paise=amount,
            tier_granted=SubscriptionTier(body.tier),
            status="created",
        )
        db.add(record); db.commit()

    return {
        "order_id": order_id,
        "amount": amount,
        "currency": "INR",
        "key_id": rzp_key or "rzp_test_mock",
        "tier": body.tier,
    }


@app.post("/api/billing/verify", tags=["Billing"])
async def verify_billing(
    body: BillingVerifyBody,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db),
):
    """Verify Razorpay payment signature and upgrade user tier."""
    if db is None:
        raise HTTPException(503, "Database unavailable.")
    if body.tier not in TIER_PRICES:
        raise HTTPException(400, "Invalid tier.")

    # In mock mode or with real key, verify signature
    rzp_key = os.getenv("RAZORPAY_KEY_ID", "")
    rzp_secret = os.getenv("RAZORPAY_KEY_SECRET", "")
    verified = False

    if rzp_key and rzp_secret and not body.razorpay_order_id.startswith("mock_"):
        try:
            import razorpay, hmac, hashlib
            msg = f"{body.razorpay_order_id}|{body.razorpay_payment_id}"
            sig = hmac.new(rzp_secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
            verified = sig == body.razorpay_signature
        except Exception as e:
            logger.warning(f"Signature verification failed: {e}")
    else:
        verified = True   # mock/dev mode — always accept

    if not verified:
        raise HTTPException(400, "Payment verification failed.")

    # Upgrade user tier
    user.tier = SubscriptionTier(body.tier)
    db.commit()

    # Update billing record
    record = db.query(BillingRecord).filter(
        BillingRecord.razorpay_order_id == body.razorpay_order_id
    ).first()
    if record:
        record.razorpay_payment_id = body.razorpay_payment_id
        record.status = "paid"
        db.commit()

    token = create_access_token(user.id, user.email, user.tier.value)
    return {"success": True, "tier": user.tier.value, "token": token}


# ════════════════════════════════════════════════════════════════════════════════
# ENERGY DASHBOARD ROUTES (Pro+)
# ════════════════════════════════════════════════════════════════════════════════

class EnergyRequest(BaseModel):
    solar_irradiance:  float
    panel_area:        float
    efficiency:        float
    electricity_rate:  Optional[float] = 8.0
    energy_per_year:   Optional[float] = None


@app.post("/api/energy/dashboard", tags=["Energy"])
async def energy_dashboard(
    body: EnergyRequest,
    user: User = Depends(require_pro),
):
    """Full energy dashboard data — live curve + forecast + surplus + carbon + P2P + blockchain."""
    daily_kwh = body.solar_irradiance * body.panel_area * body.efficiency * 5.5
    annual_kwh = body.energy_per_year or (daily_kwh * 365)

    hourly      = ed.generate_24h_energy(body.solar_irradiance, body.panel_area, body.efficiency)
    forecast    = ed.predict_7day_energy(body.solar_irradiance, body.panel_area, body.efficiency)
    surplus     = ed.calculate_surplus(daily_kwh)
    carbon      = ed.calculate_carbon_savings(annual_kwh)
    p2p_market  = ed.generate_p2p_market(surplus["surplus_kwh"], body.electricity_rate)
    blockchain  = ed.generate_blockchain_ledger()

    return {
        "hourly_generation":  hourly,
        "weekly_forecast":    forecast,
        "surplus":            surplus,
        "carbon":             carbon,
        "p2p_market":         p2p_market,
        "blockchain_ledger":  blockchain,
        "daily_kwh":          round(daily_kwh, 2),
        "annual_kwh":         round(annual_kwh, 2),
    }


@app.post("/api/energy/carbon", tags=["Energy"])
async def carbon_endpoint(body: EnergyRequest, user: User = Depends(require_pro)):
    """Carbon savings endpoint."""
    annual_kwh = body.energy_per_year or (body.solar_irradiance * body.panel_area * body.efficiency * 5.5 * 365)
    return ed.calculate_carbon_savings(annual_kwh)


@app.post("/api/energy/p2p", tags=["Energy"])
async def p2p_endpoint(body: EnergyRequest, user: User = Depends(require_enterprise)):
    """P2P marketplace — Enterprise only."""
    daily_kwh = body.solar_irradiance * body.panel_area * body.efficiency * 5.5
    surplus   = ed.calculate_surplus(daily_kwh)
    return {
        "surplus":    surplus,
        "marketplace": ed.generate_p2p_market(surplus["surplus_kwh"], body.electricity_rate),
    }


@app.get("/api/energy/blockchain", tags=["Energy"])
async def blockchain_endpoint(user: User = Depends(require_enterprise)):
    """Blockchain ledger — Enterprise only."""
    return {"ledger": ed.generate_blockchain_ledger(10)}


# ════════════════════════════════════════════════════════════════════════════════
# HEATMAP — Micro-Grid Placement Analysis
# ════════════════════════════════════════════════════════════════════════════════

class HeatmapRequest(BaseModel):
    vertices: List[Tuple[float, float]]   # [[lat, lng], ...], min 3 points
    plant_size_kw:     float = 10.0
    solar_irradiance:  float = 5.5
    wind_speed:        float = 3.5
    temperature:       float = 25.0
    humidity:          float = 50.0
    cloud_cover_pct:   float = 30.0
    grid_distance_km:  Optional[float] = None
    available_area_m2: Optional[float] = None
    cell_metres:       int   = 100
    base_elevation:    float = 200.0   # reuse elevation from main analysis


@app.post("/api/heatmap", tags=["Analysis"])
@limiter.limit("10/minute")
async def heatmap_analysis(
    request: Request,
    body: HeatmapRequest,
    user: Optional[User] = Depends(get_current_user),
):
    """
    🌎 Micro-Grid Heatmap Analysis
    Divides the polygon into grid cells, scores each cell, identifies
    optimal placement sub-region, and returns grid-variance confidence calibration.
    """
    if len(body.vertices) < 3:
        raise HTTPException(400, "Polygon must have at least 3 vertices.")
    if body.cell_metres < 10 or body.cell_metres > 1000:
        raise HTTPException(400, "cell_metres must be 10–1000.")

    result = await compute_heatmap(
        vertices=body.vertices,
        plant_size_kw=body.plant_size_kw,
        solar_irradiance=body.solar_irradiance,
        wind_speed=body.wind_speed,
        temperature=body.temperature,
        humidity=body.humidity,
        cloud_cover_pct=body.cloud_cover_pct,
        grid_distance_km=body.grid_distance_km,
        available_area_m2=body.available_area_m2,
        cell_metres=body.cell_metres,
        base_elevation=body.base_elevation,
    )
    logger.info(f"[Heatmap] {result['cell_count']} cells, mean={result['score_mean']}, "
                f"conf_calibrated={result['confidence_calibrated']}%")
    return result


# ════════════════════════════════════════════════════════════════════════════════
# SEASONAL — Monthly Irradiance Time-Series
# ════════════════════════════════════════════════════════════════════════════════

@app.get("/api/seasonal", tags=["Analysis"])
async def seasonal_analysis(
    lat: float,
    lng: float,
    plant_size_kw: float = 10.0,
    user: Optional[User] = Depends(get_current_user),
):
    """
    📅 Seasonal Time-Series Simulation
    Fetches NASA POWER 12-month climatology for the location, computes
    monthly generation estimates and seasonal stability index.
    """
    seasonal = await fetch_monthly_irradiance(lat, lng)
    # Scale generation by actual plant size
    seasonal["monthly_gen_kwh"] = [
        round(v * plant_size_kw, 1)
        for v in seasonal["monthly_gen_kwh_per_kw"]
    ]
    seasonal["annual_total_kwh"] = round(seasonal["annual_kwh_per_kw"] * plant_size_kw, 0)
    seasonal["plant_size_kw"]    = plant_size_kw
    return seasonal


# ════════════════════════════════════════════════════════════════════════════════
# TARIFF SENSITIVITY
# ════════════════════════════════════════════════════════════════════════════════

class TariffSensRequest(BaseModel):
    lat:              float
    lng:              float
    plant_size_kw:    float  = 10.0
    solar_irradiance: float  = 5.5
    installation_cost: float = 500000.0

@app.post("/api/roi/sensitivity", tags=["Analysis"])
async def tariff_sensitivity(
    body: TariffSensRequest,
    user: Optional[User] = Depends(get_current_user),
):
    """
    📉 Tariff Sensitivity Analysis
    Returns ROI metrics at ₹4/6/8/10/12/15 per kWh for sensitivity chart.
    """
    table = calculate_tariff_sensitivity(
        solar_irradiance=body.solar_irradiance,
        plant_size_kw=body.plant_size_kw,
        installation_cost=body.installation_cost,
    )
    return {"sensitivity": table, "plant_size_kw": body.plant_size_kw}


# ════════════════════════════════════════════════════════════════════════════════
# NATIONWIDE INDIA HEATMAP
# ════════════════════════════════════════════════════════════════════════════════

@app.get("/api/heatmap/nationwide", tags=["Analysis"])
async def nationwide_heatmap(
    plant_size_kw: float = 10.0,
    user: Optional[User] = Depends(get_current_user),
):
    """
    🏭🗳️ Nationwide India Solar Heatmap
    Pre-computed 0.75°-resolution grid across all of India (~1300 cells).
    Uses estimated climate data — no external API calls — cached after first run.
    Returns cells with scores, top regions, and optimal national location.
    """
    result = await compute_nationwide_heatmap(plant_size_kw=plant_size_kw)
    return result
