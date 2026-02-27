"""
EnerScopeAI — Risk Awareness & Analysis Layer
==============================================
Transparent, conservative risk modeling for renewable energy decisions.
Not engineering-grade, but honest about what could go wrong.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def analyze_risks(
    energy_source: str,
    suitability_score: int,
    confidence_index: int,
    climate_data: Dict[str, Any],
    economic_data: Dict[str, Any],
    location_data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Identify and categorize risks for renewable energy investment.
    
    Risk categories:
    1. Technical/Environmental risks
    2. Economic/Financial risks
    3. Policy/Regulatory risks
    4. Maintenance/Operational risks
    5. Data/Uncertainty risks
    
    Returns:
    - risk_level: High / Medium / Low
    - risk_categories: Dict of category → list of risks
    - mitigation_suggestions: Actionable steps to reduce risk
    - show_stoppers: Critical risks that might prevent project
    """
    
    risks_by_category = {
        "technical": [],
        "economic": [],
        "policy": [],
        "operational": [],
        "uncertainty": [],
    }
    
    show_stoppers = []
    mitigation_suggestions = []
    
    # ── TECHNICAL/ENVIRONMENTAL RISKS ──────────────────────────────────────
    if energy_source.lower() == "solar":
        analyze_solar_technical_risks(
            climate_data, risks_by_category, show_stoppers, mitigation_suggestions
        )
    elif energy_source.lower() == "wind":
        analyze_wind_technical_risks(
            climate_data, risks_by_category, show_stoppers, mitigation_suggestions
        )
    elif energy_source.lower() == "hydro":
        analyze_hydro_technical_risks(
            climate_data, risks_by_category, show_stoppers, mitigation_suggestions
        )
    
    # ── ECONOMIC/FINANCIAL RISKS ───────────────────────────────────────────
    analyze_economic_risks(
        economic_data, risks_by_category, mitigation_suggestions
    )
    
    # ── POLICY/REGULATORY RISKS ────────────────────────────────────────────
    analyze_policy_risks(
        location_data, energy_source, risks_by_category, mitigation_suggestions
    )
    
    # ── OPERATIONAL/MAINTENANCE RISKS ──────────────────────────────────────
    analyze_operational_risks(
        energy_source, climate_data, risks_by_category, mitigation_suggestions
    )
    
    # ── DATA/UNCERTAINTY RISKS ─────────────────────────────────────────────
    analyze_uncertainty_risks(
        confidence_index, risks_by_category, mitigation_suggestions
    )
    
    # ── OVERALL RISK LEVEL ─────────────────────────────────────────────────
    total_risks = sum(len(v) for v in risks_by_category.values())
    
    if show_stoppers or total_risks >= 8:
        risk_level = "High"
        risk_emoji = "🔴"
    elif total_risks >= 4 or confidence_index < 60:
        risk_level = "Medium"
        risk_emoji = "🟡"
    else:
        risk_level = "Low"
        risk_emoji = "🟢"
    
    logger.info(
        f"Risk analysis: {risk_level} ({total_risks} risks identified, "
        f"{len(show_stoppers)} show-stoppers)"
    )
    
    return {
        "risk_level": risk_level,
        "risk_emoji": risk_emoji,
        "total_risks_identified": total_risks,
        "show_stoppers": show_stoppers,
        "risks_by_category": risks_by_category,
        "mitigation_suggestions": mitigation_suggestions,
        "risk_score": calculate_risk_score(risks_by_category, show_stoppers),
    }


def analyze_solar_technical_risks(
    climate_data: Dict[str, Any],
    risks: Dict[str, List[str]],
    show_stoppers: List[str],
    mitigations: List[str],
):
    """Identify solar-specific technical risks."""
    
    solar_irr = climate_data.get("solar_irradiance", 0)
    cloud_pct = climate_data.get("cloud_cover_pct", 0)
    slope = climate_data.get("slope_degrees", 0)
    temp = climate_data.get("temperature_c", 25)
    
    if solar_irr < 3.5:
        show_stoppers.append("Insufficient solar resource for viable system")
    elif solar_irr < 4.5:
        risks["technical"].append("Marginal solar resource - output may be lower than expected")
        mitigations.append("Consider high-efficiency panels to maximize yield")
    
    if cloud_pct > 60:
        risks["technical"].append(f"High cloud cover ({cloud_pct:.0f}%) will reduce actual output vs. rated capacity")
        mitigations.append("Use conservative capacity factor in financial planning (15-20%)")
    
    if slope > 15:
        risks["technical"].append(f"Steep terrain ({slope:.1f}°) increases installation complexity and cost")
        mitigations.append("Budget for specialized mounting and engineering")
    
    if temp > 35:
        risks["technical"].append(f"High ambient temperature ({temp:.1f}°C) reduces panel efficiency")
        mitigations.append("Consider panel cooling or high-temperature-rated panels")
    
    # Weather variability risk (generic solar risk)
    risks["technical"].append("Seasonal and daily variability in solar output")
    mitigations.append("Consider battery storage for load matching")


