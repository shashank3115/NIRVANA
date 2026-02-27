"""
EnerScopeAI — Gemini AI Integration
Generates intelligent renewable energy decision recommendations using Google Gemini.
Supports both single-source and multi-renewable comparison analysis.
"""

import os
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


async def generate_summary(
    score: int,
    roi_years: float,
    lat: float,
    lng: float,
    solar_irradiance: Optional[float] = None,
    wind_speed: Optional[float] = None,
    elevation: Optional[float] = None,
    annual_savings: Optional[float] = None,
) -> dict:
    """
    Generate an AI-powered recommendation using Google Gemini.
    Falls back to a template-based response if the API key is not set.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")

    if not api_key:
        logger.info("GEMINI_API_KEY not set — using template-based summary.")
        return {
            "summary": _template_summary(score, roi_years, solar_irradiance, wind_speed, elevation, annual_savings),
            "generated_by": "template",
        }

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        # Try models in order of preference (newest first)
        model_names = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-pro",
        ]

        prompt = _build_prompt(score, roi_years, lat, lng, solar_irradiance, wind_speed, elevation, annual_savings)
        last_err = None

        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                logger.info(f"Gemini response via {model_name}")
                return {
                    "summary": response.text.strip(),
                    "generated_by": model_name,
                }
            except Exception as e:
                last_err = e
                logger.warning(f"Gemini model {model_name} failed: {e}")
                continue

        raise last_err

    except Exception as e:
        logger.error(f"All Gemini models failed: {e}")
        return {
            "summary": _template_summary(score, roi_years, solar_irradiance, wind_speed, elevation, annual_savings),
            "generated_by": "template",
        }


def _build_prompt(
    score: int,
    roi_years: float,
    lat: float,
    lng: float,
    solar_irradiance: Optional[float],
    wind_speed: Optional[float],
    elevation: Optional[float],
    annual_savings: Optional[float],
) -> str:
    details = []
    if solar_irradiance:
        details.append(f"Solar Irradiance: {solar_irradiance} kWh/m²/day")
    if wind_speed:
        details.append(f"Wind Speed: {wind_speed} m/s")
    if elevation:
        details.append(f"Elevation: {elevation} m")
    if annual_savings:
        details.append(f"Estimated Annual Savings: ₹{annual_savings:,.0f}")

    details_str = "\n".join(details) if details else "N/A"

    return f"""You are EnerScopeAI, an expert in renewable energy site evaluation.

Analyze this location and provide a concise (3-4 sentence), professional, and actionable recommendation for renewable energy installation.

Location: {lat:.4f}°N, {lng:.4f}°E
Placement Score: {score}/100
ROI Payback Period: {roi_years} years
{details_str}

Address:
1. Whether this site is suitable for solar, wind, or both.
2. The key factor driving the score (solar, wind, or elevation).
3. Practical advice for maximizing energy yield.
4. Investment outlook.

Keep it concise, insightful, and data-driven."""


def _template_summary(
    score: int,
    roi_years: float,
    solar_irradiance: Optional[float],
    wind_speed: Optional[float],
    elevation: Optional[float],
    annual_savings: Optional[float],
) -> str:
    """Generate a smart template-based summary when Gemini is unavailable."""
    if score >= 80:
        suitability = "an excellent"
        outlook = "The investment outlook is very strong"
    elif score >= 65:
        suitability = "a good"
        outlook = "The investment outlook is favorable"
    elif score >= 50:
        suitability = "a moderate"
        outlook = "The investment outlook is acceptable"
    else:
        suitability = "a below-average"
        outlook = "Consider alternative sites for better returns"

    solar_note = f"with solar irradiance of {solar_irradiance:.1f} kWh/m²/day" if solar_irradiance else ""
    wind_note = f" and wind speed of {wind_speed:.1f} m/s" if wind_speed else ""
    savings_note = f" Estimated annual savings of ₹{annual_savings:,.0f} make this" if annual_savings else " This"

    return (
        f"This location has {suitability} renewable energy potential (score: {score}/100) "
        f"{solar_note}{wind_note}. "
        f"{savings_note} site financially viable with a payback period of approximately {roi_years:.1f} years. "
        f"{outlook}, and installation of solar panels is recommended for optimal energy yield."
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENERSCOPEAI — Decision-Focused Multi-Renewable Summary Generator
# ═══════════════════════════════════════════════════════════════════════════════

async def generate_decision_summary(
    best_option: str,
    solar_data: Dict[str, Any],
    wind_data: Dict[str, Any],
    hydro_data: Optional[Dict[str, Any]],
    lat: float,
    lng: float,
    comparison_summary: str,
) -> dict:
    """
    Generate decision-focused AI summary for multi-renewable comparison.
    
    Focus: Help users DECIDE which renewable energy source to choose,
    not just describe what the data says.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")

    if not api_key:
        logger.info("GEMINI_API_KEY not set — using decision template.")
        return {
            "summary": _template_decision_summary(best_option, solar_data, wind_data, hydro_data, comparison_summary),
            "generated_by": "template",
        }

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model_names = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-pro",
        ]

        prompt = _build_decision_prompt(best_option, solar_data, wind_data, hydro_data, lat, lng, comparison_summary)
        last_err = None

        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                logger.info(f"Gemini decision summary via {model_name}")
                return {
                    "summary": response.text.strip(),
                    "generated_by": model_name,
                }
            except Exception as e:
                last_err = e
                logger.warning(f"Gemini model {model_name} failed: {e}")
                continue

        raise last_err

    except Exception as e:
        logger.error(f"All Gemini models failed: {e}")
        return {
            "summary": _template_decision_summary(best_option, solar_data, wind_data, hydro_data, comparison_summary),
            "generated_by": "template",
        }


