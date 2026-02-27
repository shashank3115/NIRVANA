"""
EnerScopeAI — Pydantic Data Models v4
Supports multi-renewable comparison, decision confidence index, GO/CAUTION/NO-GO recommendations,
and risk awareness for solar and wind energy sources.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal


# ── Location / Climate ─────────────────────────────────────────────────────────

class LocationRequest(BaseModel):
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    panel_area: float = Field(default=100.0, gt=0)
    efficiency: float = Field(default=0.20, gt=0, le=1)


class ClimateData(BaseModel):
    solar_irradiance: float
    wind_speed: float
    elevation: float


class PlacementScoreResponse(BaseModel):
    score: int
    grade: str
    solar_irradiance: float
    wind_speed: float
    elevation: float
    solar_score: float
    wind_score: float
    elevation_score: float
    lat: float
    lng: float
    recommendation: str


# ── ROI ───────────────────────────────────────────────────────────────────────

class ROIRequest(BaseModel):
    solar_irradiance: float
    panel_area: float = Field(default=100.0, gt=0)
    efficiency: float = Field(default=0.20, gt=0, le=1)
    electricity_rate: float = Field(default=8.0)
    installation_cost: float = Field(default=0.0)
    plant_size_kw: Optional[float] = Field(default=None, gt=0)


class ROIResponse(BaseModel):
    energy_output_kwh_per_year: float
    annual_savings_inr: float
    payback_years: float
    lifetime_profit_inr: float
    monthly_savings_inr: float
    system_lifetime_years: int


class SummaryRequest(BaseModel):
    score: int
    roi_years: float
    lat: float
    lng: float
    solar_irradiance: Optional[float] = None
    wind_speed: Optional[float] = None
    elevation: Optional[float] = None
    annual_savings: Optional[float] = None


class SummaryResponse(BaseModel):
    summary: str
    generated_by: str


class HealthResponse(BaseModel):
    status: str
    version: str
    services: dict


# ── Unified Pipeline v3 ────────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    """
    Full pipeline request — capacity-first planning supported via plant_size_kw.
    """
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)

    # Capacity-first (preferred)
    plant_size_kw: Optional[float] = Field(
        default=10.0, gt=0,
        description="Desired plant capacity in kW (10/20/30/50 or custom)"
    )

    # Legacy area-first (still supported)
    panel_area: float = Field(default=80.0, ge=0, description="Panel area m² (0 = use plant_size_kw only)")
    efficiency: float = Field(default=0.20, gt=0, le=1)

    electricity_rate: float  = Field(default=8.0,  description="₹/kWh")
    installation_cost: float = Field(default=0.0,  description="₹ (0 = auto from plant_size)")

    # Optional user hints for scoring
    grid_distance_km: Optional[float] = Field(default=None, ge=0, description="km to nearest grid")
    available_area_m2: Optional[float] = Field(default=None, ge=0)


class AnalyzeResponse(BaseModel):
    """
    Full pipeline response — placement score + ROI + confidence + AI summary.
    """
    # ── Location ─────────────────────────────────────────────────────────
    lat: float
    lng: float

    # ── Measured climate data ─────────────────────────────────────────────
    solar_irradiance: float
    wind_speed: float
    elevation: float
    temperature_c: float
    humidity_pct: float
    cloud_cover_pct: float
    slope_degrees: float

    # ── Placement score ───────────────────────────────────────────────────
    score: int
    grade: str
    confidence: float                       # 0-100 %
    suitability_class: str                  # Excellent / Good / Moderate / Poor / Unsuitable
    recommendation: str
    constraint_violations: List[str]
    is_suitable: bool

    # Per-factor sub-scores (0-100)
    solar_score: float
    wind_score: float
    elevation_score: float
    temperature_score: float
    cloud_score: float
    slope_score: float
    grid_score: float
    plant_size_score: float

    calibration_adjustment: float
    algorithm_version: str

    # ── Plant sizing ──────────────────────────────────────────────────────
    plant_size_kw: float
    required_land_area_m2: float
    system_size_kwp: float
    installation_cost_inr: float

    # ── ROI ───────────────────────────────────────────────────────────────
    energy_output_kwh_per_year: float
    annual_savings_inr: float
    monthly_savings_inr: float
    daily_savings_inr: float
    payback_years: float
    lifetime_profit_inr: float
    system_lifetime_years: int

    # PM Surya Ghar subsidy
    subsidy_amount_inr: float
    net_cost_after_subsidy_inr: float
    payback_years_after_subsidy: float
    lifetime_profit_after_subsidy_inr: float

    # ── AI Summary ────────────────────────────────────────────────────────
    ai_summary: str
    ai_generated_by: str


# ═══════════════════════════════════════════════════════════════════════════════
# ENERSCOPEAI v4 — Multi-Renewable Decision Intelligence Models
# ═══════════════════════════════════════════════════════════════════════════════


class RenewableOptionAnalysis(BaseModel):
    """Analysis result for a single renewable energy source."""
    energy_source: str
    emoji: str
    suitability_score: int
    confidence_index: int
    recommendation: Literal["GO", "CAUTION", "NO-GO"]
    composite_viability: float
    payback_years: float
    annual_output_kwh: float
    key_strength: str
    key_weakness: str


class DecisionConfidence(BaseModel):
    """Decision Confidence Index and supporting data."""
    confidence_index: int  # 0-100
    confidence_label: str  # Very High / High / Moderate / Low / Very Low
    confidence_emoji: str
    confidence_factors: Dict[str, Any]
    uncertainty_sources: List[str]
    reliable_decision: bool
    explanation: str  # Plain language explanation


class RecommendationDetail(BaseModel):
    """GO/CAUTION/NO-GO recommendation with reasoning."""
    recommendation: Literal["GO", "CAUTION", "NO-GO"]
    reason: str
    action_items: List[str]
    risk_level: str
    confidence_in_recommendation: int


class RiskAnalysis(BaseModel):
    """Risk awareness analysis."""
    risk_level: str  # High / Medium / Low
    risk_emoji: str
    total_risks_identified: int
    show_stoppers: List[str]
    risks_by_category: Dict[str, List[str]]
    mitigation_suggestions: List[str]
    risk_score: int  # 0-100, higher = more risk
    risk_summary: str


class HybridPotential(BaseModel):
    """Assessment of hybrid renewable system potential."""
    recommended: bool
    reason: str
    score: float
    benefit: Optional[str] = None


class ComparisonSummary(BaseModel):
    """Multi-renewable comparison summary."""
    ranked_options: List[RenewableOptionAnalysis]
    best_option: Optional[RenewableOptionAnalysis]
    comparison_text: str
    hybrid_potential: HybridPotential
    total_options_analyzed: int


# ── EnerScopeAI Multi-Renewable Request ────────────────────────────────────────

class MultiRenewableRequest(BaseModel):
    """
    EnerScopeAI multi-renewable analysis request.
    Evaluates and compares solar and wind energy for a given location.
    """
    lat: float = Field(..., ge=-90, le=90)
    lng: float = Field(..., ge=-180, le=180)
    
    # System sizing
    plant_size_kw: float = Field(default=10.0, gt=0, description="Desired system size in kW")
    
    # Economic parameters
    electricity_rate: float = Field(default=8.0, description="₹/kWh or local currency")
    installation_cost_solar: Optional[float] = Field(default=None, description="₹ (auto if None)")
    installation_cost_wind: Optional[float] = Field(default=None, description="₹ (auto if None)")
    
    # Optional hints
    grid_distance_km: Optional[float] = Field(default=None, ge=0)
    available_area_m2: Optional[float] = Field(default=None, ge=0)
    
    # Options
    include_solar: bool = Field(default=True)
    include_wind: bool = Field(default=True)


# ── EnerScopeAI Multi-Renewable Response ───────────────────────────────────────

class EnerScopeResponse(BaseModel):
    """
    EnerScopeAI comprehensive multi-renewable decision intelligence response.
    """
    # ── Metadata ──────────────────────────────────────────────────────────
    analysis_type: str = "multi-renewable-comparison"
    platform_version: str = "EnerScopeAI-v1.0"
    
    # ── Location & Climate ────────────────────────────────────────────────
    lat: float
    lng: float
    solar_irradiance: float
    wind_speed: float
    elevation: float
    temperature_c: float
    humidity_pct: float
    cloud_cover_pct: float
    slope_degrees: float
    
    # ── Solar Analysis ────────────────────────────────────────────────────
    solar_suitability_score: int
    solar_grade: str
    solar_suitability_class: str
    solar_constraint_violations: List[str]
    solar_payback_years: float
    solar_annual_output_kwh: float
    solar_confidence_index: int
    solar_recommendation: RecommendationDetail
    
    # ── Wind Analysis ─────────────────────────────────────────────────────
    wind_suitability_score: int
    wind_grade: str
    wind_suitability_class: str
    wind_constraint_violations: List[str]
    wind_payback_years: float
    wind_annual_output_kwh: float
    wind_confidence_index: int
    wind_recommendation: RecommendationDetail
    wind_class: str
    wind_capacity_factor: int
    
    # ── Hydro Analysis ────────────────────────────────────────────────────
    hydro_suitability_score: Optional[int] = None
    hydro_grade: Optional[str] = None
    hydro_suitability_class: Optional[str] = None
    hydro_constraint_violations: Optional[List[str]] = None
    hydro_payback_years: Optional[float] = None
    hydro_annual_output_kwh: Optional[float] = None
    hydro_confidence_index: Optional[int] = None
    hydro_recommendation: Optional[RecommendationDetail] = None
    hydro_head_meters: Optional[float] = None
    hydro_flow_l_s: Optional[float] = None
    
    # ── Decision Intelligence ─────────────────────────────────────────────
    comparison: ComparisonSummary
    best_renewable_option: str  # "Solar" / "Wind" / "Hydro" / "Neither" / "Hybrid"
    overall_decision_confidence: DecisionConfidence
    
    # ── Risk Awareness ────────────────────────────────────────────────────
    solar_risk_analysis: RiskAnalysis
    wind_risk_analysis: RiskAnalysis
    hydro_risk_analysis: Optional[RiskAnalysis] = None
    
    # ── AI Explanation ────────────────────────────────────────────────────
    ai_decision_summary: str  # Decision-focused explanation
    ai_generated_by: str
    
    # ── Economic Summary ──────────────────────────────────────────────────
    best_option_economics: Dict[str, Any]
