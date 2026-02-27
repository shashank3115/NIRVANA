"""
EnerScopeAI — Micro-Hydro Suitability Evaluation Service
=========================================================
High-level micro-hydro (small-scale hydroelectric) energy feasibility assessment.
Evaluates potential based on water availability, elevation change, and flow rate.

Scope: Micro-hydro systems (1-100 kW)
NOT suitable for: Run-of-river environmental impact assessment, large dam projects
"""

import logging
import math
from typing import Dict, Any

logger = logging.getLogger(__name__)


# ── Micro-Hydro Constants ──────────────────────────────────────────────────────
MIN_HEAD_METERS = 5           # Minimum water drop for viable system
OPTIMAL_HEAD_METERS = 50      # Good micro-hydro potential
EXCELLENT_HEAD_METERS = 100   # Excellent potential
MIN_FLOW_L_S = 2              # Minimum water flow (liters/second)
OPTIMAL_FLOW_L_S = 20         # Good flow rate
EXCELLENT_FLOW_L_S = 50       # Excellent flow rate

# Efficiency
MICRO_HYDRO_EFFICIENCY = 0.80  # 80% typical for micro-hydro systems

# Environmental considerations
MIN_WATER_PROXIMITY_KM = 0.5   # Must be within 0.5 km of water source
RAINFALL_THRESHOLD_MM = 400    # Annual rainfall indicating perennial water


def calculate_hydro_suitability_score(
    water_proximity_km: float,
    elevation_gradient: float,
    rainfall_mm: float,
    lat: float,
    lng: float,
) -> Dict[str, Any]:
    """
    Calculate micro-hydro suitability score (0-100) and supporting metrics.
    
    This is a SIMPLIFIED feasibility assessment focused on decision confidence.
    Real hydro projects need hydrological surveys, environmental assessments, etc.
    
    Args:
        water_proximity_km: Distance to nearest river/stream (km)
        elevation_gradient: Average elevation change per km (meters/km)
        rainfall_mm: Annual rainfall (mm)
        lat: Latitude
        lng: Longitude
    
    Returns:
        Dict with:
        - score: 0-100 suitability
        - grade: A+ to F letter grade
        - constraint_violations: List of blocking issues
        - micro_hydro_class: Simple/Moderate/Complex/Challenging
        - estimated_flow_l_s: Estimated water flow (liters/second)
        - estimated_head_m: Estimated usable head (meters)
        - power_potential_kw: Estimated power output (kW)
        - seasonality_factor: 0-1, accounts for seasonal variation
    """
    
    constraint_violations = []
    
    # ── CONSTRAINT CHECK 1: Water Proximity ────────────────────────────────
    if water_proximity_km > 2.0:
        constraint_violations.append(
            f"Too far from water source ({water_proximity_km:.1f} km > 2 km). "
            "Penstock construction cost becomes prohibitive."
        )
    elif water_proximity_km > MIN_WATER_PROXIMITY_KM:
        constraint_violations.append(
            f"Water source at {water_proximity_km:.1f} km. "
            "Long penstock will increase installation cost significantly."
        )
    
    # ── CONSTRAINT CHECK 2: Head (Elevation Drop) ──────────────────────────
    estimated_head = calculate_estimated_head(elevation_gradient)
    if estimated_head < MIN_HEAD_METERS:
        constraint_violations.append(
            f"Insufficient elevation drop ({estimated_head:.1f}m < {MIN_HEAD_METERS}m). "
            "Area is too flat for micro-hydro."
        )
    
    # ── CONSTRAINT CHECK 3: Permanent Water Flow ──────────────────────────
    if rainfall_mm < RAINFALL_THRESHOLD_MM:
        constraint_violations.append(
            f"Low annual rainfall ({rainfall_mm}mm). "
            "Water source may be seasonal - not reliable year-round."
        )
    
    # Return failure if hard constraints violated
    if len(constraint_violations) >= 2:
        return {
            "score": 15,
            "grade": "F",
            "suitability_class": "Unsuitable",
            "constraint_violations": constraint_violations,
            "micro_hydro_class": "Not Feasible",
            "estimated_flow_l_s": 0,
            "estimated_head_m": estimated_head,
            "power_potential_kw": 0,
            "seasonality_factor": 0.2,
        }
    
    # ── FACTOR 1: Water Proximity (30% weight) ────────────────────────────
    proximity_score = score_water_proximity(water_proximity_km)
    
    # ── FACTOR 2: Elevation Gradient / Head (40% weight) ─────────────────
    head_score = score_elevation_head(estimated_head)
    
    # ── FACTOR 3: Expected Flow Rate (20% weight) ───────────────────────
    # Flow estimate based on rainfall and proximity to water
    estimated_flow = estimate_water_flow(rainfall_mm, water_proximity_km, lat, lng)
    flow_score = score_water_flow(estimated_flow)
    
    # ── FACTOR 4: Seasonality / Reliability (10% weight) ────────────────
    seasonality = estimate_seasonality(lat, rainfall_mm)
    
    # ── Composite Score ────────────────────────────────────────────────────
    # Base score from factors
    base_score = (
        proximity_score * 0.30 +
        head_score * 0.40 +
        flow_score * 0.20 +
        (seasonality * 100) * 0.10
    )
    
    # Apply constraint penalty
    constraint_penalty = 1.0 - (len(constraint_violations) * 0.15)
    final_score = base_score * constraint_penalty
    final_score = max(0, min(100, final_score))
    
    # Estimate power potential
    power_kw = estimate_power_output(estimated_head, estimated_flow)
    
    # Grade assignment
    if final_score >= 80:
        grade = "A+" if final_score >= 95 else "A"
        suitability_class = "Excellent"
        hydro_class = "Simple"
    elif final_score >= 70:
        grade = "B"
        suitability_class = "Good"
        hydro_class = "Moderate"
    elif final_score >= 50:
        grade = "C"
        suitability_class = "Moderate"
        hydro_class = "Moderate"
    elif final_score >= 30:
        grade = "D"
        suitability_class = "Poor"
        hydro_class = "Challenging"
    else:
        grade = "F"
        suitability_class = "Unsuitable"
        hydro_class = "Not Feasible"
    
    logger.info(
        f"Micro-hydro suitability: score={final_score:.0f}, head={estimated_head:.0f}m, "
        f"flow={estimated_flow:.1f}L/s, power={power_kw:.2f}kW"
    )
    
    return {
        "score": round(final_score, 1),
        "grade": grade,
        "suitability_class": suitability_class,
        "constraint_violations": constraint_violations,
        "micro_hydro_class": hydro_class,
        "estimated_flow_l_s": round(estimated_flow, 2),
        "estimated_head_m": round(estimated_head, 1),
        "power_potential_kw": round(power_kw, 2),
        "seasonality_factor": round(seasonality, 2),
    }