def _build_decision_prompt(
    best_option: str,
    solar_data: Dict[str, Any],
    wind_data: Dict[str, Any],
    hydro_data: Optional[Dict[str, Any]],
    lat: float,
    lng: float,
    comparison_summary: str,
) -> str:
    """Build decision-focused prompt for Gemini."""
    
    solar_rec = solar_data.get("recommendation", "UNKNOWN")
    wind_rec = wind_data.get("recommendation", "UNKNOWN")
    solar_conf = solar_data.get("confidence_index", 0)
    wind_conf = wind_data.get("confidence_index", 0)
    solar_score = solar_data.get("suitability_score", 0)
    wind_score = wind_data.get("suitability_score", 0)
    hydro_rec = (hydro_data or {}).get("recommendation", "UNKNOWN")
    hydro_conf = (hydro_data or {}).get("confidence_index", 0)
    hydro_score = (hydro_data or {}).get("suitability_score", 0)

    hydro_block = f"""
HYDRO ANALYSIS:
- Suitability Score: {hydro_score}/100
- Decision Confidence: {hydro_conf}%
- Recommendation: {hydro_rec}
- Payback: {(hydro_data or {}).get('payback_years', 999):.1f} years
- Resource: {(hydro_data or {}).get('estimated_head_m', 0):.1f} m head, {(hydro_data or {}).get('estimated_flow_l_s', 0):.1f} L/s flow
"""
    
    return f"""You are EnerScopeAI, a renewable energy DECISION INTELLIGENCE assistant.

Your job is NOT to describe technical data, but to help users CONFIDENTLY DECIDE which renewable energy source to choose.

Location: {lat:.4f}°N, {lng:.4f}°E

SOLAR ANALYSIS:
- Suitability Score: {solar_score}/100
- Decision Confidence: {solar_conf}%
- Recommendation: {solar_rec}
- Payback: {solar_data.get('payback_years', 999):.1f} years
- Resource: {solar_data.get('solar_irradiance', 0):.1f} kWh/m²/day

WIND ANALYSIS:
- Suitability Score: {wind_score}/100
- Decision Confidence: {wind_conf}%
- Recommendation: {wind_rec}
- Payback: {wind_data.get('payback_years', 999):.1f} years
- Resource: {wind_data.get('wind_speed', 0):.1f} m/s

{hydro_block}

BEST OPTION: {best_option}

COMPARISON: {comparison_summary}

Write a 4-5 sentence decision-focused summary that:
1. Clearly states WHAT the user should do (choose solar, wind, hydro, hybrid, or neither)
2. Explains WHY this is the right decision (2-3 key deciding factors)
3. Addresses confidence: How certain should the user be?
4. Provides ONE actionable next step

Write in plain language. No jargon. Be honest about uncertainty. Focus on DECISIONS, not data.
"""


