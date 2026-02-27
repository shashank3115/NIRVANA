"""
EnerScopeAI — Multi-Renewable Comparison & Ranking Engine
==========================================================
Compares multiple renewable energy sources for a given location and
provides ranked recommendations with decision intelligence.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def rank_renewable_options(
    solar_analysis: Dict[str, Any],
    wind_analysis: Dict[str, Any],
    hydro_analysis: Dict[str, Any] = None,
    location_context: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Compare and rank renewable energy options for a location.
    
    Now supports: Solar, Wind, and Hydro
    
    Returns:
    - ranked_options: List of options sorted by composite viability score
    - best_option: Top recommendation
    - comparison_summary: Plain language comparison
    - diversity_score: Whether mixing sources makes sense
    """
    
    options = []
    
    # ── SOLAR OPTION ───────────────────────────────────────────────────────
    if solar_analysis:
        solar_composite = calculate_composite_viability(
            suitability_score=solar_analysis.get("suitability_score", 0),
            confidence_index=solar_analysis.get("confidence_index", 0),
            payback_years=solar_analysis.get("payback_years", 999),
            recommendation=solar_analysis.get("recommendation", "NO-GO"),
        )
        
        options.append({
            "energy_source": "Solar",
            "emoji": "☀️",
            "suitability_score": solar_analysis.get("suitability_score", 0),
            "confidence_index": solar_analysis.get("confidence_index", 0),
            "recommendation": solar_analysis.get("recommendation", "NO-GO"),
            "composite_viability": solar_composite,
            "payback_years": solar_analysis.get("payback_years", 999),
            "annual_output_kwh": solar_analysis.get("annual_output_kwh", 0),
            "key_strength": identify_key_strength("solar", solar_analysis),
            "key_weakness": identify_key_weakness("solar", solar_analysis),
        })
    
    # ── WIND OPTION ────────────────────────────────────────────────────────
    if wind_analysis:
        wind_composite = calculate_composite_viability(
            suitability_score=wind_analysis.get("suitability_score", 0),
            confidence_index=wind_analysis.get("confidence_index", 0),
            payback_years=wind_analysis.get("payback_years", 999),
            recommendation=wind_analysis.get("recommendation", "NO-GO"),
        )
        
        options.append({
            "energy_source": "Wind",
            "emoji": "💨",
            "suitability_score": wind_analysis.get("suitability_score", 0),
            "confidence_index": wind_analysis.get("confidence_index", 0),
            "recommendation": wind_analysis.get("recommendation", "NO-GO"),
            "composite_viability": wind_composite,
            "payback_years": wind_analysis.get("payback_years", 999),
            "annual_output_kwh": wind_analysis.get("annual_output_kwh", 0),
            "key_strength": identify_key_strength("wind", wind_analysis),
            "key_weakness": identify_key_weakness("wind", wind_analysis),
        })
    
    # ── HYDRO OPTION ───────────────────────────────────────────────────────
    if hydro_analysis:
        hydro_composite = calculate_composite_viability(
            suitability_score=hydro_analysis.get("suitability_score", 0),
            confidence_index=hydro_analysis.get("confidence_index", 0),
            payback_years=hydro_analysis.get("payback_years", 999),
            recommendation=hydro_analysis.get("recommendation", "NO-GO"),
        )
        
        options.append({
            "energy_source": "Hydro",
            "emoji": "💧",
            "suitability_score": hydro_analysis.get("suitability_score", 0),
            "confidence_index": hydro_analysis.get("confidence_index", 0),
            "recommendation": hydro_analysis.get("recommendation", "NO-GO"),
            "composite_viability": hydro_composite,
            "payback_years": hydro_analysis.get("payback_years", 999),
            "annual_output_kwh": hydro_analysis.get("annual_output_kwh", 0),
            "key_strength": identify_key_strength("hydro", hydro_analysis),
            "key_weakness": identify_key_weakness("hydro", hydro_analysis),
        })
    
    # ── RANK OPTIONS ───────────────────────────────────────────────────────
    ranked = sorted(options, key=lambda x: x["composite_viability"], reverse=True)
    
    # ── BEST OPTION ────────────────────────────────────────────────────────
    best = ranked[0] if ranked else None
    
    # ── COMPARISON SUMMARY ─────────────────────────────────────────────────
    comparison = generate_comparison_summary(ranked, location_context)
    
    # ── DIVERSITY ASSESSMENT ───────────────────────────────────────────────
    diversity = assess_hybrid_potential(ranked)
    
    logger.info(
        f"Renewable ranking: {len(ranked)} options analyzed, "
        f"best={best['energy_source'] if best else 'None'} "
        f"(viability={best['composite_viability'] if best else 0})"
    )
    
    return {
        "ranked_options": ranked,
        "best_option": best,
        "comparison_summary": comparison,
        "hybrid_potential": diversity,
        "total_options_analyzed": len(ranked),
    }