def analyze_wind_technical_risks(
    climate_data: Dict[str, Any],
    risks: Dict[str, List[str]],
    show_stoppers: List[str],
    mitigations: List[str],
):
    """Identify wind-specific technical risks."""
    
    wind_speed = climate_data.get("wind_speed", 0)
    slope = climate_data.get("slope_degrees", 0)
    elevation = climate_data.get("elevation", 0)
    
    if wind_speed < 4.0:
        show_stoppers.append("Wind speed too low for viable turbine operation")
    elif wind_speed < 5.5:
        risks["technical"].append("Below-optimal wind resource - low capacity factor expected")
        mitigations.append("Consider taller tower to access higher wind speeds")
    
    if wind_speed > 20:
        risks["technical"].append("Very high wind speeds require expensive turbine class")
        mitigations.append("Ensure turbine rated for site wind class")
    
    if slope > 15:
        risks["technical"].append(f"Steep terrain ({slope:.1f}°) complicates turbine installation and foundation")
        mitigations.append("Professional geotechnical assessment required")
    
    if elevation > 2500:
        risks["technical"].append("High elevation may complicate installation and increase extreme weather exposure")
    
    risks["technical"].append("Hub height and actual wind profile unknown from ground-level data")
    mitigations.append("Conduct on-site wind measurement at proposed hub height (critical for accuracy)")
    
    risks["operational"].append("Wind resource varies significantly with height and local terrain")
    mitigations.append("Professional micro-siting study strongly recommended")


def analyze_hydro_technical_risks(
    climate_data: Dict[str, Any],
    risks: Dict[str, List[str]],
    show_stoppers: List[str],
    mitigations: List[str],
):
    """Identify hydro-specific technical risks."""

    rainfall_mm = climate_data.get("rainfall_mm", 0)
    water_proximity_km = climate_data.get("water_proximity_km", 99)
    head_m = climate_data.get("estimated_head_m", 0)
    flow_l_s = climate_data.get("estimated_flow_l_s", 0)

    if water_proximity_km > 2:
        show_stoppers.append("Water source too far for practical micro-hydro development")
    elif water_proximity_km > 1:
        risks["technical"].append("Water source distance increases penstock cost and complexity")
        mitigations.append("Validate penstock route and civil works cost before proceeding")

    if head_m < 5:
        show_stoppers.append("Insufficient hydraulic head for viable micro-hydro output")
    elif head_m < 15:
        risks["technical"].append("Low hydraulic head limits generation capacity")
        mitigations.append("Assess turbine type optimized for low-head applications")

    if flow_l_s < 2:
        show_stoppers.append("Estimated stream flow too low for year-round operation")
    elif flow_l_s < 8:
        risks["technical"].append("Marginal stream flow may reduce annual output")

    if rainfall_mm < 500:
        risks["technical"].append("Low annual rainfall increases seasonal flow uncertainty")
        mitigations.append("Use conservative dry-season flow assumptions in financial model")

    risks["technical"].append("Hydrological estimates are model-based, not measured stream data")
    mitigations.append("Perform on-site flow and head survey before final investment")


def analyze_economic_risks(
    economic_data: Dict[str, Any],
    risks: Dict[str, List[str]],
    mitigations: List[str],
):
    """Identify economic and financial risks."""
    
    payback = economic_data.get("payback_years", 999)
    installation_cost = economic_data.get("installation_cost_inr", 0)
    electricity_rate = economic_data.get("electricity_rate", 8.0)
    
    if payback > 12:
        risks["economic"].append(f"Long payback period ({payback:.1f} years) increases investment risk")
        mitigations.append("Explore subsidies, grants, or financing to improve economics")
    elif payback > 8:
        risks["economic"].append("Moderate payback period - sensitive to cost and price assumptions")
    
    if electricity_rate < 6.0:
        risks["economic"].append(f"Low electricity rate (₹{electricity_rate:.1f}/kWh) reduces savings")
        mitigations.append("Verify actual electricity rates including all charges")
    
    risks["economic"].append("Electricity price changes over 25-year lifetime unpredictable")
    mitigations.append("Model scenarios with ±30% price variation")
    
    risks["economic"].append("Technology costs declining - waiting may improve economics")
    
    if installation_cost > 1000000:
        risks["economic"].append("Large capital requirement increases financial risk")
        mitigations.append("Consider phased installation or smaller initial system")


def analyze_policy_risks(
    location_data: Dict[str, Any],
    energy_source: str,
    risks: Dict[str, List[str]],
    mitigations: List[str],
):
    """Identify policy and regulatory risks."""
    
    lat = location_data.get("lat", 0)
    
    # India-specific (rough lat bounds)
    if 8 <= lat <= 37:
        risks["policy"].append("Subsidy programs (PM Surya Ghar, etc.) subject to change or budget exhaustion")
        mitigations.append("Apply for subsidies early; don't rely on uncertain future programs")
        
        risks["policy"].append("Net metering policies vary by state and may change")
        mitigations.append("Verify current net metering rules with local utility")
    else:
        risks["policy"].append("Local subsidy and net metering policies unknown - verify with authorities")
    
    risks["policy"].append(f"Permitting and grid connection requirements for {energy_source} vary by location")
    mitigations.append("Research local permits and approvals needed before committing")
    
    if energy_source.lower() == "wind":
        risks["policy"].append("Wind turbines may face height restrictions or noise ordinances")
        mitigations.append("Check zoning laws and neighbor proximity before proceeding")


