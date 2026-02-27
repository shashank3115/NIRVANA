"""
EnerScopeAI — Wind Energy Suitability Evaluation Service
==========================================================
High-level wind energy feasibility assessment focused on decision-making
rather than engineering simulation. Evaluates wind potential based on
wind speed, terrain characteristics, and environmental factors.

NOTE: This is NOT a full wind turbine design tool. It provides decision
intelligence for whether wind energy is worth exploring further.
"""

import logging
import math
from typing import Dict, Any

logger = logging.getLogger(__name__)


# ── Wind Suitability Constants ────────────────────────────────────────────────
# Based on IEC wind class standards and small turbine requirements
MIN_VIABLE_WIND_SPEED = 4.0      # m/s - Below this, wind is generally unviable
OPTIMAL_WIND_SPEED = 7.0         # m/s - Good wind resource
EXCELLENT_WIND_SPEED = 9.0       # m/s - Excellent wind resource
MAX_SAFE_WIND_SPEED = 25.0       # m/s - Above this, needs expensive turbines

# Terrain considerations
MAX_ACCEPTABLE_SLOPE = 20.0      # degrees - Wind turbines need relatively flat land
OPTIMAL_ELEVATION_MIN = 50       # m - Some height helps, but not critical
OPTIMAL_ELEVATION_MAX = 2000     # m - Very high altitude has challenges

# Turbine sizing estimates (very rough, for feasibility only)
SMALL_TURBINE_KW = 10            # Residential scale
MEDIUM_TURBINE_KW = 50           # Small commercial
POWER_COEFFICIENT = 0.35         # Typical for small turbines (Betz limit = 0.59)


def calculate_wind_suitability_score(
    wind_speed: float,
    elevation: float,
    slope_degrees: float,
    temperature_c: float,
    humidity_pct: float,
    lat: float,
    lng: float,
) -> Dict[str, Any]:
    """
    Calculate wind energy suitability score (0-100) and supporting metrics.
    
    This is a SIMPLIFIED feasibility model focused on decision confidence,
    not engineering accuracy. Considers:
    - Wind speed (primary factor)
    - Terrain suitability
    - Air density (temp/elevation effect)
    - Geographic context
    
    Returns dict with:
    - score: 0-100 suitability score
    - grade: A+ to F letter grade
    - suitability_class: Excellent/Good/Moderate/Poor/Unsuitable
    - constraint_violations: List of blocking issues
    - wind_class: IEC wind class estimate
    - estimated_capacity_factor: % of rated capacity
    - subscore_wind_speed: 0-100
    - subscore_terrain: 0-100
    - subscore_air_density: 0-100
    """
    
    constraint_violations = []
    subscores = {}
    
    # ── CONSTRAINT CHECK: Hard failures ────────────────────────────────────
    if wind_speed < MIN_VIABLE_WIND_SPEED:
        constraint_violations.append(
            f"Wind speed too low ({wind_speed:.1f} m/s < {MIN_VIABLE_WIND_SPEED} m/s minimum)"
        )
    
    if slope_degrees > MAX_ACCEPTABLE_SLOPE:
        constraint_violations.append(
            f"Terrain too steep ({slope_degrees:.1f}° > {MAX_ACCEPTABLE_SLOPE}° max for wind turbines)"
        )
    
    # ── FACTOR 1: Wind Speed (50% weight) ──────────────────────────────────
    def score_wind_resource(ws: float) -> float:
        """Score wind speed using sigmoid and Gaussian combination."""
        if ws < MIN_VIABLE_WIND_SPEED:
            return 0.0
        elif ws < OPTIMAL_WIND_SPEED:
            # Linear ramp from 0.4 to 0.9 between 4-7 m/s
            return 0.4 + (ws - MIN_VIABLE_WIND_SPEED) / (OPTIMAL_WIND_SPEED - MIN_VIABLE_WIND_SPEED) * 0.5
        elif ws < EXCELLENT_WIND_SPEED:
            # Optimal range 7-9 m/s
            return 0.9 + (ws - OPTIMAL_WIND_SPEED) / (EXCELLENT_WIND_SPEED - OPTIMAL_WIND_SPEED) * 0.1
        elif ws < MAX_SAFE_WIND_SPEED:
            # Still good but approaching design limits
            return 1.0 - (ws - EXCELLENT_WIND_SPEED) / (MAX_SAFE_WIND_SPEED - EXCELLENT_WIND_SPEED) * 0.15
        else:
            # Too windy - needs special equipment
            return 0.7
    
    wind_speed_score = score_wind_resource(wind_speed)
    subscores["wind_speed"] = wind_speed_score * 100
    
    # ── FACTOR 2: Terrain Suitability (30% weight) ─────────────────────────
    def score_terrain(slope: float, elev: float) -> float:
        """Score terrain suitability for wind turbine installation."""
        slope_factor = 1.0 if slope < 5 else max(0.3, 1.0 - (slope - 5) / 15)
        
        # Elevation sweet spot - not too low, not too high
        if elev < OPTIMAL_ELEVATION_MIN:
            elev_factor = 0.8 + (elev / OPTIMAL_ELEVATION_MIN) * 0.2
        elif elev < OPTIMAL_ELEVATION_MAX:
            elev_factor = 1.0
        else:
            # Penalty for high altitude (air density, access, extreme weather)
            elev_factor = max(0.5, 1.0 - (elev - OPTIMAL_ELEVATION_MAX) / 2000 * 0.5)
        
        return slope_factor * 0.7 + elev_factor * 0.3
    
    terrain_score = score_terrain(slope_degrees, elevation)
    subscores["terrain"] = terrain_score * 100
    
    # ── FACTOR 3: Air Density (20% weight) ─────────────────────────────────
    def score_air_density(temp: float, elev: float, hum: float) -> float:
        """
        Score air density effect on wind power.
        Power ∝ air density, density decreases with temp and elevation.
        """
        # Standard air density at sea level, 15°C: 1.225 kg/m³
        # Approximate adjustment
        density_factor = (1.0 - elev / 10000) * (1.0 - (temp - 15) / 100)
        # Humidity has minor effect, simplify
        density_factor = max(0.7, min(1.1, density_factor))
        
        # Map to 0-1 score (optimal at 1.0)
        return min(1.0, density_factor / 0.95)
    
    air_density_score = score_air_density(temperature_c, elevation, humidity_pct)
    subscores["air_density"] = air_density_score * 100
    
    # ── COMPOSITE SCORE ────────────────────────────────────────────────────
    raw_score = (
        wind_speed_score * 0.50 +
        terrain_score * 0.30 +
        air_density_score * 0.20
    )
    
    # Apply constraint penalty
    if constraint_violations:
        raw_score *= 0.3  # Heavy penalty for violations
    
    final_score = int(round(raw_score * 100))
    final_score = max(0, min(100, final_score))
    
    # ── GRADING ────────────────────────────────────────────────────────────
    if final_score >= 90:
        grade, suitability = "A+", "Excellent"
    elif final_score >= 80:
        grade, suitability = "A", "Good"
    elif final_score >= 70:
        grade, suitability = "B+", "Good"
    elif final_score >= 60:
        grade, suitability = "B", "Moderate"
    elif final_score >= 50:
        grade, suitability = "C", "Moderate"
    elif final_score >= 40:
        grade, suitability = "D", "Poor"
    else:
        grade, suitability = "F", "Unsuitable"
    
    # ── WIND CLASS ESTIMATE ────────────────────────────────────────────────
    # IEC 61400-1 wind class (simplified)
    if wind_speed >= 8.5:
        wind_class = "Class I (High wind)"
    elif wind_speed >= 7.5:
        wind_class = "Class II (Medium wind)"
    elif wind_speed >= 6.0:
        wind_class = "Class III (Low wind)"
    else:
        wind_class = "Below Class III (Marginal)"
    
    # ── CAPACITY FACTOR ESTIMATE ───────────────────────────────────────────
    # Very rough estimate: small turbines typically 20-40% capacity factor
    if wind_speed < MIN_VIABLE_WIND_SPEED:
        capacity_factor = 5
    elif wind_speed < 6:
        capacity_factor = 15
    elif wind_speed < 7:
        capacity_factor = 25
    elif wind_speed < 9:
        capacity_factor = 35
    else:
        capacity_factor = 42
    
    logger.info(
        f"Wind suitability: score={final_score}/100 grade={grade} "
        f"wind={wind_speed:.1f}m/s class={wind_class} "
        f"capacity_factor={capacity_factor}%"
    )
    
    return {
        "score": final_score,
        "grade": grade,
        "suitability_class": suitability,
        "constraint_violations": constraint_violations,
        "is_suitable": len(constraint_violations) == 0 and final_score >= 50,
        "wind_class": wind_class,
        "estimated_capacity_factor": capacity_factor,
        "subscores": subscores,
        # Data quality indicators
        "data_completeness": 100,  # All parameters available
        "algorithm_version": "wind-v1.0-feasibility",
    }


