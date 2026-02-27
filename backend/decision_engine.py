"""
EnerScopeAI — Decision Confidence & Recommendation Engine
==========================================================
Calculates Decision Confidence Index (DCI) and provides GO/CAUTION/NO-GO
recommendations for renewable energy decisions.

Philosophy: Help users understand HOW CONFIDENT they should be in a
recommendation, not just what the recommendation is.
"""

import logging
import math
from typing import Dict, Any, List, Literal

logger = logging.getLogger(__name__)

RecommendationType = Literal["GO", "CAUTION", "NO-GO"]


def calculate_decision_confidence(
    suitability_score: int,
    constraint_violations: List[str],
    weather_variability_score: float,  # 0-100, higher = more stable
    data_completeness: float,  # 0-100, higher = more complete
    seasonal_stability: float,  # 0-100, higher = more stable across seasons
    economic_viability_score: float,  # 0-100 based on ROI
) -> Dict[str, Any]:
    """
    Calculate Decision Confidence Index (DCI) - a meta-score representing
    how reliable the recommendation is.
    
    DCI considers:
    1. Data quality (completeness, freshness)
    2. Environmental stability (weather variability, seasonal patterns)
    3. Score confidence (is the score in a clear range?)
    4. Economic clarity (is ROI clearly positive or negative?)
    5. Constraint certainty (hard blockers reduce confidence)
    
    Returns:
    - confidence_index: 0-100 percentage
    - confidence_label: Very High / High / Moderate / Low / Very Low
    - confidence_factors: Dict of what affects confidence
    - uncertainty_sources: List of what reduces confidence
    """
    
    uncertainty_sources = []
    confidence_factors = {}
    
    # ── FACTOR 1: Data Completeness (20% weight) ──────────────────────────
    data_factor = data_completeness / 100
    confidence_factors["data_quality"] = round(data_factor * 100, 1)
    
    if data_completeness < 80:
        uncertainty_sources.append(
            f"Limited data availability ({data_completeness:.0f}% complete)"
        )
    
    # ── FACTOR 2: Weather Stability (25% weight) ──────────────────────────
    weather_factor = weather_variability_score / 100
    confidence_factors["weather_stability"] = round(weather_factor * 100, 1)
    
    if weather_variability_score < 60:
        uncertainty_sources.append(
            "High weather variability reducing prediction reliability"
        )
    
    # ── FACTOR 3: Seasonal Stability (15% weight) ─────────────────────────
    seasonal_factor = seasonal_stability / 100
    confidence_factors["seasonal_consistency"] = round(seasonal_factor * 100, 1)
    
    if seasonal_stability < 70:
        uncertainty_sources.append(
            "Significant seasonal variation in energy resource"
        )
    
    # ── FACTOR 4: Score Clarity (25% weight) ──────────────────────────────
    # How clearly is this in a good or bad range?
    # Scores near boundaries (45-55, 70-80) are less confident
    def score_clarity(score: int) -> float:
        """Returns 0-1, higher when score is clearly good or clearly bad."""
        if score >= 80 or score <= 30:
            return 1.0  # Very clear
        elif score >= 70 or score <= 40:
            return 0.85  # Clear
        elif score >= 60 or score <= 50:
            return 0.65  # Moderate
        else:
            return 0.5  # Boundary zone - uncertain
    
    clarity_factor = score_clarity(suitability_score)
    confidence_factors["score_clarity"] = round(clarity_factor * 100, 1)
    
    if 45 <= suitability_score <= 65:
        uncertainty_sources.append(
            "Suitability score in borderline range (moderate uncertainty)"
        )
    
    # ── FACTOR 5: Economic Clarity (15% weight) ───────────────────────────
    economic_factor = economic_viability_score / 100
    confidence_factors["economic_clarity"] = round(economic_factor * 100, 1)
    
    if economic_viability_score < 60:
        uncertainty_sources.append(
            "Economic feasibility unclear or marginal"
        )
    
    # ── CONSTRAINT PENALTY ─────────────────────────────────────────────────
    constraint_penalty = 1.0
    if constraint_violations:
        constraint_penalty = 0.6  # Major confidence reduction
        uncertainty_sources.append(
            f"{len(constraint_violations)} constraint violation(s) detected"
        )
        confidence_factors["constraint_impact"] = "Major negative impact"
    else:
        confidence_factors["constraint_impact"] = "None"
    
    # ── COMPOSITE CONFIDENCE ───────────────────────────────────────────────
    raw_confidence = (
        data_factor * 0.20 +
        weather_factor * 0.25 +
        seasonal_factor * 0.15 +
        clarity_factor * 0.25 +
        economic_factor * 0.15
    ) * constraint_penalty
    
    confidence_index = int(round(raw_confidence * 100))
    confidence_index = max(0, min(100, confidence_index))
    
    # ── CONFIDENCE LABEL ───────────────────────────────────────────────────
    if confidence_index >= 85:
        confidence_label = "Very High"
        emoji = "🟢"
    elif confidence_index >= 70:
        confidence_label = "High"
        emoji = "🟢"
    elif confidence_index >= 55:
        confidence_label = "Moderate"
        emoji = "🟡"
    elif confidence_index >= 40:
        confidence_label = "Low"
        emoji = "🟠"
    else:
        confidence_label = "Very Low"
        emoji = "🔴"
    
    logger.info(
        f"Decision Confidence: {confidence_index}% ({confidence_label}) "
        f"- {len(uncertainty_sources)} uncertainty source(s)"
    )
    
    return {
        "confidence_index": confidence_index,
        "confidence_label": confidence_label,
        "confidence_emoji": emoji,
        "confidence_factors": confidence_factors,
        "uncertainty_sources": uncertainty_sources if uncertainty_sources else ["None - high confidence decision"],
        "reliable_decision": confidence_index >= 60,
    }


