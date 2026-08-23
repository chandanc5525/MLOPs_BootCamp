"""
Pydantic request/response models for the FastAPI service.

WHY: FastAPI uses these to auto-validate incoming JSON (wrong type/missing
field -> automatic 422 error, before our code ever runs) and to generate the
interactive /docs (Swagger UI) page for free.
"""

from pydantic import BaseModel, Field


class AirQualityInput(BaseModel):
    PM2_5: float = Field(..., example=45.2, description="PM2.5 concentration (ug/m3)")
    PM10: float = Field(..., example=70.5, description="PM10 concentration (ug/m3)")
    NO2: float = Field(..., example=18.3, description="NO2 concentration (ppb)")
    SO2: float = Field(..., example=6.1, description="SO2 concentration (ppb)")
    CO: float = Field(..., example=0.8, description="CO concentration (ppm)")
    O3: float = Field(..., example=32.0, description="O3 concentration (ppb)")
    Temperature: float = Field(..., example=27.5, description="Temperature (C)")
    Humidity: float = Field(..., example=60.0, description="Relative humidity (%)")
    WindSpeed: float = Field(..., example=3.2, description="Wind speed (m/s)")

    class Config:
        json_schema_extra = {
            "example": {
                "PM2_5": 45.2,
                "PM10": 70.5,
                "NO2": 18.3,
                "SO2": 6.1,
                "CO": 0.8,
                "O3": 32.0,
                "Temperature": 27.5,
                "Humidity": 60.0,
                "WindSpeed": 3.2,
            }
        }


class PredictionResponse(BaseModel):
    predicted_AQI: float
    model_version: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