def _template_decision_summary(
    best_option: str,
    solar_data: Dict[str, Any],
    wind_data: Dict[str, Any],
    hydro_data: Optional[Dict[str, Any]],
    comparison_summary: str,
) -> str:
    """Template-based decision summary when Gemini unavailable."""
    
    solar_rec = solar_data.get("recommendation", "CAUTION")
    wind_rec = wind_data.get("recommendation", "CAUTION")
    hydro_rec = (hydro_data or {}).get("recommendation", "CAUTION")
    solar_conf = solar_data.get("confidence_index", 50)
    wind_conf = wind_data.get("confidence_index", 50)
    hydro_conf = (hydro_data or {}).get("confidence_index", 50)
    
    # Decision statement
    if best_option == "Solar" and solar_rec == "GO":
        decision = "**Recommendation: Proceed with solar energy.** "
        reason = f"Solar shows strong suitability (confidence {solar_conf}%) and favorable economics. "
    elif best_option == "Wind" and wind_rec == "GO":
        decision = "**Recommendation: Proceed with wind energy.** "
        reason = f"Wind resources are sufficient (confidence {wind_conf}%) for viable installation. "
    elif best_option == "Solar" and solar_rec == "CAUTION":
        decision = "**Recommendation: Solar energy with caution.** "
        reason = f"Solar is the best option available, but confidence is moderate ({solar_conf}%). "
    elif best_option == "Wind" and wind_rec == "CAUTION":
        decision = "**Recommendation: Wind energy with caution.** "
        reason = f"Wind shows potential but has elevated uncertainties ({wind_conf}% confidence). "
    elif best_option == "Hydro" and hydro_rec == "GO":
        decision = "**Recommendation: Proceed with micro-hydro energy.** "
        reason = f"Hydro shows strong site potential (confidence {hydro_conf}%) with stable output characteristics. "
    elif best_option == "Hydro" and hydro_rec == "CAUTION":
        decision = "**Recommendation: Micro-hydro with caution.** "
        reason = f"Hydro is the strongest option, but confidence is moderate ({hydro_conf}%). "
    else:
        decision = "**Recommendation: Proceed with caution or consider alternatives.** "
        reason = "No renewable option shows a strong and low-risk advantage at this location. "
    
    # Confidence statement
    if best_option == "Solar":
        best_conf = solar_conf
    elif best_option == "Wind":
        best_conf = wind_conf
    elif best_option == "Hydro":
        best_conf = hydro_conf
    else:
        best_conf = max(solar_conf, wind_conf, hydro_conf)
    if best_conf >= 75:
        conf_stmt = "You can proceed with high confidence in this analysis. "
    elif best_conf >= 60:
        conf_stmt = "Professional validation is recommended to confirm viability. "
    else:
        conf_stmt = "This is a low-confidence decision - site-specific assessment is strongly recommended. "
    
    # Next step
    if solar_rec == "GO" or wind_rec == "GO" or hydro_rec == "GO":
        next_step = "Next step: Get quotes from qualified installers to validate economics."
    elif solar_rec == "CAUTION" or wind_rec == "CAUTION" or hydro_rec == "CAUTION":
        next_step = "Next step: Obtain professional feasibility study with on-site measurements."  
    else:
        next_step = "Next step: Explore alternative locations or energy efficiency improvements."
    
    return decision + reason + comparison_summary + " " + conf_stmt + next_step


async def analyze_renewable_tradeoffs(
    renewable_options: list,
    lat: float,
    lng: float,
) -> dict:
    """
    Generate LLM-powered analysis of trade-offs between renewable energy options.
    
    Addresses SRS requirement FR-20: 'LLM shall describe trade-offs between 
    renewable energy options for the given location.'
    
    Args:
        renewable_options: List of dicts with renewable option details
        lat, lng: Location coordinates
    
    Returns:
        Dict with tradeoff_analysis, generated_by, recommendations
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    if not api_key:
        logger.info("GEMINI_API_KEY not set for tradeoff analysis — using template")
        return {
            "tradeoff_analysis": _template_tradeoff_analysis(renewable_options),
            "generated_by": "template",
            "recommendations": _rank_renewable_options(renewable_options),
        }
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        
        prompt = _build_tradeoff_prompt(renewable_options, lat, lng)
        
        model_names = [
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-flash-latest",
            "gemini-1.5-flash",
            "gemini-pro",
        ]
        
        last_err = None
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(prompt)
                logger.info(f"LLM tradeoff analysis generated via {model_name}")
                
                return {
                    "tradeoff_analysis": response.text.strip(),
                    "generated_by": model_name,
                    "recommendations": _rank_renewable_options(renewable_options),
                }
            except Exception as e:
                last_err = e
                logger.warning(f"Model {model_name} failed for tradeoff analysis: {e}")
                continue
        
        raise last_err
    
    except Exception as e:
        logger.error(f"All LLM models failed for tradeoff analysis: {e}")
        return {
            "tradeoff_analysis": _template_tradeoff_analysis(renewable_options),
            "generated_by": "template",
            "recommendations": _rank_renewable_options(renewable_options),
        }


def _build_tradeoff_prompt(
    renewable_options: list,
    lat: float,
    lng: float,
) -> str:
    """Build prompt for LLM to analyze renewable trade-offs."""
    
    options_text = ""
    for opt in renewable_options:
        options_text += f"""
{opt.get('name', 'Unknown')}:
  - Suitability: {opt.get('score', 0)}/100
  - Confidence: {opt.get('confidence', 0)}%
  - Annual Output: {opt.get('estimated_annual_output', 0):,.0f} kWh
  - Payback Period: {opt.get('payback_years', 999):.1f} years
  - Installation Cost: ${opt.get('installation_cost', 0):,.0f}
  - Pros: {', '.join(opt.get('pros', []))}
  - Cons: {', '.join(opt.get('cons', []))}"""
    
    return f"""You are EnerScopeAI, a renewable energy decision intelligence expert.

