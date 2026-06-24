from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd

# Load the variables from your hidden .env file into system memory
load_dotenv()

API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
API_KEY_SECRET = os.getenv("API_KEY_SECRET")

if not API_KEY_SECRET:
    raise RuntimeError("CRITICAL ERROR: API_KEY_SECRET environment variable is missing!")

app = FastAPI(
    title="IPO Profitability Prediction API",
    version="1.0.0"
)

async def validate_api_key(api_key: str = Security(api_key_header)):
    if api_key == API_KEY_SECRET:
        return api_key
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid or missing API Key. Access Denied."
        )

model = None
scaler = None

@app.on_event("startup")
def load_artifacts():
    global model, scaler
    try:
        model = joblib.load("best_rf_model.pkl")
        scaler = joblib.load("scaler.pkl")
        print("Machine Learning pipelines loaded successfully.")
    except Exception as e:
        print(f"Failed to load binary components: {str(e)}")

# Define the strict Data Schema using Pydantic
class IPOFeatures(BaseModel):
    issue_size: float = Field(..., alias="Issue_Size(crores)", description="Total value of IPO in crores", example=450.0)
    qib: float = Field(..., alias="QIB", description="Qualified Institutional Buyers subscription multiple", example=55.4)
    hni: float = Field(..., alias="HNI", description="High Net-worth Individuals subscription multiple", example=12.1)
    rii: float = Field(..., alias="RII", description="Retail Individual Investors subscription multiple", example=4.5)
    total: float = Field(..., alias="Total", description="Total aggregate subscription multiplier", example=24.3)
    offer_price: float = Field(..., alias="Offer Price", description="Final listing offer price in INR", example=250.0)

    class Config:
        populate_by_name = True  # Allows parsing raw JSON names matching your dataframe columns

@app.get("/")
def read_root():
    return {"status": "online"}

@app.post("/predict", summary="Compute day-one listing profitability probability")
async def predict_ipo(data: IPOFeatures, api_key: str = Security(validate_api_key)):
    if model is None or scaler is None:
        raise HTTPException(status_code=503, detail="Inference engine inactive: Artifacts missing.")

    try:
        raw_features = np.array([[
            data.issue_size,
            data.qib,
            data.hni,
            data.rii,
            data.total,
            data.offer_price
        ]])

        # Execute transformation mapping pipeline
        scaled_features = scaler.transform(raw_features)

        # Generate predictions and raw structural confidence levels
        prediction = int(model.predict(scaled_features)[0])
        probability = float(model.predict_proba(scaled_features)[0][1])

        # Return clean structured payload response
        return {
            "prediction": prediction,
            "profitable_class_signal": "SUCCESS" if prediction == 1 else "WARNING",
            "profit_probability": round(probability * 100, 2),
            "status_code": 200
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Inference Pipeline Failure: {str(e)}")