"""
FastAPI-based Inference Server for ML Model Deployment

This module provides a RESTful API for model inference using FastAPI.
It supports single predictions, batch predictions, and monitoring endpoints.

Features:
- Async request handling with FastAPI
- Automatic OpenAPI/Swagger documentation
- Prometheus metrics collection
- Health check endpoints
- Comprehensive error handling
- DataFrame input support

Endpoints:
- GET  /health                  - Service health check
- GET  /api/v1/info            - Model and service information
- POST /api/v1/predict         - Single sample prediction
- POST /api/v1/predict_batch   - Batch predictions
- POST /api/v1/predict_dataframe - DataFrame predictions
- GET  /metrics                 - Prometheus metrics

Author: ML Deployment Team
Version: 1.0
"""

import os
import json
import time
import logging
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, Field, validator
from contextlib import asynccontextmanager
import uvicorn

# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge, REGISTRY, CollectorRegistry, CONTENT_TYPE_LATEST
from prometheus_client import generate_latest as prometheus_generate_latest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Prometheus Metrics Definition
# ============================================================================

# Counters (monotonically increasing)
inference_requests_total = Counter(
    'model_inference_requests_total',
    'Total number of inference requests',
    ['status']  # labels: success, error
)

inference_predictions_total = Counter(
    'model_inference_predictions_total',
    'Total number of predictions made',
)

inference_errors_total = Counter(
    'model_inference_errors_total',
    'Total number of inference errors',
    ['error_type']  # labels: validation, runtime, etc.
)

# Histograms (measure request latency)
inference_latency = Histogram(
    'model_inference_latency_seconds',
    'Request latency in seconds',
    buckets=(0.001, 0.01, 0.05, 0.1, 0.25, 0.5, 1.0)
)

# Gauges (current state)
model_loaded = Gauge(
    'model_loaded',
    'Whether model is currently loaded',
)

features_count = Gauge(
    'model_features_count',
    'Number of model features',
)

predictions_per_second = Gauge(
    'model_throughput_per_sec',
    'Current throughput in predictions per second',
)

# Initialize error counter with labels to make them visible in Prometheus
# This ensures the metric exists even with 0 errors
inference_errors_total.labels(error_type='validation')
inference_errors_total.labels(error_type='runtime')


# Global variables
MODEL = None
FEATURE_NAMES = None
MODEL_VERSION = os.getenv('MODEL_VERSION', '1.0')
MODEL_METADATA = {}
STARTUP_TIME = time.time()


# ============================================================================
# Data Models for Request/Response Validation
# ============================================================================
class PredictionRequest(BaseModel):
    """Single sample prediction request."""
    features: List[float] = Field(..., description="Feature values for prediction")
    request_id: Optional[str] = Field(default=None, description="Optional request identifier")
    
    @validator('features')
    def validate_features(cls, v):
        if len(v) == 0:
            raise ValueError("Features list cannot be empty")
        return v


class BatchPredictionRequest(BaseModel):
    """Batch prediction request."""
    features: List[List[float]] = Field(..., description="Batch of feature vectors")
    request_id: Optional[str] = Field(default=None)
    
    @validator('features')
    def validate_batch(cls, v):
        if len(v) == 0:
            raise ValueError("Batch cannot be empty")
        first_len = len(v[0])
        if not all(len(f) == first_len for f in v):
            raise ValueError("All feature vectors must have same length")
        return v


class DataFramePredictionRequest(BaseModel):
    """DataFrame prediction request."""
    data: List[Dict[str, float]] = Field(..., description="Records as dictionaries")
    request_id: Optional[str] = Field(default=None)


class PredictionResponse(BaseModel):
    """Single prediction response."""
    request_id: str
    prediction: float
    status: str
    model_version: str
    timestamp: str


class BatchPredictionResponse(BaseModel):
    """Batch prediction response."""
    request_id: str
    predictions: List[float]
    count: int
    status: str
    model_version: str
    timestamp: str


# ============================================================================
# Model Loading and Setup
# ============================================================================