Analyze the trade-offs between these renewable energy options for a specific location.

Location: {lat:.4f}°N, {lng:.4f}°E

RENEWABLE ENERGY OPTIONS:{options_text}

TASK:
1. Compare the options directly (e.g., "Solar is cheaper but wind has better confidence")
2. Explain the key trade-offs (cost vs efficiency, payback vs output, etc.)
3. Identify which option offers the best balance of factors
4. Highlight any surprising advantages or disadvantages

Format your response as 3-4 clear paragraphs that non-technical homeowners can understand.
Focus on DECISION-RELEVANT factors, not technical details.
"""


def _template_tradeoff_analysis(renewable_options: list) -> str:
    """Generate template-based trade-off analysis when LLM unavailable."""
    
    if not renewable_options:
        return "No renewable options available for comparison."
    
    # Sort by score
    sorted_opts = sorted(renewable_options, key=lambda x: x.get("score", 0), reverse=True)
    
    best = sorted_opts[0]
    best_name = best.get("name", "Unknown")
    best_score = best.get("score", 0)
    
    analysis = f"**{best_name} emerges as the strongest option** with a suitability score of {best_score}/100. "
    
    if len(sorted_opts) > 1:
        second = sorted_opts[1]
        second_name = second.get("name", "Unknown")
        score_diff = best_score - second.get("score", 0)
        
        analysis += f"This outperforms {second_name} by {score_diff} points in raw suitability. "
        
        # Compare payback
        best_payback = best.get("payback_years", 999)
        second_payback = second.get("payback_years", 999)
        
        if best_payback < second_payback:
            analysis += (
                f"Additionally, {best_name} offers faster financial returns "
                f"({best_payback:.1f} years vs {second_payback:.1f} years for {second_name}). "
            )
        else:
            analysis += (
                f"However, {second_name} has a shorter payback period "
                f"({second_payback:.1f} years vs {best_payback:.1f} years). "
            )
        
        # Compare confidence
        best_conf = best.get("confidence", 0)
        second_conf = second.get("confidence", 0)
        
        if best_conf >= 75:
            analysis += (
                f"The recommendation for {best_name} is backed by high confidence ({best_conf}%), "
                f"making this a strong decision. "
            )
        elif best_conf >= 60:
            analysis += (
                f"While {best_name} leads on score, be aware that the analysis confidence is moderate ({best_conf}%). "
                f"Professional validation is recommended. "
            )
        else:
            analysis += (
                f"Note: The analysis confidence is low ({best_conf}%), so additional site assessment is recommended. "
            )
    else:
        analysis += (
            f"Confidence in this recommendation is {best.get('confidence', 0)}%. "
            f"Payback period is approximately {best.get('payback_years', 999):.1f} years."
        )
    
    return analysis


def _rank_renewable_options(renewable_options: list) -> list:
    """Rank renewable options by composite scoring."""
    
    ranked = []
    for opt in renewable_options:
        # Composite score: 40% suitability, 30% confidence, 20% (inverse) payback, 10% cost efficiency
        score = opt.get("score", 0)
        confidence = opt.get("confidence", 0)
        payback = opt.get("payback_years", 999)
        cost = opt.get("installation_cost", 1)
        output = opt.get("estimated_annual_output", 1)
        
        # Normalize payback (lower is better) - cap at 50 for very high paybacks
        payback_score = 100 - min(50, payback * 2)
        
        # Cost efficiency: output per dollar invested
        cost_efficiency = (output / max(1, cost)) * 1000 if cost > 0 else 0
        cost_efficiency_score = min(100, cost_efficiency / 10)
        
        composite = (
            score * 0.40 +
            confidence * 0.30 +
            payback_score * 0.20 +
            cost_efficiency_score * 0.10
        )
        
        ranked.append({
            "name": opt.get("name", "Unknown"),
            "composite_score": round(composite, 1),
            "suitability_score": score,
            "confidence": confidence,
            "payback_years": opt.get("payback_years", 999),
            "estimated_annual_output": opt.get("estimated_annual_output", 0),
            "installation_cost": opt.get("installation_cost", 0),
        })
    
    # Sort by composite score
    ranked.sort(key=lambda x: x["composite_score"], reverse=True)
    return ranked
