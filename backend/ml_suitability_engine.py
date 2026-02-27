"""
EnerScopeAI — ML-Based Suitability & Ranking Engine
====================================================
Implements scikit-learn models for renewable energy feasibility prediction
and ranking as specified in SRS requirements.

Models:
- Linear Regression: Energy generation estimation (kWh/year)
- Random Forest: Composite renewable type suitability ranking
- Rule-based geographic filtering: Pre-scoring eligibility
"""

import logging
import json
import numpy as np
from typing import Dict, Any, List, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import joblib
import os

logger = logging.getLogger(__name__)

# ── Pre-trained model paths (will be created/loaded at startup) ────────────────
ML_MODELS_DIR = "/tmp/enerscopeai_models"  # In production, use persistent storage
ENERGY_REGRESSION_MODEL = os.path.join(ML_MODELS_DIR, "energy_regression.pkl")
SUITABILITY_RF_MODEL = os.path.join(ML_MODELS_DIR, "suitability_rf.pkl")
FEATURE_SCALER = os.path.join(ML_MODELS_DIR, "feature_scaler.pkl")


def _ensure_models_directory():
    """Create models directory if it doesn't exist."""
    os.makedirs(ML_MODELS_DIR, exist_ok=True)


def _create_default_energy_regression_model() -> LinearRegression:
    """
    Create and train a basic Linear Regression model for energy generation.
    
    Features: [solar_irradiance_kwh_m2_day, wind_speed_ms, elevation_m, temp_c, plant_size_kw]
    Target: Annual energy generation (kWh/year)
    
    Coefficients based on physical laws and empirical data:
    - Solar: 365 days × irradiance × plant_size × efficiency (0.18)
    - Wind: Power law scaling with wind speed, plant capacity
    """
    
    # Training data: simulated diverse locations with known outcomes
    X_train = np.array([
        # [solar_irr, wind_speed, elevation, temp, plant_size_kw]
        [5.5, 4.0, 100, 25, 10],      # Good solar, weak wind
        [6.2, 4.5, 150, 22, 10],      # Better solar, moderate wind
        [4.8, 6.5, 300, 15, 10],      # Moderate solar, good wind
        [5.0, 7.5, 400, 12, 10],      # Moderate solar, excellent wind
        [6.8, 3.5, 50, 28, 10],       # Excellent solar, weak wind
        [3.2, 8.5, 800, 10, 10],      # Poor solar, very good wind
        [5.5, 5.0, 200, 20, 10],      # Good solar, moderate wind
        [6.5, 4.2, 120, 26, 10],      # Excellent solar, weak wind
        [4.0, 9.0, 600, 8, 10],       # Poor solar, exceptional wind
        [5.8, 6.0, 250, 18, 10],      # Good solar, good wind (hybrid potential)
    ])
    
    # Annual energy generation (kWh/year) - estimated for 10 kW system
    # Solar: ~1600 kWh/m²/year × plant_size_kw × 0.18 efficiency ≈ 2880 kWh per kW per year
    # Wind: Varies greatly with wind speed (cubic relationship)
    y_train = np.array([
        32100,   # 5.5 solar, weak wind
        36200,   # 6.2 solar, moderate wind
        27500,   # Moderate solar, good wind
        32000,   # Moderate solar, excellent wind
        40500,   # Excellent solar, weak wind
        21000,   # Poor solar, very good wind (wind cubic effect)
        33500,   # Good solar, moderate wind
        39200,   # Excellent solar, weak wind
        24600,   # Poor solar, exceptional wind
        38500,   # Good solar, good wind (hybrid)
    ])
    
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    logger.info(f"Created Linear Regression model with coefficients: {model.coef_}")
    logger.info(f"Intercept: {model.intercept_}")
    
    return model