def load_model_and_features():
    """Load model and feature names at startup."""
    global MODEL, FEATURE_NAMES, MODEL_METADATA
    
    try:
        # Load model from root-level output/modeling folder
        model_path = os.environ.get('MODEL_PATH', '/output/modeling/regression_model.pkl')
        MODEL = joblib.load(model_path)
        logger.info(f"✓ Model loaded from {model_path}")
        
        # Load feature names from root-level output/modeling folder
        features_path = os.environ.get('FEATURES_PATH', '/output/modeling/feature_names.json')
        with open(features_path, 'r') as f:
            FEATURE_NAMES = json.load(f)
        logger.info(f"✓ Features loaded: {len(FEATURE_NAMES)} features")
        
        # Load metadata if available (root-level output/modeling folder)
        metadata_path = os.environ.get('METADATA_PATH', '/output/modeling/model_params.json')
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                MODEL_METADATA = json.load(f)
        
        # Update Prometheus gauges
        model_loaded.set(1)
        features_count.set(len(FEATURE_NAMES))
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        model_loaded.set(0)
        raise


# ============================================================================
# FastAPI Application Lifespan
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info("Starting FastAPI application...")
    load_model_and_features()
    
    if MODEL is not None and FEATURE_NAMES is not None:
        logger.info("✓ Model and features ready for inference")
    else:
        logger.warning("⚠ Model or features not loaded")
    
    yield
    
    # Shutdown
    logger.info("Shutting down FastAPI application...")


