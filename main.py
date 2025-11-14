"""
Multi-Agent Regulated Substitute Recommender System - REST API
FastAPI service for pharmaceutical substitute recommendations
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
from datetime import datetime

from services import add_product_to_catalog, bulk_add_products, recommend_substitute

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

    class Config:
        json_schema_extra = {
            "example": {
                "requested_item": "Aspirin 500mg for headache",
                "country": "CO",
                "quantity": 200,
                "urgency": "high"
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
            "get_recommendations": "POST /api/v1/recommendations"
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
            urgency=request.urgency.lower()
        )
        
        # Transform recommendations to response format
        recommendations = [
            SubstituteCandidateResponse(**rec)
            for rec in result.get("recommendations", [])
        ]
        
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
            coordinator_synthesis=result.get("coordinator_synthesis")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recommendation system error: {str(e)}"
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