def analyze_operational_risks(
    energy_source: str,
    climate_data: Dict[str, Any],
    risks: Dict[str, List[str]],
    mitigations: List[str],
):
    """Identify operational and maintenance risks."""
    
    if energy_source.lower() == "solar":
        risks["operational"].append("Panel soiling, dust, and bird droppings reduce output 5-15%")
        mitigations.append("Plan for regular cleaning (2-4 times/year in dusty areas)")
        
        risks["operational"].append("Inverter replacement needed 1-2 times over 25-year life (~₹50-100k)")
        mitigations.append("Budget for inverter replacement in year 10-12")
        
        humidity = climate_data.get("humidity_pct", 50)
        if humidity > 80:
            risks["operational"].append("High humidity accelerates component degradation")
    
    elif energy_source.lower() == "wind":
        risks["operational"].append("Small wind turbines have higher failure rates than solar")
        mitigations.append("Choose reputable manufacturer with strong warranty and support")
        
        risks["operational"].append("Moving parts require regular maintenance (annual servicing critical)")
        mitigations.append("Budget ₹20-40k/year for maintenance and parts")
        
        risks["operational"].append("Noise and vibration may cause neighbor complaints")
        mitigations.append("Site turbine away from residences; consider quieter models")

    elif energy_source.lower() == "hydro":
        risks["operational"].append("Seasonal stream variation can reduce generation during dry months")
        mitigations.append("Design around firm dry-season flow, not peak monsoon flow")

        risks["operational"].append("Debris and silt can increase maintenance and turbine wear")
        mitigations.append("Include intake screening and periodic desilting in O&M plan")

        risks["operational"].append("Civil works and waterways require regular inspection")
        mitigations.append("Budget annual civil and intake maintenance")
    
    risks["operational"].append("Performance degrades 0.5-1% per year over system lifetime")


def analyze_uncertainty_risks(
    confidence_index: int,
    risks: Dict[str, List[str]],
    mitigations: List[str],
):
    """Identify risks from data uncertainty."""
    
    if confidence_index < 50:
        risks["uncertainty"].append(f"Low decision confidence ({confidence_index}%) indicates high uncertainty in analysis")
        mitigations.append("Gather site-specific measured data before major investment")
    elif confidence_index < 70:
        risks["uncertainty"].append("Moderate uncertainty in resource estimates")
        mitigations.append("Professional site assessment recommended")
    
    risks["uncertainty"].append("Analysis based on satellite/model data, not site measurements")
    mitigations.append("Consider 1-year on-site monitoring for large projects (>50kW)")
    
    risks["uncertainty"].append("Local microclimate and shading not accounted for")
    mitigations.append("Conduct shade analysis for actual installation site")


def calculate_risk_score(
    risks_by_category: Dict[str, List[str]],
    show_stoppers: List[str],
) -> int:
    """
    Calculate overall risk score 0-100 (higher = more risk).
    Inverse of safety/confidence.
    """
    
    total_risks = sum(len(v) for v in risks_by_category.values())
    
    # Base score from risk count
    base_score = min(70, total_risks * 8)
    
    # Show-stopper penalty
    stopper_penalty = len(show_stoppers) * 20
    
    risk_score = min(100, base_score + stopper_penalty)
    
    return risk_score


def generate_risk_summary(risk_analysis: Dict[str, Any]) -> str:
    """Generate plain-language risk summary for users."""
    
    level = risk_analysis["risk_level"]
    emoji = risk_analysis["risk_emoji"]
    total = risk_analysis["total_risks_identified"]
    show_stoppers = risk_analysis["show_stoppers"]
    
    if level == "High":
        summary = f"{emoji} **HIGH RISK** - {total} risk factors identified. "
        if show_stoppers:
            summary += f"**Critical issues:** {', '.join(show_stoppers)}. "
        summary += "Proceed with extreme caution only after professional validation."
    
    elif level == "Medium":
        summary = f"{emoji} **MODERATE RISK** - {total} risk factors identified. "
        summary += "Manageable risks, but careful planning and professional consultation recommended."
    
    else:  # Low
        summary = f"{emoji} **LOW RISK** - {total} risk factors identified. "
        summary += "Typical risks for renewable energy projects. Proceed with standard due diligence."
    
    # Add top mitigation
    if risk_analysis.get("mitigation_suggestions"):
        summary += f"\n\n**Key mitigation:** {risk_analysis['mitigation_suggestions'][0]}"
    
    return summary