def estimate_wind_energy_output(
    wind_speed: float,
    turbine_size_kw: float = SMALL_TURBINE_KW,
) -> Dict[str, float]:
    """
    Very rough estimate of annual wind energy output.
    
    WARNING: This is NOT engineering-grade. For decision guidance only.
    Real output depends on turbine model, hub height, wind distribution, etc.
    
    Uses simplified power curve: P = 0.5 * ρ * A * Cp * v³
    """
    # Air density (standard, kg/m³)
    rho = 1.225
    
    # Estimate rotor swept area from turbine size
    # Very rough: small 10kW turbine has ~7-9m diameter rotor
    rotor_diameter = math.sqrt(turbine_size_kw / 0.4) * 2  # Empirical scaling
    swept_area = math.pi * (rotor_diameter / 2) ** 2
    
    # Power in wind (W)
    power_in_wind = 0.5 * rho * swept_area * (wind_speed ** 3)
    
    # Extractable power (apply power coefficient and generator efficiency)
    extractable_power_w = power_in_wind * POWER_COEFFICIENT * 0.85
    
    # Cap at rated power
    actual_power_w = min(extractable_power_w, turbine_size_kw * 1000)
    
    # Annual energy (kWh) - assuming constant wind (huge simplification)
    # Real capacity factor is ~20-40%, so this is very optimistic
    hours_per_year = 8760
    annual_kwh_max = (actual_power_w / 1000) * hours_per_year
    
    # Apply realistic capacity factor derating
    capacity_factor = 0.25 if wind_speed < 6 else 0.35 if wind_speed < 8 else 0.40
    annual_kwh_realistic = annual_kwh_max * capacity_factor
    
    return {
        "turbine_size_kw": turbine_size_kw,
        "rotor_diameter_m": round(rotor_diameter, 1),
        "swept_area_m2": round(swept_area, 1),
        "annual_output_kwh": round(annual_kwh_realistic, 0),
        "capacity_factor": round(capacity_factor * 100, 1),
        "note": "Rough estimate only - not for engineering design",
    }