# ── Scoring Functions ──────────────────────────────────────────────────────────

def score_water_proximity(distance_km: float) -> float:
    """Score proximity to water source. Closer is better."""
    if distance_km <= 0.2:
        return 100.0  # Adjacent to water
    elif distance_km <= 0.5:
        return 90.0   # Very close
    elif distance_km <= 1.0:
        return 75.0   # Close
    elif distance_km <= 2.0:
        return 50.0   # Moderate distance
    elif distance_km <= 5.0:
        return 25.0   # Far, penstock cost high
    else:
        return 5.0    # Too far


def score_elevation_head(head_meters: float) -> float:
    """Score available elevation drop (head). More is better."""
    if head_meters < MIN_HEAD_METERS:
        return 0.0    # Not feasible
    elif head_meters < 10:
        return 30.0   # Marginal
    elif head_meters < 25:
        return 60.0   # Decent
    elif head_meters < OPTIMAL_HEAD_METERS:
        return 85.0   # Good
    elif head_meters < EXCELLENT_HEAD_METERS:
        return 95.0   # Very good
    else:
        # Beyond excellent - still good but may need more complex engineering
        return min(100.0, 85.0 + (head_meters - EXCELLENT_HEAD_METERS) / 100)


def score_water_flow(flow_l_s: float) -> float:
    """Score estimated water flow rate. More is better."""
    if flow_l_s < MIN_FLOW_L_S:
        return 20.0   # Marginal
    elif flow_l_s < 5:
        return 50.0   # Moderate
    elif flow_l_s < OPTIMAL_FLOW_L_S:
        return 80.0   # Good
    elif flow_l_s < EXCELLENT_FLOW_L_S:
        return 95.0   # Very good
    else:
        return 100.0  # Excellent


# ── Estimation Functions ──────────────────────────────────────────────────────

def calculate_estimated_head(elevation_gradient: float) -> float:
    """
    Estimate usable head based on elevation gradient.
    
    In reality, this requires topographic surveys and stream reconnaissance.
    This is a rough estimate for feasibility screening.
    
    Args:
        elevation_gradient: Meters of elevation change per km of stream
    
    Returns:
        Estimated usable head in meters (accounts for ~30% of vertical relief)
    """
    # Typical micro-hydro systems use 20-30% of gross elevation change
    # accounting for penstock placement and natural stream course
    usable_fraction = 0.25
    
    # Convert gradient to head over 1 km distance
    gross_head = elevation_gradient
    usable_head = gross_head * usable_fraction
    
    return max(0, usable_head)


