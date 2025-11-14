"""
Agent Wrapper - Wraps agents with automatic observability tracking
"""

import time
from typing import Callable
from functools import wraps
from models import State
from .middleware import get_observability_middleware


def with_observability(agent_name: str, model_name: str = "us.amazon.nova-micro-v1:0"):
    """
    Decorator to add observability tracking to agents
    
    Usage:
        @with_observability("manager_agent")
        def manager_agent(state: State) -> State:
            ...
    """
    def decorator(func: Callable[[State], State]) -> Callable[[State], State]:
        @wraps(func)
        def wrapper(state: State) -> State:
            # Skip if observability is not enabled for this request
            if not state.get("observability_request_id"):
                return func(state)
            
            try:
                observability = get_observability_middleware()
                
                # Serialize input
                input_parts = []
                for key in ["requested_item", "requested_country", "urgency", "strategy"]:
                    if key in state and state[key]:
                        input_parts.append(f"{key}={state[key]}")
                input_text = ", ".join(input_parts)
                
                # Track execution time
                start_time = time.time()
                
                # Execute agent
                result = func(state)
                
                execution_time = (time.time() - start_time) * 1000
                
                # Serialize output
                output_parts = []
                # Detect what changed or was added
                for key in result:
                    if key not in ["observability_request_id"] and (key not in state or result[key] != state.get(key)):
                        value = result[key]
                        if isinstance(value, str) and len(value) > 200:
                            output_parts.append(f"{key}={value[:200]}...")
                        elif isinstance(value, list):
                            output_parts.append(f"{key}=[{len(value)} items]")
                        elif isinstance(value, dict):
                            output_parts.append(f"{key}={{...}}")
                        else:
                            output_parts.append(f"{key}={value}")
                
                output_text = ", ".join(output_parts) if output_parts else "State updated"
                
                # Track metrics
                observability.metrics_collector.track_agent_execution(
                    agent_name=agent_name,
                    input_text=input_text,
                    output_text=output_text,
                    execution_time_ms=execution_time,
                    model_name=model_name,
                    success=True
                )
                
                return result
                
            except Exception as e:
                # Track failure if observability is active
                try:
                    execution_time = (time.time() - start_time) * 1000
                    observability = get_observability_middleware()
                    observability.metrics_collector.track_agent_execution(
                        agent_name=agent_name,
                        input_text=input_text if 'input_text' in locals() else "Error before input capture",
                        output_text="",
                        execution_time_ms=execution_time,
                        model_name=model_name,
                        success=False,
                        error_message=str(e)
                    )
                except:
                    pass  # Don't fail if observability tracking fails
                
                raise  # Re-raise the original exception
        
        return wrapper
    return decorator

