from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import joblib
import traceback
app = FastAPI(title="Dynamic Pricing API", version="1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
MODEL_PATH = "optimized_gradient_boost_model.pkl"
# Load trained pipeline
try:
    model = joblib.load(MODEL_PATH)
    print(f" Model loaded successfully from {MODEL_PATH}")
except Exception as e:
    model = None
    print(f" Failed to load model: {e}")
# Request body schema
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
CATEGORIES = {
    "Time_of_Booking": ["Morning", "Afternoon", "Evening", "Night"],
    "Customer_Loyalty_Status": ["Gold", "Silver", "Regular"],
    "Location_Category": ["Urban", "Suburban", "Rural"],
    "Vehicle_Type": ["Economy", "Premium"],
}
@app.get("/health")
def health_check():
    return {"ok": model is not None}
@app.get("/categories")
def get_categories():
    return CATEGORIES
@app.post("/recommend")
def recommend(record: Record):
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")
        try:
        # Convert input to DataFrame
        input_df = pd.DataFrame([record.dict()])
        # The model was trained without 'competitor_price'
        model_input = input_df.drop(columns=["competitor_price"])
        # Predict normalized price from pipeline
        predicted_norm = model.predict(model_input)[0]
        # Calculate recommended price
        base_price = record.competitor_price
        hist_cost = record.Expected_Ride_Duration
        price_recommended = (base_price + hist_cost) / 2 + (predicted_norm * 10)
        return {
            "price_recommended": round(price_recommended, 2),
            "predicted_normalized": float(round(predicted_norm, 4)),
            "bounds": {"low": base_price * 0.9, "high": base_price * 1.1},
            "categories": CATEGORIES,
        }
except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