# Create FastAPI app
app = FastAPI(
    title="ML Model Inference API",
    description="FastAPI-based inference server for regression model",
    version="1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================================
# Dependency Check
# ============================================================================

async def check_model_loaded():
    """Check if model is loaded."""
    if MODEL is None or FEATURE_NAMES is None:
        raise HTTPException(status_code=503, detail="Model not loaded")


# ============================================================================
# Endpoints
# ============================================================================

@app.get('/health', tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    if MODEL is None or FEATURE_NAMES is None:
        raise HTTPException(status_code=503, detail="Model not ready")
    
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'model_loaded': True,
        'model_version': MODEL_VERSION,
        'features_count': len(FEATURE_NAMES)
    }


@app.get('/api/v1/info', tags=["Information"])
async def model_info() -> Dict[str, Any]:
    """Get model and service information."""
    if MODEL is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    return {
        'model_version': MODEL_VERSION,
        'model_type': type(MODEL).__name__,
        'features': FEATURE_NAMES,
        'features_count': len(FEATURE_NAMES) if FEATURE_NAMES else 0,
        'metadata': MODEL_METADATA,
        'timestamp': datetime.utcnow().isoformat()
    }


@app.post('/api/v1/predict', response_model=PredictionResponse, tags=["Prediction"])
async def predict_single(request: PredictionRequest) -> PredictionResponse:
    """Make single sample prediction."""
    await check_model_loaded()
    
    # Validate feature count
    if len(request.features) != len(FEATURE_NAMES):
        raise HTTPException(
            status_code=400,
            detail=f"Expected {len(FEATURE_NAMES)} features, got {len(request.features)}"
        )
    
    request_id = request.request_id or f"req_{int(time.time() * 1000)}"
    
    try:
        # Make prediction with latency tracking
        with inference_latency.time():
            features_array = np.array(request.features).reshape(1, -1)
            prediction = MODEL.predict(features_array)[0]
        
        # Record metrics
        inference_requests_total.labels(status='success').inc()
        inference_predictions_total.inc()
        
        logger.info(f"Prediction successful - Request: {request_id}, Value: {prediction:.4f}")
        
        return PredictionResponse(
            request_id=request_id,
            prediction=float(prediction),
            status="success",
            model_version=MODEL_VERSION,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        inference_requests_total.labels(status='error').inc()
        inference_errors_total.labels(error_type='runtime').inc()
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@app.post('/api/v1/predict_batch', response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_batch(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """Make batch predictions."""
    await check_model_loaded()
    
    if len(request.features[0]) != len(FEATURE_NAMES):
        raise HTTPException(
            status_code=400,
            detail=f"Expected {len(FEATURE_NAMES)} features per sample"
        )
    
    request_id = request.request_id or f"batch_{int(time.time() * 1000)}"
    
    try:
        with inference_latency.time():
            features_array = np.array(request.features)
            predictions = MODEL.predict(features_array)
        
        # Record metrics
        inference_requests_total.labels(status='success').inc()
        inference_predictions_total.inc(len(predictions))
        
        logger.info(f"Batch prediction successful - Request: {request_id}, Count: {len(predictions)}")
        
        return BatchPredictionResponse(
            request_id=request_id,
            predictions=[float(p) for p in predictions],
            count=len(predictions),
            status="success",
            model_version=MODEL_VERSION,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"Batch prediction failed: {e}")
        inference_requests_total.labels(status='error').inc()
        inference_errors_total.labels(error_type='runtime').inc()
        raise HTTPException(status_code=500, detail=f"Batch prediction failed: {str(e)}")


@app.post('/api/v1/predict_dataframe', response_model=BatchPredictionResponse, tags=["Prediction"])
async def predict_dataframe(request: DataFramePredictionRequest) -> BatchPredictionResponse:
    """Make predictions from DataFrame records."""
    await check_model_loaded()
    
    request_id = request.request_id or f"df_{int(time.time() * 1000)}"
    
    try:
        # Convert to DataFrame
        df = pd.DataFrame(request.data)
        df = df[FEATURE_NAMES]
        
        # Make predictions
        with inference_latency.time():
            predictions = MODEL.predict(df.values)
        
        # Record metrics
        inference_requests_total.labels(status='success').inc()
        inference_predictions_total.inc(len(predictions))
        
        logger.info(f"DataFrame prediction successful - Request: {request_id}, Rows: {len(df)}")
        
        return BatchPredictionResponse(
            request_id=request_id,
            predictions=[float(p) for p in predictions],
            count=len(predictions),
            status="success",
            model_version=MODEL_VERSION,
            timestamp=datetime.utcnow().isoformat()
        )
    
    except Exception as e:
        logger.error(f"DataFrame prediction failed: {e}")
        inference_requests_total.labels(status='error').inc()
        inference_errors_total.labels(error_type='runtime').inc()
        raise HTTPException(status_code=500, detail=f"DataFrame prediction failed: {str(e)}")


@app.get('/metrics', tags=["Monitoring"])
async def get_metrics() -> PlainTextResponse:
    """Get Prometheus-format metrics."""
    return PlainTextResponse(
        prometheus_generate_latest(REGISTRY).decode('utf-8'),
        media_type='text/plain; version=0.0.4'
    )


@app.get('/metrics/json', tags=["Monitoring"])
async def get_metrics_json() -> Dict[str, Any]:
    """Get metrics summary as JSON."""
    uptime_sec = time.time() - STARTUP_TIME
    return {
        'uptime_seconds': round(uptime_sec, 2),
        'model_loaded': bool(MODEL is not None),
        'model_version': MODEL_VERSION,
        'features_count': len(FEATURE_NAMES) if FEATURE_NAMES else 0,
        'timestamp': datetime.utcnow().isoformat()
    }


@app.get('/', tags=["Root"])
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {
        "service": "ML Model Inference API",
        "version": "1.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }


# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors and count them as errors."""
    # Increment error counter for validation errors
    inference_errors_total.labels(error_type='validation').inc()
    
    logger.warning(f"Validation error: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    # Count 400-level errors as validation errors
    if 400 <= exc.status_code < 500:
        inference_errors_total.labels(error_type='validation').inc()
    
    logger.error(f"HTTP error: {exc.status_code} - {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    # Configuration from environment
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    workers = int(os.getenv('API_WORKERS', 1))
    
    logger.info(f"Starting API server on {host}:{port} with {workers} worker(s)")
    logger.info(f"Model path: {os.getenv('MODEL_PATH', '/app/model/regression_model.pkl')}")
    logger.info(f"Features path: {os.getenv('FEATURES_PATH', '/app/model/feature_names.json')}")
    
    # Run server
    uvicorn.run(
        app,
        host=host,
        port=port,
        workers=workers,
        log_level="info"
    )