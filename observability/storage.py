"""
Observability Storage - Stores and retrieves observability data
"""

import json
import os
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import threading


class ObservabilityStorage:
    """
    In-memory and file-based storage for observability data
    
    Stores:
    - Request metrics
    - AI analysis results
    - Drift detection results
    """
    
    def __init__(self, storage_dir: str = "observability_data"):
        """
        Initialize storage
        
        Args:
            storage_dir: Directory to store observability data files
        """
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # In-memory caches
        self.recent_metrics: List[Dict[str, Any]] = []
        self.recent_analyses: List[Dict[str, Any]] = []
        self.drift_history: List[Dict[str, Any]] = []
        
        # Thread lock for concurrent access
        self.lock = threading.Lock()
        
        # Load recent data from disk
        self._load_recent_data()
    
    def _sanitize_numpy_types(self, obj: Any) -> Any:
        """
        Recursively convert numpy types to native Python types for JSON serialization
        
        Args:
            obj: Object that may contain numpy types
            
        Returns:
            Object with all numpy types converted to native Python types
        """
        if isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self._sanitize_numpy_types(value) for key, value in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [self._sanitize_numpy_types(item) for item in obj]
        else:
            return obj
    
    def _get_date_filename(self, date: datetime = None) -> str:
        """Get filename for a specific date"""
        if date is None:
            date = datetime.utcnow()
        return f"metrics_{date.strftime('%Y%m%d')}.jsonl"
    
    def _load_recent_data(self) -> None:
        """Load recent data from disk into memory"""
        # Load last 7 days of data
        for days_ago in range(7):
            date = datetime.utcnow() - timedelta(days=days_ago)
            filepath = self.storage_dir / self._get_date_filename(date)
            
            if filepath.exists():
                try:
                    with open(filepath, 'r') as f:
                        for line in f:
                            if line.strip():
                                data = json.loads(line)
                                if data.get("type") == "request_metrics":
                                    self.recent_metrics.append(data["data"])
                                elif data.get("type") == "ai_analysis":
                                    self.recent_analyses.append(data["data"])
                                elif data.get("type") == "drift_analysis":
                                    self.drift_history.append(data["data"])
                except Exception as e:
                    print(f"Warning: Could not load {filepath}: {e}")
        
        # Keep only last 100 entries in memory
        self.recent_metrics = self.recent_metrics[-100:]
        self.recent_analyses = self.recent_analyses[-100:]
        self.drift_history = self.drift_history[-50:]
    
    def store_request_metrics(self, metrics: Dict[str, Any]) -> None:
        """Store request metrics"""
        with self.lock:
            # Sanitize numpy types before storing
            sanitized_metrics = self._sanitize_numpy_types(metrics)
            self.recent_metrics.append(sanitized_metrics)
            
            # Keep only last 100 in memory
            if len(self.recent_metrics) > 100:
                self.recent_metrics.pop(0)
            
            # Append to file
            self._append_to_file({
                "type": "request_metrics",
                "timestamp": datetime.utcnow().isoformat(),
                "data": sanitized_metrics
            })
    
    def store_ai_analysis(self, request_id: str, analysis: Dict[str, Any]) -> None:
        """Store AI analysis results"""
        with self.lock:
            analysis_data = {
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": analysis
            }
            
            # Sanitize numpy types before storing
            sanitized_data = self._sanitize_numpy_types(analysis_data)
            self.recent_analyses.append(sanitized_data)
            
            if len(self.recent_analyses) > 100:
                self.recent_analyses.pop(0)
            
            self._append_to_file({
                "type": "ai_analysis",
                "timestamp": datetime.utcnow().isoformat(),
                "data": sanitized_data
            })
    
    def store_drift_analysis(self, drift_analysis: Dict[str, Any]) -> None:
        """Store drift detection results"""
        with self.lock:
            drift_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "analysis": drift_analysis
            }
            
            # Sanitize numpy types before storing
            sanitized_data = self._sanitize_numpy_types(drift_data)
            self.drift_history.append(sanitized_data)
            
            if len(self.drift_history) > 50:
                self.drift_history.pop(0)
            
            self._append_to_file({
                "type": "drift_analysis",
                "timestamp": datetime.utcnow().isoformat(),
                "data": sanitized_data
            })
    
    def _append_to_file(self, data: Dict[str, Any]) -> None:
        """Append data to today's file"""
        filepath = self.storage_dir / self._get_date_filename()
        
        try:
            # Sanitize numpy types before JSON serialization
            sanitized_data = self._sanitize_numpy_types(data)
            with open(filepath, 'a') as f:
                f.write(json.dumps(sanitized_data) + '\n')
        except Exception as e:
            print(f"Warning: Could not write to {filepath}: {e}")
    
    def get_recent_metrics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent request metrics"""
        with self.lock:
            return self.recent_metrics[-limit:]
    
    def get_recent_analyses(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent AI analyses"""
        with self.lock:
            return self.recent_analyses[-limit:]
    
    def get_drift_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get drift detection history"""
        with self.lock:
            return self.drift_history[-limit:]
    
    def get_metrics_by_request_id(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific request"""
        with self.lock:
            for metrics in reversed(self.recent_metrics):
                if metrics.get("request_id") == request_id:
                    return metrics
            return None
    
    def get_metrics_summary(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get summary statistics for recent metrics
        
        Args:
            hours: Number of hours to look back
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        with self.lock:
            recent = [
                m for m in self.recent_metrics
                if datetime.fromisoformat(m["timestamp"]) > cutoff_time
            ]
            
            if not recent:
                return {
                    "count": 0,
                    "time_period_hours": hours,
                    "message": "No metrics in time period"
                }
            
            total_requests = len(recent)
            successful_requests = sum(1 for m in recent if m.get("success"))
            
            avg_execution_time = sum(m.get("total_execution_time_ms", 0) for m in recent) / total_requests
            avg_tokens = sum(m.get("total_tokens", 0) for m in recent) / total_requests
            avg_cost = sum(m.get("total_cost_usd", 0) for m in recent) / total_requests
            total_cost = sum(m.get("total_cost_usd", 0) for m in recent)
            
            # Agent statistics
            agent_counts = {}
            for m in recent:
                for agent in m.get("agents_executed", []):
                    agent_counts[agent] = agent_counts.get(agent, 0) + 1
            
            return {
                "count": total_requests,
                "time_period_hours": hours,
                "success_rate": (successful_requests / total_requests) * 100 if total_requests > 0 else 0,
                "avg_execution_time_ms": avg_execution_time,
                "avg_tokens_per_request": avg_tokens,
                "avg_cost_per_request_usd": avg_cost,
                "total_cost_usd": total_cost,
                "most_used_agents": sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)[:5],
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def cleanup_old_files(self, days_to_keep: int = 30) -> int:
        """
        Remove old observability files
        
        Args:
            days_to_keep: Number of days of data to retain
            
        Returns:
            Number of files deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        deleted_count = 0
        
        for filepath in self.storage_dir.glob("metrics_*.jsonl"):
            try:
                # Extract date from filename
                date_str = filepath.stem.replace("metrics_", "")
                file_date = datetime.strptime(date_str, "%Y%m%d")
                
                if file_date < cutoff_date:
                    filepath.unlink()
                    deleted_count += 1
            except Exception as e:
                print(f"Warning: Could not process {filepath}: {e}")
        
        return deleted_count

