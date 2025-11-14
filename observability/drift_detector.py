"""
Drift Detector - Detects changes in AI behavior using entropy and statistical tests
"""

import numpy as np
from typing import List, Dict, Any, Optional
from collections import Counter
from scipy import stats
from datetime import datetime, timedelta
import math


class DriftDetector:
    """
    Detects drift in AI agent behavior using:
    - Entropy analysis (Shannon entropy)
    - Kolmogorov-Smirnov test
    - Statistical distribution analysis
    """
    
    def __init__(self, window_size: int = 50):
        """
        Initialize drift detector
        
        Args:
            window_size: Number of recent samples to compare against baseline
        """
        self.window_size = window_size
        self.baseline_metrics: Optional[Dict[str, List[float]]] = None
        self.baseline_text_samples: List[str] = []
        
    def set_baseline(self, historical_metrics: List[Dict[str, Any]]) -> None:
        """
        Set baseline from historical metrics
        
        Args:
            historical_metrics: List of historical request metrics
        """
        self.baseline_metrics = {
            "execution_times": [],
            "token_counts": [],
            "costs": [],
            "quality_scores": []
        }
        
        for metric in historical_metrics:
            self.baseline_metrics["execution_times"].append(
                metric.get("total_execution_time_ms", 0)
            )
            self.baseline_metrics["token_counts"].append(
                metric.get("total_tokens", 0)
            )
            self.baseline_metrics["costs"].append(
                metric.get("total_cost_usd", 0)
            )
            
            # Extract text from agent outputs
            for agent_metric in metric.get("agent_metrics", []):
                if agent_metric.get("output_text"):
                    self.baseline_text_samples.append(agent_metric["output_text"])
    
    def calculate_entropy(self, text_samples: List[str]) -> float:
        """
        Calculate Shannon entropy of text patterns
        
        Higher entropy = more diverse/unpredictable outputs
        Lower entropy = more repetitive/predictable outputs
        """
        if not text_samples:
            return 0.0
        
        # Analyze character-level distribution
        all_text = " ".join(text_samples)
        char_counts = Counter(all_text)
        total_chars = len(all_text)
        
        entropy = 0.0
        for count in char_counts.values():
            probability = count / total_chars
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def calculate_word_entropy(self, text_samples: List[str]) -> float:
        """
        Calculate word-level entropy
        """
        if not text_samples:
            return 0.0
        
        # Tokenize into words
        all_words = []
        for text in text_samples:
            words = text.lower().split()
            all_words.extend(words)
        
        if not all_words:
            return 0.0
        
        word_counts = Counter(all_words)
        total_words = len(all_words)
        
        entropy = 0.0
        for count in word_counts.values():
            probability = count / total_words
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def kolmogorov_smirnov_test(
        self,
        baseline_data: List[float],
        current_data: List[float]
    ) -> Dict[str, Any]:
        """
        Perform Kolmogorov-Smirnov test to detect distribution drift
        
        Returns:
            - statistic: KS test statistic (0-1, higher = more different)
            - p_value: probability that distributions are same
            - drift_detected: True if p_value < 0.05
        """
        if len(baseline_data) < 2 or len(current_data) < 2:
            return {
                "statistic": 0.0,
                "p_value": 1.0,
                "drift_detected": False,
                "message": "Insufficient data for KS test"
            }
        
        try:
            # Perform two-sample KS test
            statistic, p_value = stats.ks_2samp(baseline_data, current_data)
            
            # Convert numpy types to native Python types
            statistic = float(statistic)
            p_value = float(p_value)
            drift_detected = bool(p_value < 0.05)  # 95% confidence - convert to native bool
            
            return {
                "statistic": statistic,
                "p_value": p_value,
                "drift_detected": drift_detected,
                "message": "Significant drift detected" if drift_detected else "No significant drift",
                "confidence": "high" if p_value < 0.01 else "medium" if p_value < 0.05 else "low"
            }
        except Exception as e:
            return {
                "statistic": 0.0,
                "p_value": 1.0,
                "drift_detected": False,
                "message": f"KS test error: {str(e)}"
            }
    
    def detect_drift(self, recent_metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect drift by comparing recent metrics to baseline
        
        Returns comprehensive drift analysis
        """
        if not self.baseline_metrics:
            return {
                "drift_detected": False,
                "message": "No baseline set. Call set_baseline() first.",
                "entropy_analysis": {},
                "ks_tests": {},
                "recommendations": []
            }
        
        if not recent_metrics:
            return {
                "drift_detected": False,
                "message": "No recent metrics to analyze",
                "entropy_analysis": {},
                "ks_tests": {},
                "recommendations": []
            }
        
        # Extract recent data
        recent_execution_times = [m.get("total_execution_time_ms", 0) for m in recent_metrics]
        recent_token_counts = [m.get("total_tokens", 0) for m in recent_metrics]
        recent_costs = [m.get("total_cost_usd", 0) for m in recent_metrics]
        
        recent_text_samples = []
        for metric in recent_metrics:
            for agent_metric in metric.get("agent_metrics", []):
                if agent_metric.get("output_text"):
                    recent_text_samples.append(agent_metric["output_text"])
        
        # Entropy Analysis
        baseline_entropy = self.calculate_entropy(self.baseline_text_samples)
        baseline_word_entropy = self.calculate_word_entropy(self.baseline_text_samples)
        
        recent_entropy = self.calculate_entropy(recent_text_samples)
        recent_word_entropy = self.calculate_word_entropy(recent_text_samples)
        
        entropy_change = float(abs(recent_entropy - baseline_entropy) / baseline_entropy) if baseline_entropy > 0 else 0.0
        word_entropy_change = float(abs(recent_word_entropy - baseline_word_entropy) / baseline_word_entropy) if baseline_word_entropy > 0 else 0.0
        
        # KS Tests for numerical metrics
        ks_execution_time = self.kolmogorov_smirnov_test(
            self.baseline_metrics["execution_times"],
            recent_execution_times
        )
        
        ks_tokens = self.kolmogorov_smirnov_test(
            self.baseline_metrics["token_counts"],
            recent_token_counts
        )
        
        ks_costs = self.kolmogorov_smirnov_test(
            self.baseline_metrics["costs"],
            recent_costs
        )
        
        # Overall drift detection
        drift_indicators = []
        
        if entropy_change > 0.15:  # 15% change in entropy
            drift_indicators.append(f"Text entropy changed by {entropy_change*100:.1f}%")
        
        if word_entropy_change > 0.15:
            drift_indicators.append(f"Word entropy changed by {word_entropy_change*100:.1f}%")
        
        if ks_execution_time["drift_detected"]:
            drift_indicators.append("Execution time distribution has drifted")
        
        if ks_tokens["drift_detected"]:
            drift_indicators.append("Token usage distribution has drifted")
        
        if ks_costs["drift_detected"]:
            drift_indicators.append("Cost distribution has drifted")
        
        drift_detected = bool(len(drift_indicators) > 0)
        
        # Generate recommendations
        recommendations = []
        
        if recent_entropy < baseline_entropy * 0.85:
            recommendations.append(
                "⚠️ Output diversity has decreased - AI may be producing more repetitive responses"
            )
        elif recent_entropy > baseline_entropy * 1.15:
            recommendations.append(
                "⚠️ Output diversity has increased - AI may be producing less consistent responses"
            )
        
        if ks_execution_time["drift_detected"]:
            recent_avg = float(np.mean(recent_execution_times))
            baseline_avg = float(np.mean(self.baseline_metrics["execution_times"]))
            if recent_avg > baseline_avg * 1.2:
                recommendations.append(
                    f"⚠️ Performance degradation: Average execution time increased by "
                    f"{((recent_avg/baseline_avg - 1) * 100):.1f}%"
                )
        
        if ks_costs["drift_detected"]:
            recent_avg = float(np.mean(recent_costs))
            baseline_avg = float(np.mean(self.baseline_metrics["costs"]))
            if recent_avg > baseline_avg * 1.2:
                recommendations.append(
                    f"⚠️ Cost increase: Average cost increased by "
                    f"{((recent_avg/baseline_avg - 1) * 100):.1f}%"
                )
        
        return {
            "drift_detected": drift_detected,
            "message": f"Drift detected: {len(drift_indicators)} indicator(s)" if drift_detected else "No significant drift",
            "drift_indicators": drift_indicators,
            "entropy_analysis": {
                "baseline_char_entropy": baseline_entropy,
                "recent_char_entropy": recent_entropy,
                "char_entropy_change_pct": entropy_change * 100,
                "baseline_word_entropy": baseline_word_entropy,
                "recent_word_entropy": recent_word_entropy,
                "word_entropy_change_pct": word_entropy_change * 100
            },
            "ks_tests": {
                "execution_time": ks_execution_time,
                "token_usage": ks_tokens,
                "costs": ks_costs
            },
            "statistical_summary": {
                "baseline_avg_time_ms": float(np.mean(self.baseline_metrics["execution_times"])),
                "recent_avg_time_ms": float(np.mean(recent_execution_times)),
                "baseline_avg_tokens": float(np.mean(self.baseline_metrics["token_counts"])),
                "recent_avg_tokens": float(np.mean(recent_token_counts)),
                "baseline_avg_cost": float(np.mean(self.baseline_metrics["costs"])),
                "recent_avg_cost": float(np.mean(recent_costs))
            },
            "recommendations": recommendations
        }
    
    def get_drift_severity(self, drift_analysis: Dict[str, Any]) -> str:
        """
        Determine severity level of detected drift
        
        Returns: 'none', 'low', 'medium', 'high', 'critical'
        """
        if not drift_analysis.get("drift_detected"):
            return "none"
        
        num_indicators = len(drift_analysis.get("drift_indicators", []))
        
        # Check for critical KS test results
        ks_tests = drift_analysis.get("ks_tests", {})
        critical_ks = sum(
            1 for test in ks_tests.values() 
            if test.get("confidence") == "high" and test.get("drift_detected")
        )
        
        if critical_ks >= 2 or num_indicators >= 4:
            return "critical"
        elif critical_ks == 1 or num_indicators >= 3:
            return "high"
        elif num_indicators >= 2:
            return "medium"
        else:
            return "low"

