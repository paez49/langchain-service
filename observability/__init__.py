"""
Observability module for AI agent monitoring and analysis
"""

from .metrics_collector import MetricsCollector
from .ai_analyzer import AIObservabilityAnalyzer
from .drift_detector import DriftDetector
from .storage import ObservabilityStorage

# Import CloudWatch components if available
try:
    from .cloudwatch_publisher import CloudWatchPublisher
    from .cloudwatch_dashboard import CloudWatchDashboard, setup_cloudwatch_observability
    __all__ = [
        'MetricsCollector',
        'AIObservabilityAnalyzer',
        'DriftDetector',
        'ObservabilityStorage',
        'CloudWatchPublisher',
        'CloudWatchDashboard',
        'setup_cloudwatch_observability'
    ]
except ImportError:
    __all__ = [
        'MetricsCollector',
        'AIObservabilityAnalyzer',
        'DriftDetector',
        'ObservabilityStorage'
    ]

