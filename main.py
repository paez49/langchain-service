"""
Multi-Agent Regulated Substitute Recommender System - REST API
FastAPI service for pharmaceutical substitute recommendations
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime

from services import add_product_to_catalog, bulk_add_products, recommend_substitute
from observability.middleware import get_observability_middleware

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Agent Pharmaceutical Substitute Recommender",
    description="REST API for intelligent pharmaceutical substitute recommendations using multi-agent AI system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


# ============================================================
# REQUEST/RESPONSE MODELS
# ============================================================

class ProductRequest(BaseModel):
    """Request model for adding a single product"""
    product_description: str = Field(..., description="Full product description")
    sku: str = Field(..., description="Stock Keeping Unit identifier")
    atc_code: str = Field(..., description="Anatomical Therapeutic Chemical code")
    cold_chain: bool = Field(default=False, description="Requires cold chain storage")
    shelf_life_months: int = Field(default=24, description="Shelf life in months")

    class Config:
        json_schema_extra = {
            "example": {
                "product_description": "Atorvastatin 20mg - ATC Code: C10AA05 - Lipid-lowering agent - Cold chain: NO - Shelf life: 24 months",
                "sku": "ATOR-20",
                "atc_code": "C10AA05",
                "cold_chain": False,
                "shelf_life_months": 24
            }
        }


class BulkProductRequest(BaseModel):
    """Request model for adding multiple products"""
    products: List[Dict[str, Any]] = Field(..., description="List of products to add")

    class Config:
        json_schema_extra = {
            "example": {
                "products": [
                    {
                        "description": "Metformin 850mg - ATC Code: A10BA02 - Oral antidiabetic",
                        "sku": "METF-850",
                        "atc": "A10BA02",
                        "cold_chain": False,
                        "shelf_life_months": 36
                    }
                ]
            }
        }


class RecommendationRequest(BaseModel):
    """Request model for substitute recommendations"""
    requested_item: str = Field(..., description="Name of the unavailable product")
    country: str = Field(..., description="Destination country code (CO, PE, MX, etc.)")
    quantity: int = Field(default=100, description="Required quantity", ge=1)
    urgency: str = Field(default="medium", description="Urgency level: low, medium, high, or critical")
    enable_observability: bool = Field(default=True, description="Enable observability tracking")
    enable_ai_analysis: bool = Field(default=False, description="Enable AI analysis of outputs (more expensive)")

    class Config:
        json_schema_extra = {
            "example": {
                "requested_item": "Aspirin 500mg for headache",
                "country": "CO",
                "quantity": 200,
                "urgency": "high",
                "enable_observability": True,
                "enable_ai_analysis": False
            }
        }


class ProductResponse(BaseModel):
    """Response model for product operations"""
    success: bool
    message: str
    sku: Optional[str] = None
    product_count: Optional[int] = None


class SubstituteCandidateResponse(BaseModel):
    """Response model for substitute candidate"""
    sku: str
    product_name: str
    warehouse: str
    country: str
    lot: str
    stock: int
    expiry: str
    cost_usd: float
    eta_days: int
    score: float
    compliance_rules: List[str]
    justification: str


class RecommendationResponse(BaseModel):
    """Response model for recommendations"""
    success: bool
    requested_item: str
    country: str
    quantity: int
    urgency: str
    strategy: str
    recommendations: List[SubstituteCandidateResponse]
    suggested_action: str
    final_report: str
    coordinator_synthesis: Optional[str] = None
    observability: Optional[Dict[str, Any]] = None


# ============================================================
# API ENDPOINTS
# ============================================================

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "service": "Multi-Agent Pharmaceutical Substitute Recommender",
        "version": "1.0.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat(),
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "add_product": "POST /api/v1/products",
            "bulk_add_products": "POST /api/v1/products/bulk",
            "get_recommendations": "POST /api/v1/recommendations",
            "observability_summary": "GET /api/v1/observability/summary",
            "observability_metrics": "GET /api/v1/observability/metrics/recent",
            "drift_alerts": "GET /api/v1/observability/drift/alerts"
        },
        "features": {
            "multi_agent_system": True,
            "observability": True,
            "ai_analysis": True,
            "drift_detection": True
        }
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "multi-agent-recommender"
    }


@app.post(
    "/api/v1/products",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Catalog Management"]
)
async def create_product(product: ProductRequest):
    """
    Add a new product to the catalog
    
    This endpoint allows adding pharmaceutical products to the searchable catalog.
    The product will be indexed and available for substitute recommendations.
    """
    try:
        add_product_to_catalog(
            product_description=product.product_description,
            sku=product.sku,
            atc_code=product.atc_code,
            cold_chain=product.cold_chain,
            shelf_life_months=product.shelf_life_months
        )
        
        return ProductResponse(
            success=True,
            message=f"Product {product.sku} successfully added to catalog",
            sku=product.sku
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add product: {str(e)}"
        )

@app.post(
    "/api/v1/recommendations",
    response_model=RecommendationResponse,
    tags=["Recommendations"]
)
async def get_recommendations(request: RecommendationRequest):
    """
    Get substitute product recommendations using multi-agent AI system
    
    This endpoint orchestrates multiple specialized AI agents to:
    - Search the product catalog for similar items
    - Check regulatory compliance for the destination country
    - Verify inventory availability across warehouses
    - Calculate logistics and delivery times
    - Analyze costs and generate optimized recommendations
    
    The system adapts its strategy based on urgency:
    - **high/critical**: Fast strategy (local warehouses only)
    - **medium**: Balanced strategy (regional search)
    - **low**: Exhaustive strategy (global search)
    """
    try:
        # Validate urgency level
        valid_urgency_levels = ["low", "medium", "high", "critical"]
        if request.urgency.lower() not in valid_urgency_levels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid urgency level. Must be one of: {', '.join(valid_urgency_levels)}"
            )
        
        # Call the multi-agent recommendation system
        result = recommend_substitute(
            requested_item=request.requested_item,
            country=request.country,
            quantity=request.quantity,
            urgency=request.urgency.lower(),
            enable_observability=request.enable_observability,
            enable_ai_analysis=request.enable_ai_analysis
        )
        
        # Transform recommendations to response format
        recommendations = [
            SubstituteCandidateResponse(**rec)
            for rec in result.get("recommendations", [])
        ]
        # Ensure observability payload is fully JSON-serializable (handles numpy types, etc.)
        observability_payload = None
        if result.get("observability") is not None:
            observability_payload = jsonable_encoder(result.get("observability"))
        
        return RecommendationResponse(
            success=True,
            requested_item=request.requested_item,
            country=request.country,
            quantity=request.quantity,
            urgency=request.urgency,
            strategy=result.get("strategy", "unknown"),
            recommendations=recommendations,
            suggested_action=result.get("suggested_action", ""),
            final_report=result.get("final_report", ""),
            coordinator_synthesis=result.get("coordinator_synthesis"),
            observability=observability_payload
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation system error: {str(e)}"
        )


# ============================================================
# OBSERVABILITY ENDPOINTS
# ============================================================

@app.get("/api/v1/observability/summary", tags=["Observability"])
async def get_observability_summary(hours: int = 24):
    """
    Get observability metrics summary
    
    Provides aggregated metrics for the specified time period:
    - Request count and success rate
    - Average execution time, tokens, and cost
    - Most used agents
    """
    try:
        observability = get_observability_middleware()
        summary = observability.get_summary(hours=hours)
        return JSONResponse(content=summary)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve observability summary: {str(e)}"
        )


@app.get("/api/v1/observability/metrics/recent", tags=["Observability"])
async def get_recent_metrics(limit: int = 50):
    """
    Get recent request metrics
    
    Returns detailed metrics for recent requests including:
    - Execution times per agent
    - Token usage and costs
    - Success/failure status
    """
    try:
        observability = get_observability_middleware()
        metrics = observability.storage.get_recent_metrics(limit=limit)
        return JSONResponse(content={"count": len(metrics), "metrics": metrics})
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


@app.get("/api/v1/observability/metrics/{request_id}", tags=["Observability"])
async def get_metrics_by_id(request_id: str):
    """
    Get detailed metrics for a specific request
    
    Returns complete observability data including:
    - All agent executions
    - Token counts and costs
    - Execution timeline
    """
    try:
        observability = get_observability_middleware()
        metrics = observability.storage.get_metrics_by_request_id(request_id)
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No metrics found for request ID: {request_id}"
            )
        
        return JSONResponse(content=metrics)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )


@app.get("/api/v1/observability/drift/alerts", tags=["Observability"])
async def get_drift_alerts():
    """
    Get recent drift detection alerts
    
    Returns alerts when AI behavior has drifted from baseline:
    - Drift severity (low, medium, high, critical)
    - Specific indicators of drift
    - Recommendations for action
    """
    try:
        observability = get_observability_middleware()
        alerts = observability.get_recent_drift_alerts()
        return JSONResponse(content={
            "count": len(alerts),
            "alerts": alerts
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve drift alerts: {str(e)}"
        )


@app.get("/api/v1/observability/drift/history", tags=["Observability"])
async def get_drift_history(limit: int = 20):
    """
    Get drift detection history
    
    Returns historical drift analysis results including:
    - Entropy changes over time
    - Kolmogorov-Smirnov test results
    - Statistical summaries
    """
    try:
        observability = get_observability_middleware()
        history = observability.storage.get_drift_history(limit=limit)
        return JSONResponse(content={
            "count": len(history),
            "history": history
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve drift history: {str(e)}"
        )


@app.get("/api/v1/observability/analyses/recent", tags=["Observability"])
async def get_recent_analyses(limit: int = 20):
    """
    Get recent AI analysis results
    
    Returns AI-powered analysis of agent outputs:
    - Text quality scores
    - Reasoning analysis
    - Performance insights
    - Comprehensive reports
    
    Note: Only available for requests with AI analysis enabled
    """
    try:
        observability = get_observability_middleware()
        analyses = observability.storage.get_recent_analyses(limit=limit)
        return JSONResponse(content={
            "count": len(analyses),
            "analyses": analyses
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve analyses: {str(e)}"
        )


@app.post("/api/v1/observability/drift/set-baseline", tags=["Observability"])
async def set_drift_baseline(num_samples: int = 100):
    """
    Manually set drift detection baseline
    
    Uses recent historical data to establish a new baseline for drift detection.
    Useful after system updates or when establishing initial baseline.
    """
    try:
        observability = get_observability_middleware()
        recent_metrics = observability.storage.get_recent_metrics(limit=num_samples)
        
        if len(recent_metrics) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient data for baseline. Need at least 2 samples, have {len(recent_metrics)}"
            )
        
        observability.drift_detector.set_baseline(recent_metrics)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Baseline set using {len(recent_metrics)} samples",
            "samples_used": len(recent_metrics)
        })
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set baseline: {str(e)}"
        )


# ============================================================
# APPLICATION STARTUP
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🚀 STARTING MULTI-AGENT REST API SERVICE")
    print("=" * 80)
    print("Service: Multi-Agent Pharmaceutical Substitute Recommender")
    print("Architecture: Manager Agent + 4 Specialized Agents + Coordinator + Recommendation")
    print("=" * 80)
    print("\n📚 API Documentation available at:")
    print("   • Swagger UI: http://localhost:8000/docs")
    print("   • ReDoc: http://localhost:8000/redoc")
    print("\n🌐 Server starting on: http://localhost:8000")
    print("=" * 80 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
