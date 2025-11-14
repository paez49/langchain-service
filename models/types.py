"""
Type Definitions for Multi-Agent System
"""

from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.documents import Document


class SubstituteCandidate(TypedDict):
    """Represents a potential product substitute"""
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


class AgentDecision(TypedDict):
    """Represents a decision made by an agent"""
    agent_name: str
    decision: str
    priority_score: float
    reasoning: str


class State(TypedDict):
    """Global state for multi-agent system"""
    # Input
    requested_item: str
    requested_country: str
    requested_quantity: int
    urgency: str  # "low", "medium", "high", "critical"
    observability_request_id: Optional[str]
    
    # Manager routing
    strategy: Optional[str]  # "fast", "balanced", "exhaustive"
    
    # Parallel agent results
    compliance_result: Optional[Dict[str, Any]]
    inventory_result: Optional[Dict[str, Any]]
    logistics_result: Optional[Dict[str, Any]]
    cost_result: Optional[Dict[str, Any]]
    
    # Processing
    catalog_candidates: List[Document]
    agent_decisions: List[AgentDecision]
    compliant_substitutes: List[SubstituteCandidate]
    
    # Coordination
    coordinator_synthesis: Optional[str]
    
    # Output
    recommendations: List[SubstituteCandidate]
    suggested_action: str
    final_report: Optional[str]