def _create_default_random_forest_model() -> Tuple[RandomForestRegressor, StandardScaler]:
    """
    Create and train Random Forest model for renewable suitability ranking.
    
    Features: [solar_irr, wind_speed, rainfall, elevation, lat, vegetation_ndvi, 
               water_proximity_km, population_density, slope, temperature]
    Target: Composite suitability score (0-100) per renewable type
    
    Random Forest captures non-linear feature interactions better than linear models
    for multi-renewable decision making.
    """
    
    # Training features (10 locations, 10 environmental features each)
    X_train = np.array([
        # [solar_irr, wind_sp, rainfall, elevation, lat, ndvi, water_prox, pop_density, slope, temp]
        [6.5, 4.5, 800, 200, 28.5, 0.45, 5.0, 150, 8, 25],      # Rainforest - good solar
        [5.8, 6.2, 600, 500, 35.0, 0.35, 2.0, 80, 12, 18],       # Mountain - wind/solar mixed
        [7.2, 3.2, 400, 50, 20.0, 0.25, 15.0, 300, 2, 28],       # Desert - excellent solar
        [4.5, 8.5, 900, 1000, 45.0, 0.55, 8.0, 60, 18, 8],       # Windy plateau - wind focus
        [6.0, 5.5, 700, 300, 32.0, 0.40, 3.0, 120, 10, 22],      # Mixed temperate
        [5.2, 7.0, 750, 600, 40.0, 0.48, 4.0, 70, 14, 12],       # Windy terrain
        [7.0, 4.0, 500, 100, 22.0, 0.30, 10.0, 250, 5, 26],      # Sunny semi-arid
        [5.5, 6.8, 850, 800, 38.0, 0.50, 6.0, 90, 16, 10],       # Rainy wind region
        [6.8, 3.8, 600, 200, 25.0, 0.38, 12.0, 180, 7, 24],      # Coastal tropical
        [5.0, 7.5, 900, 400, 42.0, 0.52, 5.0, 75, 15, 11],       # Alpine wind
    ])
    
    # Target: suitability scores for different renewables (0-100)
    # Format: [solar_score, wind_score, hydro_score, biomass_score]
    y_train_solar = np.array([65, 58, 78, 45, 65, 52, 82, 58, 75, 48])
    y_train_wind = np.array([42, 72, 68, 85, 62, 78, 45, 75, 52, 82])
    y_train_hydro = np.array([75, 70, 45, 60, 68, 65, 50, 72, 65, 58])
    y_train_biomass = np.array([58, 65, 72, 55, 62, 68, 48, 70, 60, 65])
    
    # Standardize features for better RF performance
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X_train)
    
    # Train separate RF for each renewable type
    rf_solar = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)
    rf_wind = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)
    rf_hydro = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)
    rf_biomass = RandomForestRegressor(n_estimators=50, max_depth=6, random_state=42)
    
    rf_solar.fit(X_scaled, y_train_solar)
    rf_wind.fit(X_scaled, y_train_wind)
    rf_hydro.fit(X_scaled, y_train_hydro)
    rf_biomass.fit(X_scaled, y_train_biomass)
    
    # Combine into ensemble
    models = {
        "solar": rf_solar,
        "wind": rf_wind,
        "hydro": rf_hydro,
        "biomass": rf_biomass,
    }
    
    logger.info("Created Random Forest ensemble for renewable suitability ranking")
    logger.info(f"Feature importance (Wind RF): {rf_wind.feature_importances_}")
    
    return models, scaler


def _get_or_create_models():
    """Load models from disk or create defaults if not found."""
    _ensure_models_directory()
    
    # Try to load existing models
    if (os.path.exists(ENERGY_REGRESSION_MODEL) and 
        os.path.exists(SUITABILITY_RF_MODEL) and 
        os.path.exists(FEATURE_SCALER)):
        try:
            energy_model = joblib.load(ENERGY_REGRESSION_MODEL)
            rf_models = joblib.load(SUITABILITY_RF_MODEL)
            scaler = joblib.load(FEATURE_SCALER)
            logger.info("Loaded pre-trained ML models from disk")
            return energy_model, rf_models, scaler
        except Exception as e:
            logger.warning(f"Failed to load models from disk: {e}, creating defaults")
    
    # Create and save default models
    energy_model = _create_default_energy_regression_model()
    rf_models, scaler = _create_default_random_forest_model()
    
    try:
        joblib.dump(energy_model, ENERGY_REGRESSION_MODEL)
        joblib.dump(rf_models, SUITABILITY_RF_MODEL)
        joblib.dump(scaler, FEATURE_SCALER)
        logger.info("Saved trained models to disk")
    except Exception as e:
        logger.warning(f"Could not persist models to disk: {e} (models in memory only)")
    
    return energy_model, rf_models, scaler


# ── Global model instances ────────────────────────────────────────────────────
_energy_model = None
_rf_models = None
_feature_scaler = None


def _ensure_models_loaded():
    """Lazy-load models on first use."""
    global _energy_model, _rf_models, _feature_scaler
    if _energy_model is None:
        _energy_model, _rf_models, _feature_scaler = _get_or_create_models()


# ════════════════════════════════════════════════════════════════════════════════
# PUBLIC API
# ════════════════════════════════════════════════════════════════════════════════