def generate_recommendation(
    suitability_score: int,
    confidence_index: int,
    constraint_violations: List[str],
    payback_years: float,
    energy_source: str,
) -> Dict[str, Any]:
    """
    Generate GO / CAUTION / NO-GO recommendation based on suitability,
    confidence, and economic factors.
    
    Logic:
    - NO-GO: Score < 40 OR hard constraints OR very poor ROI
    - CAUTION: Score 40-65 OR low confidence OR marginal ROI
    - GO: Score >= 65 AND no constraints AND reasonable ROI
    
    Returns:
    - recommendation: "GO" | "CAUTION" | "NO-GO"
    - reason: Plain language explanation
    - action_items: What user should do next
    - risk_level: High / Medium / Low
    """
    
    # ── BLOCKING CONDITIONS (NO-GO) ───────────────────────────────────────
    if constraint_violations:
        return {
            "recommendation": "NO-GO",
            "reason": f"{energy_source.title()} energy is not feasible at this location due to critical constraints that cannot be easily overcome.",
            "action_items": [
                "Review constraint violations carefully",
                "Consider alternative renewable energy sources",
                "Evaluate nearby alternative locations",
            ],
            "risk_level": "High",
            "confidence_in_recommendation": min(95, confidence_index + 10),  # High confidence in rejection
        }
    
    if suitability_score < 40:
        return {
            "recommendation": "NO-GO",
            "reason": f"Location shows poor suitability for {energy_source} energy (score {suitability_score}/100). Resource quality is insufficient for economically viable installation.",
            "action_items": [
                f"Explore alternative renewable sources (this location may be better for other options)",
                "Consider energy efficiency improvements instead",
                "Evaluate grid-supplied renewable energy plans",
            ],
            "risk_level": "High",
            "confidence_in_recommendation": confidence_index,
        }
    
    if payback_years > 15:
        return {
            "recommendation": "NO-GO",
            "reason": f"Economic feasibility is very poor (payback period {payback_years:.1f} years exceeds reasonable investment horizon).",
            "action_items": [
                "Wait for technology cost reductions",
                "Investigate subsidy programs",
                "Consider smaller system size",
            ],
            "risk_level": "High",
            "confidence_in_recommendation": confidence_index,
        }
    
    # ── EXCELLENT CONDITIONS (GO) ──────────────────────────────────────────
    if suitability_score >= 75 and confidence_index >= 70 and payback_years <= 5:
        return {
            "recommendation": "GO",
            "reason": f"Excellent {energy_source} potential with high confidence. Strong resource quality and favorable economics make this a low-risk investment.",
            "action_items": [
                "Proceed with detailed site assessment",
                f"Get quotes from qualified {energy_source} installers",
                "Verify local permits and grid connection requirements",
                "Explore financing and subsidy options",
            ],
            "risk_level": "Low",
            "confidence_in_recommendation": confidence_index,
        }
    
    if suitability_score >= 65 and payback_years <= 7:
        return {
            "recommendation": "GO",
            "reason": f"Good {energy_source} potential with reasonable economics. This location is suitable for {energy_source} installation.",
            "action_items": [
                "Get professional site assessment to confirm analysis",
                f"Compare quotes from multiple {energy_source} providers",
                "Review available incentives and financing",
                "Plan for seasonal variation in output",
            ],
            "risk_level": "Low" if confidence_index >= 70 else "Medium",
            "confidence_in_recommendation": confidence_index,
        }
    
    # ── MODERATE CONDITIONS (CAUTION) ──────────────────────────────────────
    if suitability_score >= 55 and payback_years <= 10:
        return {
            "recommendation": "CAUTION",
            "reason": f"Moderate {energy_source} potential. Feasible but with elevated risk. Economics are marginal and/or confidence is limited.",
            "action_items": [
                "Get professional feasibility study before major investment",
                "Consider starting with smaller pilot system",
                "Evaluate risk factors carefully (see Risk section)",
                "Compare multiple renewable options for this location",
                "Model various subsidy and financing scenarios",
            ],
            "risk_level": "Medium",
            "confidence_in_recommendation": confidence_index,
        }
    
    if confidence_index < 50:
        return {
            "recommendation": "CAUTION",
            "reason": f"Decision confidence is low ({confidence_index}%). While {energy_source} shows promise, high uncertainty makes this a risky investment.",
            "action_items": [
                "Gather additional site-specific data",
                "Request professional assessment with measured data",
                "Consider waiting for better data availability",
                "Evaluate less-uncertain renewable alternatives",
            ],
            "risk_level": "Medium",
            "confidence_in_recommendation": confidence_index - 10,  # Lower confidence in marginal case
        }
    
    # ── MARGINAL CONDITIONS (CAUTION or NO-GO) ────────────────────────────
    if suitability_score >= 40:
        return {
            "recommendation": "CAUTION",
            "reason": f"Marginal {energy_source} suitability. Feasibility is questionable. Proceed only with strong justification and professional validation.",
            "action_items": [
                "Mandatory: Get professional feasibility study",
                "Explore alternative renewable sources",
                "Consider hybrid renewable systems",
                "Model conservative economic scenarios",
            ],
            "risk_level": "High",
            "confidence_in_recommendation": confidence_index,
        }
    
    # ── DEFAULT FALLBACK (NO-GO) ──────────────────────────────────────────
    return {
        "recommendation": "NO-GO",
        "reason": f"Location does not meet minimum viability criteria for {energy_source} energy.",
        "action_items": [
            "Consider alternative renewable energy sources",
            "Investigate community renewable programs",
            "Focus on energy efficiency improvements",
        ],
        "risk_level": "High",
        "confidence_in_recommendation": confidence_index,
    }