def calculate_composite_viability(
    suitability_score: int,
    confidence_index: int,
    payback_years: float,
    recommendation: str,
) -> float:
    """
    Calculate composite viability score (0-100) that balances
    suitability, confidence, and economics.
    
    Formula weighs:
    - Suitability score: 40%
    - Confidence index: 30%
    - Economic viability (from payback): 20%
    - Recommendation (GO/CAUTION/NO-GO): 10%
    """
    
    # Normalize payback to 0-100 score (lower is better)
    if payback_years <= 3:
        economic_score = 100
    elif payback_years <= 5:
        economic_score = 90
    elif payback_years <= 7:
        economic_score = 75
    elif payback_years <= 10:
        economic_score = 55
    elif payback_years <= 15:
        economic_score = 35
    else:
        economic_score = 10
    
    # Recommendation boost/penalty
    rec_multiplier = {
        "GO": 1.0,
        "CAUTION": 0.8,
        "NO-GO": 0.5,
    }.get(recommendation, 0.7)
    
    composite = (
        suitability_score * 0.40 +
        confidence_index * 0.30 +
        economic_score * 0.20 +
        rec_multiplier * 10
    )
    
    return round(composite, 1)


def identify_key_strength(source: str, analysis: Dict[str, Any]) -> str:
    """Identify the strongest aspect of this energy source for this location."""
    
    if source == "solar":
        solar_irr = analysis.get("solar_irradiance", 0)
        if solar_irr > 6.0:
            return "Exceptional solar resource"
        elif solar_irr > 5.0:
            return "Strong solar irradiance"
        elif analysis.get("cloud_cover_pct", 100) < 20:
            return "Low cloud cover"
        elif analysis.get("slope_degrees", 90) < 5:
            return "Ideal terrain"
        else:
            return "Proven technology"
    
    elif source == "wind":
        wind_speed = analysis.get("wind_speed", 0)
        if wind_speed > 8:
            return "Excellent wind resource"
        elif wind_speed > 6.5:
            return "Good wind speeds"
        elif analysis.get("elevation", 0) > 500:
            return "Elevated location benefits"
        else:
            return "24/7 generation potential"
    
    elif source == "hydro":
        head = analysis.get("estimated_head_m", 0)
        flow = analysis.get("estimated_flow_l_s", 0)
        if head > 100 and flow > 10:
            return "Excellent water resource"
        elif head > 50:
            return "Strong elevation gradient"
        elif flow > 15:
            return "Good water flow"
        else:
            return "Stable perennial flow"
    
    return "Viable option"


def identify_key_weakness(source: str, analysis: Dict[str, Any]) -> str:
    """Identify the main limiting factor for this energy source."""
    
    violations = analysis.get("constraint_violations", [])
    if violations:
        return violations[0][:60]  # First constraint, truncated
    
    if source == "solar":
        if analysis.get("cloud_cover_pct", 0) > 60:
            return "High cloud cover"
        elif analysis.get("solar_irradiance", 10) < 4.0:
            return "Limited solar resource"
        elif analysis.get("slope_degrees", 0) > 15:
            return "Steep terrain"
        elif analysis.get("payback_years", 0) > 10:
            return "Long payback period"
    
    elif source == "hydro":
        if analysis.get("water_proximity_km", 0) > 1.0:
            return "Water source too distant"
        elif analysis.get("estimated_head_m", 0) < 10:
            return "Insufficient elevation drop"
        elif analysis.get("seasonality_factor", 1.0) < 0.5:
            return "Seasonal water availability"
        elif analysis.get("payback_years", 0) > 15:
            return "High installation cost"
        else:
            return "None significant"
    
    elif source == "wind":
        if analysis.get("wind_speed", 10) < 5:
            return "Low wind speeds"
        elif analysis.get("slope_degrees", 0) > 15:
            return "Challenging terrain"
        elif analysis.get("payback_years", 0) > 10:
            return "Higher capital cost"
        else:
            return "Needs site validation"
    
    return "Further study needed"