def estimate_water_flow(rainfall_mm: float, water_proximity_km: float, lat: float, lng: float) -> float:
    """
    Estimate water flow rate (liters/second) based on rainfall and basin characteristics.
    
    This is HIGHLY approximate and should be verified with hydrological surveys.
    """
    
    # Regional rainfall patterns (simplified)
    # Equatorial and monsoon regions: higher water availability
    if -10 <= lat <= 30:  # Tropical/subtropical (monsoon)
        rainfall_factor = min(rainfall_mm / 2000, 1.0)  # Normalize to monsoon regions
    elif 30 < lat <= 60:  # Temperate
        rainfall_factor = min(rainfall_mm / 1500, 1.0)
    else:  # Polar / high altitude
        rainfall_factor = min(rainfall_mm / 800, 1.0)
    
    # Base flow estimation
    # Assumes small catchment area (~1-5 km²) typical for micro-hydro
    # Conversion: 1mm of rainfall over 1 km² = 1000 liters
    catchment_area_km2 = 2.0  # Typical small irrigation/river area
    annual_water_m3 = (rainfall_mm / 1000) * catchment_area_km2 * 1000  # m³
    daily_water_m3 = annual_water_m3 / 365
    daily_water_liters = daily_water_m3 * 1000
    flow_l_s = daily_water_liters / (24 * 3600)
    
    # Proximity penalty: farther from water = harder to access/develop
    proximity_factor = max(0.3, 1.0 - (water_proximity_km * 0.15))
    
    return flow_l_s * rainfall_factor * proximity_factor


def estimate_seasonality(lat: float, rainfall_mm: float) -> float:
    """
    Estimate water availability seasonality (0-1).
    
    1.0 = perennial flow year-round
    0.5 = significant seasonal variation
    0.0 = highly seasonal / dry season
    """
    
    # Low rainfall = highly seasonal
    if rainfall_mm < 400:
        seasonality = 0.3  # Unreliable
    elif rainfall_mm < 800:
        seasonality = 0.5  # Moderate seasonality
    elif rainfall_mm < 1500:
        seasonality = 0.75  # Good year-round
    else:
        seasonality = 0.9  # Perennial flow likely

    # Latitude adjustments (equator tends to have more reliable rainfall)
    if 0 <= abs(lat) <= 10:
        seasonality = min(1.0, seasonality * 1.1)  # Slightly better
    elif abs(lat) > 50:
        seasonality = max(0.3, seasonality * 0.7)  # Worse in polar regions

    return seasonality


def estimate_power_output(head_meters: float, flow_l_s: float) -> float:
    """
    Estimate power output using hydraulic power formula.
    
    Power (watts) = head (m) × flow (L/s) × gravity (9.81) × efficiency
    
    Simplified formula: P (kW) ≈ H (m) × Q (L/s) × 0.0078
    """
    
    if head_meters < MIN_HEAD_METERS or flow_l_s < MIN_FLOW_L_S:
        return 0.0
    
    # Hydraulic power formula: P = ρ × g × h × q
    # where ρ = 1 kg/L, g = 9.81 m/s², h = head, q = flow
    # P(kW) = 9.81 × h(m) × q(L/s) / 1000 × efficiency
    gross_power_kw = (9.81 * head_meters * flow_l_s) / 1000
    net_power_kw = gross_power_kw * MICRO_HYDRO_EFFICIENCY
    
    return max(0, net_power_kw)


def estimate_hydro_energy_output(
    head_meters: float,
    flow_l_s: float,
    capacity_factor: float = 0.4,
    system_efficiency: float = 0.75,
) -> Dict[str, Any]:
    """
    Estimate annual energy output from micro-hydro system.
    
    Args:
        head_meters: Available water head (meters)
        flow_l_s: Average water flow (liters/second)
        capacity_factor: 0.3-0.5 typical for micro-hydro
        system_efficiency: Includes penstock losses, generator efficiency
    
    Returns:
        Dict with annual_output_kwh, capacity_factor, system_efficiency
    """
    
    # Peak power potential
    peak_power_kw = estimate_power_output(head_meters, flow_l_s)
    
    # Apply system efficiency (penstock friction, transformer losses, etc.)
    system_power_kw = peak_power_kw * system_efficiency
    
    # Apply capacity factor (accounts for seasonal variation, maintenance, etc.)
    average_power_kw = system_power_kw * capacity_factor
    
    # Annual output
    annual_output_kwh = average_power_kw * 24 * 365
    
    logger.info(
        f"Micro-hydro output: peak={peak_power_kw:.2f}kW, "
        f"avg={average_power_kw:.2f}kW, annual={annual_output_kwh:.0f}kWh"
    )
    
    return {
        "peak_power_kw": round(peak_power_kw, 2),
        "average_power_kw": round(average_power_kw, 2),
        "annual_output_kwh": round(annual_output_kwh, 0),
        "capacity_factor": round(capacity_factor, 2),
        "system_efficiency": round(system_efficiency, 2),
    }