def explain_confidence(
    confidence_index: int,
    uncertainty_sources: List[str],
    confidence_factors: Dict[str, Any],
) -> str:
    """
    Generate plain-language explanation of what affects decision confidence.
    
    This helps users understand WHY they should or shouldn't trust the recommendation.
    """
    
    if confidence_index >= 80:
        base = "This is a **high-confidence** decision. "
        base += "The data quality is good, environmental conditions are stable, and the suitability is clear. "
        base += "You can proceed with reasonable certainty."
    elif confidence_index >= 60:
        base = "This is a **moderate-confidence** decision. "
        base += "While the analysis is reasonably reliable, some uncertainty factors should be considered. "
        base += "Professional validation is recommended before major investment."
    else:
        base = "This is a **low-confidence** decision. "
        base += "Significant uncertainties exist in the analysis. "
        base += "This recommendation should be treated as preliminary guidance only. "
        base += "Professional site assessment is strongly recommended."
    
    if uncertainty_sources and uncertainty_sources[0] != "None - high confidence decision":
        base += "\n\n**Factors reducing confidence:**\n"
        for source in uncertainty_sources:
            base += f"- {source}\n"
    
    base += f"\n\n**Confidence breakdown:** "
    base += f"Data quality {confidence_factors.get('data_quality', 0):.0f}%, "
    base += f"Weather stability {confidence_factors.get('weather_stability', 0):.0f}%, "
    base += f"Score clarity {confidence_factors.get('score_clarity', 0):.0f}%."
    
    return base