def generate_comparison_summary(
    ranked_options: List[Dict[str, Any]],
    location_context: Dict[str, Any],
) -> str:
    """Generate plain-language comparison of renewable options."""
    
    if not ranked_options:
        return "No viable renewable energy options identified for this location."
    
    best = ranked_options[0]
    
    if len(ranked_options) == 1:
        return (
            f"**{best['energy_source']} {best['emoji']}** is the only renewable option evaluated. "
            f"Suitability: {best['suitability_score']}/100, "
            f"Confidence: {best['confidence_index']}%, "
            f"Recommendation: **{best['recommendation']}**."
        )
    
    # Multi-option comparison
    best_name = best['energy_source']
    best_score = best['suitability_score']
    second = ranked_options[1]
    second_name = second['energy_source']
    second_score = second['suitability_score']
    
    gap = best_score - second_score
    
    if gap > 20:
        clarity = "clearly superior"
    elif gap > 10:
        clarity = "better suited"
    elif gap > 5:
        clarity = "slightly better"
    else:
        clarity = "marginally ahead"
    
    summary = (
        f"**{best_name} {best['emoji']}** is {clarity} for this location "
        f"(suitability {best_score}/100 vs {second_name} {second_score}/100). "
    )
    
    if best['recommendation'] == "GO" and second['recommendation'] in ["CAUTION", "NO-GO"]:
        summary += f"{best_name} receives a **GO** recommendation, while {second_name} is more uncertain. "
    elif best['recommendation'] == second['recommendation']:
        summary += f"Both options receive **{best['recommendation']}** recommendations. "
    
    # Add context about why
    summary += f"\n\n**Why {best_name}?** {best['key_strength']}. "
    
    if second_score >= 50:
        summary += f"\n\n**{second_name} alternative:** {second['key_strength']}, but {second['key_weakness'].lower()}."
    else:
        summary += f"\n\n**{second_name}** is not recommended: {second['key_weakness']}."
    
    return summary


def assess_hybrid_potential(ranked_options: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Assess whether a hybrid renewable system (e.g., solar + wind) makes sense.
    
    Hybrid is beneficial when:
    1. Both sources have moderate-to-good scores
    2. They have complementary generation patterns
    3. Neither dominates overwhelmingly
    """
    
    if len(ranked_options) < 2:
        return {
            "recommended": False,
            "reason": "Only one renewable source evaluated",
            "score": 0,
        }
    
    best = ranked_options[0]
    second = ranked_options[1]
    
    # Check if both are viable
    both_viable = (
        best['suitability_score'] >= 50 and
        second['suitability_score'] >= 50 and
        best['recommendation'] != "NO-GO" and
        second['recommendation'] != "NO-GO"
    )
    
    if not both_viable:
        return {
            "recommended": False,
            "reason": f"{second['energy_source']} suitability too low for hybrid system",
            "score": 0,
        }
    
    # Check gap - if one dominates, hybrid is unnecessary
    score_gap = best['suitability_score'] - second['suitability_score']
    
    if score_gap > 30:
        return {
            "recommended": False,
            "reason": f"{best['energy_source']} clearly superior - hybrid adds complexity without significant benefit",
            "score": 20,
        }
    
    # Calculate hybrid score
    base_score = (best['suitability_score'] + second['suitability_score']) / 2
    balance_bonus = max(0, 20 - score_gap) / 2  # Bonus for balanced scores
    
    hybrid_score = min(100, base_score + balance_bonus)
    
    if hybrid_score >= 70:
        return {
            "recommended": True,
            "reason": f"Both {best['energy_source']} and {second['energy_source']} show good potential. Hybrid system could provide more stable year-round generation.",
            "score": round(hybrid_score, 1),
            "benefit": "Reduced variability, higher capacity factor",
        }
    elif hybrid_score >= 55:
        return {
            "recommended": False,
            "reason": f"Hybrid possible but may not justify added complexity. Focus on {best['energy_source']} first.",
            "score": round(hybrid_score, 1),
        }
    else:
        return {
            "recommended": False,
            "reason": "Hybrid system not recommended - focus on best single source",
            "score": round(hybrid_score, 1),
        }
