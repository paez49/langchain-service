"""
Metrics Collector - Tracks tokens, costs, response times, and agent execution
"""

import time
import tiktoken
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class AgentMetrics:
    """Metrics for a single agent execution"""
    agent_name: str
    timestamp: str
    execution_time_ms: float
    input_text: str
    output_text: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float
    model_name: str
    success: bool
    error_message: Optional[str] = None


@dataclass
class RequestMetrics:
    """Metrics for a complete request through the system"""
    request_id: str
    timestamp: str
    requested_item: str
    country: str
    urgency: str
    strategy: str
    total_execution_time_ms: float
    total_tokens: int
    total_cost_usd: float
    agents_executed: List[str]
    agent_metrics: List[AgentMetrics]
    final_recommendations_count: int
    success: bool


class MetricsCollector:
    """
    Collects and tracks metrics for AI agent executions
    
    Tracks:
    - Token usage (input/output)
    - Execution times
    - Costs per model
    - Agent-level performance
    """
    
    # Pricing per 1K tokens (as of 2024)
    MODEL_PRICING = {
        "bedrock/us.anthropic.claude-3-5-sonnet-20241022-v2:0": {
            "input": 0.003,  # $3 per 1M tokens
            "output": 0.015  # $15 per 1M tokens
        },
        "bedrock/anthropic.claude-3-sonnet-20240229-v1:0": {
            "input": 0.003,
            "output": 0.015
        },
        "gpt-4": {
            "input": 0.03,
            "output": 0.06
        },
        "gpt-3.5-turbo": {
            "input": 0.0015,
            "output": 0.002
        },
        "us.amazon.nova-micro-v1:0": {
            "input": 0.00003,
            "output": 0.00007
        }
    }
    
    def __init__(self):
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.current_request_metrics: Optional[Dict[str, Any]] = None
        self.agent_metrics_list: List[AgentMetrics] = []
        
    def start_request(self, request_id: str, requested_item: str, country: str, urgency: str) -> None:
        """Start tracking a new request"""
        self.current_request_metrics = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "requested_item": requested_item,
            "country": country,
            "urgency": urgency,
            "start_time": time.time(),
            "agents_executed": [],
            "agent_metrics": []
        }
        self.agent_metrics_list = []
        
    def count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken"""
        if not text:
            return 0
        try:
            return len(self.encoder.encode(text))
        except Exception:
            # Fallback to approximate counting
            return len(text) // 4
    
    def calculate_cost(self, input_tokens: int, output_tokens: int, model_name: str) -> float:
        """Calculate estimated cost based on token usage and model"""
        pricing = self.MODEL_PRICING.get(model_name, self.MODEL_PRICING.get("gpt-3.5-turbo"))
        
        input_cost = (input_tokens / 1000) * pricing["input"]
        output_cost = (output_tokens / 1000) * pricing["output"]
        
        return input_cost + output_cost
    
    def track_agent_execution(
        self,
        agent_name: str,
        input_text: str,
        output_text: str,
        execution_time_ms: float,
        model_name: str = "bedrock/us.anthropic.claude-3-5-sonnet-20241022-v2:0",
        success: bool = True,
        error_message: Optional[str] = None
    ) -> AgentMetrics:
        """Track metrics for a single agent execution"""
        
        input_tokens = self.count_tokens(input_text)
        output_tokens = self.count_tokens(output_text)
        total_tokens = input_tokens + output_tokens
        
        cost = self.calculate_cost(input_tokens, output_tokens, model_name)
        
        metrics = AgentMetrics(
            agent_name=agent_name,
            timestamp=datetime.utcnow().isoformat(),
            execution_time_ms=execution_time_ms,
            input_text=input_text[:500],  # Store first 500 chars
            output_text=output_text[:1000],  # Store first 1000 chars
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=cost,
            model_name=model_name,
            success=success,
            error_message=error_message
        )
        
        self.agent_metrics_list.append(metrics)
        
        if self.current_request_metrics:
            self.current_request_metrics["agents_executed"].append(agent_name)
            
        return metrics
    
    def finalize_request(
        self, 
        strategy: str, 
        recommendations_count: int,
        success: bool = True
    ) -> RequestMetrics:
        """Finalize and return metrics for the entire request"""
        
        if not self.current_request_metrics:
            raise ValueError("No active request to finalize")
        
        end_time = time.time()
        total_execution_time = (end_time - self.current_request_metrics["start_time"]) * 1000
        
        total_tokens = sum(m.total_tokens for m in self.agent_metrics_list)
        total_cost = sum(m.estimated_cost_usd for m in self.agent_metrics_list)
        
        request_metrics = RequestMetrics(
            request_id=self.current_request_metrics["request_id"],
            timestamp=self.current_request_metrics["timestamp"],
            requested_item=self.current_request_metrics["requested_item"],
            country=self.current_request_metrics["country"],
            urgency=self.current_request_metrics["urgency"],
            strategy=strategy,
            total_execution_time_ms=total_execution_time,
            total_tokens=total_tokens,
            total_cost_usd=total_cost,
            agents_executed=self.current_request_metrics["agents_executed"],
            agent_metrics=self.agent_metrics_list.copy(),
            final_recommendations_count=recommendations_count,
            success=success
        )
        
        # Reset for next request
        self.current_request_metrics = None
        self.agent_metrics_list = []
        
        return request_metrics
    
    def get_metrics_dict(self, metrics: RequestMetrics) -> Dict[str, Any]:
        """Convert metrics to dictionary format"""
        data = asdict(metrics)
        # Convert agent_metrics to dicts
        data["agent_metrics"] = [asdict(am) for am in metrics.agent_metrics]
        return data

