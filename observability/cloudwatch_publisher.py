"""
CloudWatch Publisher - Publishes observability metrics to AWS CloudWatch
"""

import boto3
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import threading
from botocore.exceptions import ClientError, BotoCoreError


class CloudWatchPublisher:
    """
    Publishes observability metrics to AWS CloudWatch
    
    Publishes:
    - Request metrics (execution time, tokens, cost)
    - Agent performance metrics
    - Drift detection metrics
    - AI analysis scores
    """
    
    def __init__(
        self,
        namespace: str = "LangChainService/Observability",
        region_name: str = None,
        enabled: bool = True
    ):
        """
        Initialize CloudWatch publisher
        
        Args:
            namespace: CloudWatch namespace for metrics
            region_name: AWS region (defaults to AWS_DEFAULT_REGION env var or us-east-1)
            enabled: Whether CloudWatch publishing is enabled
        """
        self.namespace = namespace
        self.enabled = enabled
        
        if not self.enabled:
            print("CloudWatch publishing is disabled")
            return
        
        # Get region from environment or use default
        self.region_name = region_name or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        
        try:
            # Initialize CloudWatch client
            self.cloudwatch = boto3.client('cloudwatch', region_name=self.region_name)
            print(f"✅ CloudWatch publisher initialized for region: {self.region_name}")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize CloudWatch client: {e}")
            print("   Metrics will not be published to CloudWatch")
            self.enabled = False
        
        # Thread lock for concurrent access
        self.lock = threading.Lock()
        
        # Batch metrics for efficiency
        self.metric_buffer: List[Dict[str, Any]] = []
        self.max_buffer_size = 20  # CloudWatch limit is 1000, but we keep it smaller
    
    def publish_request_metrics(self, metrics: Dict[str, Any]) -> bool:
        """
        Publish request-level metrics to CloudWatch
        
        Args:
            metrics: Request metrics dictionary
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            metric_data = []
            timestamp = datetime.utcnow()
            
            # Common dimensions
            dimensions = [
                {'Name': 'Service', 'Value': 'LangChainRecommender'},
                {'Name': 'Urgency', 'Value': metrics.get('urgency', 'unknown')},
                {'Name': 'Strategy', 'Value': metrics.get('strategy', 'unknown')},
                {'Name': 'Country', 'Value': metrics.get('country', 'unknown')}
            ]
            
            # Request success/failure
            metric_data.append({
                'MetricName': 'RequestSuccess',
                'Dimensions': dimensions,
                'Value': 1.0 if metrics.get('success', True) else 0.0,
                'Unit': 'None',
                'Timestamp': timestamp
            })
            
            # Total execution time
            if 'total_execution_time_ms' in metrics:
                metric_data.append({
                    'MetricName': 'ExecutionTime',
                    'Dimensions': dimensions,
                    'Value': metrics['total_execution_time_ms'],
                    'Unit': 'Milliseconds',
                    'Timestamp': timestamp
                })
            
            # Total tokens
            if 'total_tokens' in metrics:
                metric_data.append({
                    'MetricName': 'TotalTokens',
                    'Dimensions': dimensions,
                    'Value': float(metrics['total_tokens']),
                    'Unit': 'Count',
                    'Timestamp': timestamp
                })
            
            # Total cost
            if 'total_cost_usd' in metrics:
                metric_data.append({
                    'MetricName': 'TotalCost',
                    'Dimensions': dimensions,
                    'Value': metrics['total_cost_usd'],
                    'Unit': 'None',
                    'Timestamp': timestamp
                })
            
            # Number of recommendations
            if 'final_recommendations_count' in metrics:
                metric_data.append({
                    'MetricName': 'RecommendationsCount',
                    'Dimensions': dimensions,
                    'Value': float(metrics['final_recommendations_count']),
                    'Unit': 'Count',
                    'Timestamp': timestamp
                })
            
            # Number of agents executed
            agents_count = len(metrics.get('agents_executed', []))
            metric_data.append({
                'MetricName': 'AgentsExecutedCount',
                'Dimensions': dimensions,
                'Value': float(agents_count),
                'Unit': 'Count',
                'Timestamp': timestamp
            })
            
            # Publish metrics
            return self._publish_metrics(metric_data)
            
        except Exception as e:
            print(f"Error publishing request metrics to CloudWatch: {e}")
            return False
    
    def publish_agent_metrics(self, agent_metrics: List[Dict[str, Any]], request_context: Dict[str, Any]) -> bool:
        """
        Publish agent-level metrics to CloudWatch
        
        Args:
            agent_metrics: List of agent metrics
            request_context: Context about the request (urgency, strategy, etc.)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled or not agent_metrics:
            return False
        
        try:
            metric_data = []
            timestamp = datetime.utcnow()
            
            for agent_metric in agent_metrics:
                agent_name = agent_metric.get('agent_name', 'unknown')
                
                dimensions = [
                    {'Name': 'Service', 'Value': 'LangChainRecommender'},
                    {'Name': 'AgentName', 'Value': agent_name},
                    {'Name': 'Urgency', 'Value': request_context.get('urgency', 'unknown')},
                    {'Name': 'Strategy', 'Value': request_context.get('strategy', 'unknown')}
                ]
                
                # Agent execution time
                if 'execution_time_ms' in agent_metric:
                    metric_data.append({
                        'MetricName': 'AgentExecutionTime',
                        'Dimensions': dimensions,
                        'Value': agent_metric['execution_time_ms'],
                        'Unit': 'Milliseconds',
                        'Timestamp': timestamp
                    })
                
                # Agent tokens
                if 'total_tokens' in agent_metric:
                    metric_data.append({
                        'MetricName': 'AgentTokens',
                        'Dimensions': dimensions,
                        'Value': float(agent_metric['total_tokens']),
                        'Unit': 'Count',
                        'Timestamp': timestamp
                    })
                
                # Agent cost
                if 'estimated_cost_usd' in agent_metric:
                    metric_data.append({
                        'MetricName': 'AgentCost',
                        'Dimensions': dimensions,
                        'Value': agent_metric['estimated_cost_usd'],
                        'Unit': 'None',
                        'Timestamp': timestamp
                    })
                
                # Agent success
                metric_data.append({
                    'MetricName': 'AgentSuccess',
                    'Dimensions': dimensions,
                    'Value': 1.0 if agent_metric.get('success', True) else 0.0,
                    'Unit': 'None',
                    'Timestamp': timestamp
                })
            
            # Publish in batches (CloudWatch max is 1000 per call)
            return self._publish_metrics(metric_data)
            
        except Exception as e:
            print(f"Error publishing agent metrics to CloudWatch: {e}")
            return False
    
    def publish_drift_metrics(self, drift_analysis: Dict[str, Any]) -> bool:
        """
        Publish drift detection metrics to CloudWatch
        
        Args:
            drift_analysis: Drift analysis results
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            metric_data = []
            timestamp = datetime.utcnow()
            
            dimensions = [
                {'Name': 'Service', 'Value': 'LangChainRecommender'},
                {'Name': 'MetricType', 'Value': 'DriftDetection'}
            ]
            
            # Drift detected flag
            drift_detected = drift_analysis.get('drift_detected', False)
            metric_data.append({
                'MetricName': 'DriftDetected',
                'Dimensions': dimensions,
                'Value': 1.0 if drift_detected else 0.0,
                'Unit': 'None',
                'Timestamp': timestamp
            })
            
            # Drift severity (if drift detected)
            if drift_detected:
                severity_map = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
                severity = drift_analysis.get('severity', 'low')
                severity_value = severity_map.get(severity, 0)
                
                metric_data.append({
                    'MetricName': 'DriftSeverity',
                    'Dimensions': dimensions,
                    'Value': float(severity_value),
                    'Unit': 'None',
                    'Timestamp': timestamp
                })
            
            # Statistical metrics
            stats = drift_analysis.get('statistical_summary', {})
            
            if 'mean_execution_time' in stats:
                metric_data.append({
                    'MetricName': 'MeanExecutionTime',
                    'Dimensions': dimensions,
                    'Value': stats['mean_execution_time'],
                    'Unit': 'Milliseconds',
                    'Timestamp': timestamp
                })
            
            if 'mean_tokens' in stats:
                metric_data.append({
                    'MetricName': 'MeanTokens',
                    'Dimensions': dimensions,
                    'Value': stats['mean_tokens'],
                    'Unit': 'Count',
                    'Timestamp': timestamp
                })
            
            if 'mean_cost' in stats:
                metric_data.append({
                    'MetricName': 'MeanCost',
                    'Dimensions': dimensions,
                    'Value': stats['mean_cost'],
                    'Unit': 'None',
                    'Timestamp': timestamp
                })
            
            return self._publish_metrics(metric_data)
            
        except Exception as e:
            print(f"Error publishing drift metrics to CloudWatch: {e}")
            return False
    
    def publish_ai_analysis_metrics(self, ai_analysis: Dict[str, Any]) -> bool:
        """
        Publish AI analysis metrics to CloudWatch
        
        Args:
            ai_analysis: AI analysis results
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            return False
        
        try:
            metric_data = []
            timestamp = datetime.utcnow()
            
            dimensions = [
                {'Name': 'Service', 'Value': 'LangChainRecommender'},
                {'Name': 'MetricType', 'Value': 'AIAnalysis'}
            ]
            
            # Text quality scores
            text_quality = ai_analysis.get('text_quality', [])
            for quality in text_quality:
                agent_name = quality.get('agent_name', 'unknown')
                agent_dimensions = dimensions + [{'Name': 'AgentName', 'Value': agent_name}]
                
                if 'clarity_score' in quality:
                    metric_data.append({
                        'MetricName': 'TextClarityScore',
                        'Dimensions': agent_dimensions,
                        'Value': quality['clarity_score'],
                        'Unit': 'None',
                        'Timestamp': timestamp
                    })
                
                if 'completeness_score' in quality:
                    metric_data.append({
                        'MetricName': 'TextCompletenessScore',
                        'Dimensions': agent_dimensions,
                        'Value': quality['completeness_score'],
                        'Unit': 'None',
                        'Timestamp': timestamp
                    })
                
                if 'overall_score' in quality:
                    metric_data.append({
                        'MetricName': 'TextOverallScore',
                        'Dimensions': agent_dimensions,
                        'Value': quality['overall_score'],
                        'Unit': 'None',
                        'Timestamp': timestamp
                    })
            
            # Performance analysis
            performance = ai_analysis.get('performance_analysis', {})
            
            if 'efficiency_score' in performance:
                metric_data.append({
                    'MetricName': 'EfficiencyScore',
                    'Dimensions': dimensions,
                    'Value': performance['efficiency_score'],
                    'Unit': 'None',
                    'Timestamp': timestamp
                })
            
            if 'bottlenecks' in performance:
                bottleneck_count = len(performance['bottlenecks'])
                metric_data.append({
                    'MetricName': 'BottleneckCount',
                    'Dimensions': dimensions,
                    'Value': float(bottleneck_count),
                    'Unit': 'Count',
                    'Timestamp': timestamp
                })
            
            return self._publish_metrics(metric_data)
            
        except Exception as e:
            print(f"Error publishing AI analysis metrics to CloudWatch: {e}")
            return False
    
    def _publish_metrics(self, metric_data: List[Dict[str, Any]]) -> bool:
        """
        Internal method to publish metrics to CloudWatch
        
        Args:
            metric_data: List of metric data dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        if not self.enabled:
            print("[CloudWatchPublisher] Publish skipped - publisher disabled")
            return False
        
        if not metric_data:
            print("[CloudWatchPublisher] Publish skipped - no metric data provided")
            return False
        
        try:
            print(f"[CloudWatchPublisher] Preparing to publish {len(metric_data)} metric(s) to namespace {self.namespace}")
            with self.lock:
                # CloudWatch allows max 1000 metrics per call, but we batch smaller
                batch_size = 20
                for i in range(0, len(metric_data), batch_size):
                    batch = metric_data[i:i + batch_size]
                    batch_number = (i // batch_size) + 1
                    print(f"[CloudWatchPublisher] Publishing batch {batch_number} with {len(batch)} metric(s)")
                    
                    try:
                        self.cloudwatch.put_metric_data(
                            Namespace=self.namespace,
                            MetricData=batch
                        )
                        print(f"[CloudWatchPublisher] Batch {batch_number} published successfully")
                    except (ClientError, BotoCoreError) as e:
                        print(f"Error publishing metrics batch to CloudWatch: {e}")
                        return False
            
            print("[CloudWatchPublisher] All metric batches published successfully")
            return True
            
        except Exception as e:
            print(f"Unexpected error publishing metrics to CloudWatch: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test CloudWatch connection by publishing a test metric
        
        Returns:
            True if connection works, False otherwise
        """
        if not self.enabled:
            print("CloudWatch publishing is disabled")
            return False
        
        try:
            test_metric = [{
                'MetricName': 'ConnectionTest',
                'Dimensions': [
                    {'Name': 'Service', 'Value': 'LangChainRecommender'},
                    {'Name': 'Type', 'Value': 'Test'}
                ],
                'Value': 1.0,
                'Unit': 'None',
                'Timestamp': datetime.utcnow()
            }]
            
            self.cloudwatch.put_metric_data(
                Namespace=self.namespace,
                MetricData=test_metric
            )
            
            print(f"✅ CloudWatch connection test successful (Namespace: {self.namespace})")
            return True
            
        except Exception as e:
            print(f"❌ CloudWatch connection test failed: {e}")
            return False

