from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
import pandas as pd
import joblib
import traceback
import logging
import os

# ==========================================================
# LOGGING SETUP
# ==========================================================
logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ==========================================================
# FASTAPI APP INITIALIZATION
# ==========================================================
app = FastAPI(title="Dynamic Pricing API", version="1.0")

# Enable CORS for all origins (frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# MODEL LOADING
# ==========================================================
MODEL_PATH = os.path.join(os.path.dirname(__file__), "optimized_gradient_boost_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "numeric_scaler.pkl")

try:
    model = joblib.load(MODEL_PATH)
    logging.info(f"✅ Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    model = None
    logging.error(f"⚠️ Failed to load model: {e}")

try:
    scaler = joblib.load(SCALER_PATH)
    logging.info(f"✅ Scaler loaded successfully from {SCALER_PATH}")
except Exception as e:
    scaler = None
    logging.warning(f"No scaler loaded, numeric features won't be scaled: {e}")

# ==========================================================
# INPUT SCHEMA (VALIDATION)
# ==========================================================
class Record(BaseModel):
    Number_of_Riders: float
    Number_of_Drivers: float
    Location_Category: str
    Customer_Loyalty_Status: str
    Number_of_Past_Rides: float
    Average_Ratings: float
    Time_of_Booking: str
    Vehicle_Type: str
    Expected_Ride_Duration: float
    competitor_price: float

    @field_validator(
        'Number_of_Riders', 'Number_of_Drivers', 'Number_of_Past_Rides',
        'Average_Ratings', 'Expected_Ride_Duration', 'competitor_price'
    )
    def non_negative(cls, v, info):
        if v < 0:
            raise ValueError(f"{info.field_name} must be non-negative")
        return v

# ==========================================================
# CATEGORY DEFINITIONS
# ==========================================================
CATEGORIES = {
    "Time_of_Booking": ["Morning", "Afternoon", "Evening", "Night"],
    "Customer_Loyalty_Status": ["Gold", "Silver", "Regular"],
    "Location_Category": ["Urban", "Suburban", "Rural"],
    "Vehicle_Type": ["Economy", "Premium"],
}

# ==========================================================
# ROUTES
# ==========================================================
@app.get("/health")
def health_check():
    """Check if model is loaded."""
    return {"ok": model is not None}

@app.get("/categories")
def get_categories():
    """Get dropdown options for frontend."""
    return CATEGORIES

@app.post("/recommend")
def recommend(record: Record, request: Request):
    """Generate a price recommendation."""
    if model is None:
        logging.error("Prediction request failed: model not loaded")
        raise HTTPException(status_code=500, detail="Model not loaded")

    # Validate categorical fields
    for col, allowed in CATEGORIES.items():
        val = getattr(record, col)
        if val not in allowed:
            raise HTTPException(status_code=400, detail=f"Invalid {col}: {val}")

    try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([record.dict()])

        # Scale numeric features if scaler exists
        numeric_cols = [
            'Number_of_Riders', 'Number_of_Drivers',
            'Number_of_Past_Rides', 'Average_Ratings',
            'Expected_Ride_Duration', 'competitor_price'
        ]
        if scaler is not None:
            try:
                input_df[numeric_cols] = scaler.transform(input_df[numeric_cols])
            except Exception as e:
                logging.warning(f"Scaling failed: {e}. Proceeding without scaling.")

        # Predict normalized price
        predicted_norm = model.predict(input_df)[0]

        # Compute recommended price
        base_price = record.competitor_price
        hist_cost = record.Expected_Ride_Duration
        price_recommended = (base_price + hist_cost) / 2 + (predicted_norm * 10)

        logging.info(f"Request from {request.client.host} - Recommended: {price_recommended}")

        return {
            "price_recommended": round(price_recommended, 2),
            "predicted_normalized": float(round(predicted_norm, 4)),
            "bounds": {"low": round(base_price * 0.9, 2), "high": round(base_price * 1.1, 2)},
            "categories": CATEGORIES,
        }

    except Exception as e:
        logging.error(f"Prediction failed: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