def predict_energy_generation(
    renewable_type: str,
    solar_irradiance_kwh: float,
    wind_speed_ms: float,
    elevation_m: float,
    temperature_c: float,
    plant_size_kw: float,
) -> float:
    """
    Predict annual energy generation using Linear Regression.
    
    Args:
        renewable_type: 'solar' or 'wind'
        solar_irradiance_kwh: kWh/m²/day
        wind_speed_ms: m/s average annual
        elevation_m: meters above sea level
        temperature_c: °C average annual
        plant_size_kw: System capacity in kW
    
    Returns:
        Estimated annual energy generation (kWh/year)
    """
    _ensure_models_loaded()
    
    # Feature vector: [solar_irr, wind_speed, elevation, temp, plant_size]
    features = np.array([[
        solar_irradiance_kwh,
        wind_speed_ms,
        elevation_m,
        temperature_c,
        plant_size_kw,
    ]])
    
    predicted_kwh = _energy_model.predict(features)[0]
    
    # Ensure positive output
    predicted_kwh = max(0, predicted_kwh)
    
    logger.info(
        f"ML Energy Prediction ({renewable_type}): {predicted_kwh:.0f} kWh/year "
        f"for {plant_size_kw} kW system"
    )
    
    return float(predicted_kwh)


def predict_renewable_suitability(
    solar_irradiance: float,
    wind_speed: float,
    rainfall_mm: float,
    elevation_m: float,
    latitude: float,
    vegetation_ndvi: float,  # -1 to 1, where 0.4+ is vegetated
    water_proximity_km: float,
    population_density: float,  # people per km²
    slope_degrees: float,
    temperature_c: float,
) -> Dict[str, float]:
    """
    Predict suitability scores for all renewable types using Random Forest.
    
    Features (10 total):
    1. Solar irradiance (kWh/m²/day)
    2. Wind speed (m/s)
    3. Rainfall (mm/year)
    4. Elevation (m)
    5. Latitude (degrees)
    6. Vegetation NDVI (0 to 1)
    7. Water proximity (km to nearest water)
    8. Population density (people/km²)
    9. Slope (degrees)
    10. Temperature (°C)
    
    Returns:
        Dict with suitability scores (0-100) for:
        - solar: Solar PV suitability
        - wind: Micro-wind suitability
        - hydro: Micro-hydro suitability
        - biomass: Biomass suitability
    """
    _ensure_models_loaded()
    
    # Feature vector - 10 features for RF input
    X = np.array([[
        solar_irradiance,
        wind_speed,
        rainfall_mm,
        elevation_m,
        latitude,
        vegetation_ndvi,
        water_proximity_km,
        population_density,
        slope_degrees,
        temperature_c,
    ]])
    
    # Scale features
    X_scaled = _feature_scaler.transform(X)
    
    # Get predictions from each RF model
    scores = {}
    for renewable_type, model in _rf_models.items():
        pred = model.predict(X_scaled)[0]
        # Clamp to 0-100 range
        score = max(0, min(100, pred))
        scores[renewable_type] = float(round(score, 1))
    
    logger.info(f"ML Renewable Suitability Predictions: {scores}")
    
    return scores


def get_feature_importance() -> Dict[str, Any]:
    """
    Return feature importance from the Random Forest models.
    Useful for understanding what factors drive renewable suitability.
    """
    _ensure_models_loaded()
    
    feature_names = [
        "solar_irradiance",
        "wind_speed",
        "rainfall",
        "elevation",
        "latitude",
        "vegetation_ndvi",
        "water_proximity",
        "population_density",
        "slope",
        "temperature",
    ]
    
    importances_by_type = {}
    for renewable_type, model in _rf_models.items():
        importances = model.feature_importances_
        importance_dict = {
            name: float(round(importance, 4))
            for name, importance in zip(feature_names, importances)
        }
        importances_by_type[renewable_type] = importance_dict
    
    return importances_by_type


def explain_ml_prediction(
    renewable_type: str,
    predicted_score: float,
    feature_values: Dict[str, float],
) -> str:
    """
    Generate a human-readable explanation of ML predictions.
    
    Describes which features most strongly influenced the score.
    """
    importance = get_feature_importance()
    type_importance = importance.get(renewable_type, {})
    
    # Get top 3 most important features
    top_features = sorted(
        type_importance.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:3]
    
    explanation = (
        f"The {renewable_type} suitability score of {predicted_score:.0f}/100 "
        f"is primarily influenced by: "
    )
    
    factors = []
    for feature_name, importance_weight in top_features:
        if feature_name in feature_values:
            value = feature_values[feature_name]
            factors.append(f"{feature_name.replace('_', ' ')} ({value:.1f})")
    
    explanation += ", ".join(factors) + "."
    
    return explanation
