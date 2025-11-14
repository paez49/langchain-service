"""
Observability Middleware - Integrates observability into the agent system
"""

import uuid
import time
import copy
from typing import Dict, Any, Callable, List
from functools import wraps

from .metrics_collector import MetricsCollector
from .ai_analyzer import AIObservabilityAnalyzer
from .drift_detector import DriftDetector
from .storage import ObservabilityStorage


class ObservabilityMiddleware:
    """
    Middleware to automatically track and analyze agent executions
    """
    
    def __init__(
        self, 
        enable_ai_analysis: bool = True,
        enable_cloudwatch: bool = None,
        cloudwatch_region: str = None
    ):
        """
        Initialize observability middleware
        
        Args:
            enable_ai_analysis: Whether to run AI analysis on outputs (more expensive)
            enable_cloudwatch: Enable CloudWatch metrics publishing (defaults to env var)
            cloudwatch_region: AWS region for CloudWatch (defaults to AWS_DEFAULT_REGION)
        """
        self.metrics_collector = MetricsCollector()
        self.ai_analyzer = AIObservabilityAnalyzer() if enable_ai_analysis else None
        self.drift_detector = DriftDetector()
        self.storage = ObservabilityStorage(
            enable_cloudwatch=enable_cloudwatch,
            cloudwatch_region=cloudwatch_region
        )
        
        # Initialize baseline if we have historical data
        recent_metrics = self.storage.get_recent_metrics(limit=100)
        if len(recent_metrics) >= 20:
            self.drift_detector.set_baseline(recent_metrics)
        
        self.enable_ai_analysis = enable_ai_analysis
        self.current_request_id = None
    
    def start_request_tracking(
        self,
        requested_item: str,
        country: str,
        urgency: str
    ) -> str:
        """
        Start tracking a new request
        
        Returns:
            request_id: Unique identifier for this request
        """
        request_id = str(uuid.uuid4())
        self.current_request_id = request_id
        
        self.metrics_collector.start_request(
            request_id=request_id,
            requested_item=requested_item,
            country=country,
            urgency=urgency
        )
        
        return request_id
    
    def track_agent(
        self,
        agent_name: str,
        model_name: str = "bedrock/us.amazon.nova-micro-v1:0"
    ):
        """
        Decorator to track agent execution
        
        Usage:
            @observability.track_agent("manager_agent")
            def my_agent(state):
                ...
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(state, *args, **kwargs):
                # Capture input
                input_text = self._serialize_state(state)
                
                # Track execution time
                start_time = time.time()
                
                try:
                    # Execute agent
                    result = func(state, *args, **kwargs)
                    
                    # Calculate execution time
                    execution_time = (time.time() - start_time) * 1000
                    
                    # Capture output
                    output_text = self._serialize_state(result)
                    
                    # Track metrics
                    self.metrics_collector.track_agent_execution(
                        agent_name=agent_name,
                        input_text=input_text,
                        output_text=output_text,
                        execution_time_ms=execution_time,
                        model_name=model_name,
                        success=True
                    )
                    
                    return result
                    
                except Exception as e:
                    # Track failure
                    execution_time = (time.time() - start_time) * 1000
                    
                    self.metrics_collector.track_agent_execution(
                        agent_name=agent_name,
                        input_text=input_text,
                        output_text="",
                        execution_time_ms=execution_time,
                        model_name=model_name,
                        success=False,
                        error_message=str(e)
                    )
                    
                    raise
            
            return wrapper
        return decorator
    
    def finalize_request(
        self,
        strategy: str,
        recommendations_count: int,
        success: bool = True,
        run_ai_analysis: bool = None
    ) -> Dict[str, Any]:
        """
        Finalize request tracking and perform analysis
        
        Args:
            strategy: Strategy used for recommendations
            recommendations_count: Number of recommendations generated
            success: Whether the request was successful
            run_ai_analysis: Override enable_ai_analysis for this request
            
        Returns:
            Complete observability report
        """
        # Finalize metrics collection
        request_metrics = self.metrics_collector.finalize_request(
            strategy=strategy,
            recommendations_count=recommendations_count,
            success=success
        )
        
        metrics_dict = self.metrics_collector.get_metrics_dict(request_metrics)
        public_metrics = copy.deepcopy(metrics_dict)
        public_metrics.pop("agent_metrics", None)
        
        # Store metrics
        self.storage.store_request_metrics(metrics_dict)
        
        # Perform AI analysis if enabled
        ai_analysis = {}
        if run_ai_analysis is None:
            run_ai_analysis = self.enable_ai_analysis
        elif run_ai_analysis and not self.enable_ai_analysis:
            # Enable AI analysis dynamically for this and future requests
            self.enable_ai_analysis = True
        
        if run_ai_analysis and self.ai_analyzer is None:
            # Lazily initialize the analyzer if it wasn't enabled initially
            self.ai_analyzer = AIObservabilityAnalyzer()
        
        if run_ai_analysis and self.ai_analyzer:
            ai_analysis = self._perform_ai_analysis(metrics_dict)
            self.storage.store_ai_analysis(request_metrics.request_id, ai_analysis)
        
        # Check for drift (after enough requests)
        drift_analysis = {}
        recent_metrics = self.storage.get_recent_metrics(limit=200)
        
        # PoC-friendly: run drift analysis as soon as we have at least 2 requests
        if len(recent_metrics) >= 2:
            # Ensure a baseline exists – if not, initialize it from historical data
            if self.drift_detector.baseline_metrics is None:
                # Use up to the last 100 requests as baseline
                baseline_size = min(len(recent_metrics), 100)
                baseline_metrics = recent_metrics[-baseline_size:]
                self.drift_detector.set_baseline(baseline_metrics)
            
            # Optionally refresh baseline periodically when we have lots of data
            if len(recent_metrics) >= 100 and len(recent_metrics) % 50 == 0:
                baseline_metrics = recent_metrics[-100:-20]
                self.drift_detector.set_baseline(baseline_metrics)
            
            # Detect drift on the most recent window of requests
            recent_window_size = min(len(recent_metrics), 20)
            recent_window = recent_metrics[-recent_window_size:]
            drift_analysis = self.drift_detector.detect_drift(recent_window)
            
            # Persist the drift analysis so the drift endpoints can retrieve it
            self.storage.store_drift_analysis(drift_analysis)
        
        return {
            "request_id": request_metrics.request_id,
            "metrics": public_metrics,
            "ai_analysis": ai_analysis,
            "drift_analysis": drift_analysis
        }
    
    def _perform_ai_analysis(self, metrics_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Perform comprehensive AI analysis"""
        if not self.ai_analyzer:
            return {}
        
        text_quality_results = []
        reasoning_results = []
        
        agent_metrics = metrics_dict.get("agent_metrics", [])
        target_metric = next(
            (am for am in agent_metrics if am.get("agent_name") == "recommendation_agent"),
            None
        )
        
        if not target_metric and agent_metrics:
            # Fallback to the last executed agent if recommendation metrics are missing
            target_metric = agent_metrics[-1]
        
        if target_metric:
            agent_name = target_metric["agent_name"]
            
            if target_metric.get("output_text"):
                quality = self.ai_analyzer.analyze_text_quality(
                    text=target_metric["output_text"],
                    context=f"Agent: {agent_name}"
                )
                quality["agent_name"] = agent_name
                text_quality_results.append(quality)
            
            if target_metric.get("input_text") and target_metric.get("output_text"):
                reasoning = self.ai_analyzer.analyze_reasoning(
                    agent_name=agent_name,
                    input_data=target_metric["input_text"],
                    output_data=target_metric["output_text"]
                )
                reasoning_results.append(reasoning)
        
        # Performance analysis
        performance = self.ai_analyzer.analyze_request_performance(metrics_dict)
        
        # Generate comprehensive report
        report = self.ai_analyzer.generate_comprehensive_report(
            request_metrics=metrics_dict,
            text_quality_results=text_quality_results,
            reasoning_results=reasoning_results,
            performance_analysis=performance
        )
        
        return {
            "text_quality": text_quality_results,
            "reasoning_analysis": reasoning_results,
            "performance_analysis": performance,
            "comprehensive_report": report
        }
    
    def _serialize_state(self, state) -> str:
        """Serialize state object to string for tracking"""
        if isinstance(state, dict):
            # Extract key information from state
            parts = []
            for key in ["requested_item", "requested_country", "urgency", "strategy", 
                       "candidates", "suggested_action", "final_report"]:
                if key in state:
                    value = state[key]
                    if isinstance(value, list):
                        parts.append(f"{key}: {len(value)} items")
                    else:
                        parts.append(f"{key}: {str(value)[:200]}")
            return " | ".join(parts)
        return str(state)[:500]
    
    def get_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get observability summary for recent period"""
        return self.storage.get_metrics_summary(hours=hours)
    
    def get_recent_drift_alerts(self) -> List[Dict[str, Any]]:
        """Get recent drift detection alerts"""
        drift_history = self.storage.get_drift_history(limit=10)
        
        alerts = []
        for entry in drift_history:
            analysis = entry.get("analysis", {})
            if analysis.get("drift_detected"):
                severity = self.drift_detector.get_drift_severity(analysis)
                alerts.append({
                    "timestamp": entry.get("timestamp"),
                    "severity": severity,
                    "indicators": analysis.get("drift_indicators", []),
                    "recommendations": analysis.get("recommendations", [])
                })
        
        return alerts


# Global instance
_observability_instance = None


def get_observability_middleware(
    enable_ai_analysis: bool = True,
    enable_cloudwatch: bool = None,
    cloudwatch_region: str = None
) -> ObservabilityMiddleware:
    """
    Get or create global observability middleware instance
    
    Args:
        enable_ai_analysis: Whether to run AI analysis on outputs
        enable_cloudwatch: Enable CloudWatch metrics publishing
        cloudwatch_region: AWS region for CloudWatch
    """
    global _observability_instance
    
    if _observability_instance is None:
        _observability_instance = ObservabilityMiddleware(
            enable_ai_analysis=enable_ai_analysis,
            enable_cloudwatch=enable_cloudwatch,
            cloudwatch_region=cloudwatch_region
        )
    
    return _observability_instance

