"""
CloudWatch Dashboard - Creates and manages CloudWatch dashboards for observability
"""

import boto3
import json
import os
from typing import Dict, Any, List, Optional
from botocore.exceptions import ClientError


class CloudWatchDashboard:
    """
    Creates and manages CloudWatch dashboards for LangChain service observability
    """
    
    def __init__(
        self,
        dashboard_name: str = "LangChainService-Observability",
        region_name: str = None
    ):
        """
        Initialize CloudWatch dashboard manager
        
        Args:
            dashboard_name: Name of the CloudWatch dashboard
            region_name: AWS region (defaults to AWS_DEFAULT_REGION env var or us-east-1)
        """
        self.dashboard_name = dashboard_name
        self.region_name = region_name or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        self.namespace = "LangChainService/Observability"
        
        try:
            self.cloudwatch = boto3.client('cloudwatch', region_name=self.region_name)
            print(f"✅ CloudWatch dashboard manager initialized for region: {self.region_name}")
        except Exception as e:
            print(f"⚠️  Warning: Could not initialize CloudWatch client: {e}")
            raise
    
    def create_comprehensive_dashboard(self) -> bool:
        """
        Create a comprehensive CloudWatch dashboard with all observability metrics
        
        Returns:
            True if successful, False otherwise
        """
        try:
            dashboard_body = {
                "widgets": [
                    # Row 1: Overview metrics
                    self._create_metric_widget(
                        title="Request Success Rate",
                        metrics=[
                            [self.namespace, "RequestSuccess", {"stat": "Average", "label": "Success Rate"}]
                        ],
                        y_pos=0,
                        x_pos=0,
                        width=8,
                        height=6
                    ),
                    self._create_metric_widget(
                        title="Total Requests",
                        metrics=[
                            [self.namespace, "RequestSuccess", {"stat": "SampleCount", "label": "Total Requests"}]
                        ],
                        y_pos=0,
                        x_pos=8,
                        width=8,
                        height=6
                    ),
                    self._create_metric_widget(
                        title="Execution Time (p50, p90, p99)",
                        metrics=[
                            [self.namespace, "ExecutionTime", {"stat": "p50", "label": "p50"}],
                            [self.namespace, "ExecutionTime", {"stat": "p90", "label": "p90"}],
                            [self.namespace, "ExecutionTime", {"stat": "p99", "label": "p99"}]
                        ],
                        y_pos=0,
                        x_pos=16,
                        width=8,
                        height=6
                    ),
                    
                    # Row 2: Token and Cost metrics
                    self._create_metric_widget(
                        title="Total Tokens Used",
                        metrics=[
                            [self.namespace, "TotalTokens", {"stat": "Sum", "label": "Total Tokens"}]
                        ],
                        y_pos=6,
                        x_pos=0,
                        width=8,
                        height=6
                    ),
                    self._create_metric_widget(
                        title="Average Tokens per Request",
                        metrics=[
                            [self.namespace, "TotalTokens", {"stat": "Average", "label": "Avg Tokens"}]
                        ],
                        y_pos=6,
                        x_pos=8,
                        width=8,
                        height=6
                    ),
                    self._create_metric_widget(
                        title="Total Cost (USD)",
                        metrics=[
                            [self.namespace, "TotalCost", {"stat": "Sum", "label": "Total Cost"}]
                        ],
                        y_pos=6,
                        x_pos=16,
                        width=8,
                        height=6
                    ),
                    
                    # Row 3: Agent-level metrics
                    self._create_metric_widget(
                        title="Agent Execution Time by Agent",
                        metrics=[
                            [self.namespace, "AgentExecutionTime", {"stat": "Average"}]
                        ],
                        y_pos=12,
                        x_pos=0,
                        width=12,
                        height=6,
                        period=300
                    ),
                    self._create_metric_widget(
                        title="Agent Success Rate",
                        metrics=[
                            [self.namespace, "AgentSuccess", {"stat": "Average", "label": "Agent Success Rate"}]
                        ],
                        y_pos=12,
                        x_pos=12,
                        width=12,
                        height=6
                    ),
                    
                    # Row 4: Recommendations and Agents
                    self._create_metric_widget(
                        title="Recommendations Generated",
                        metrics=[
                            [self.namespace, "RecommendationsCount", {"stat": "Sum", "label": "Total Recommendations"}],
                            [self.namespace, "RecommendationsCount", {"stat": "Average", "label": "Avg per Request"}]
                        ],
                        y_pos=18,
                        x_pos=0,
                        width=12,
                        height=6
                    ),
                    self._create_metric_widget(
                        title="Agents Executed per Request",
                        metrics=[
                            [self.namespace, "AgentsExecutedCount", {"stat": "Average", "label": "Avg Agents"}]
                        ],
                        y_pos=18,
                        x_pos=12,
                        width=12,
                        height=6
                    ),
                    
                    # Row 5: Performance by Urgency
                    self._create_metric_widget(
                        title="Execution Time by Urgency",
                        metrics=[
                            [self.namespace, "ExecutionTime", "Urgency", "critical", {"stat": "Average", "label": "Critical"}],
                            [self.namespace, "ExecutionTime", "Urgency", "high", {"stat": "Average", "label": "High"}],
                            [self.namespace, "ExecutionTime", "Urgency", "medium", {"stat": "Average", "label": "Medium"}],
                            [self.namespace, "ExecutionTime", "Urgency", "low", {"stat": "Average", "label": "Low"}]
                        ],
                        y_pos=24,
                        x_pos=0,
                        width=12,
                        height=6
                    ),
                    self._create_metric_widget(
                        title="Cost by Urgency",
                        metrics=[
                            [self.namespace, "TotalCost", "Urgency", "critical", {"stat": "Sum", "label": "Critical"}],
                            [self.namespace, "TotalCost", "Urgency", "high", {"stat": "Sum", "label": "High"}],
                            [self.namespace, "TotalCost", "Urgency", "medium", {"stat": "Sum", "label": "Medium"}],
                            [self.namespace, "TotalCost", "Urgency", "low", {"stat": "Sum", "label": "Low"}]
                        ],
                        y_pos=24,
                        x_pos=12,
                        width=12,
                        height=6
                    ),
                    
                    # Row 6: Drift Detection
                    self._create_metric_widget(
                        title="Drift Detected",
                        metrics=[
                            [self.namespace, "DriftDetected", {"stat": "Sum", "label": "Drift Events"}]
                        ],
                        y_pos=30,
                        x_pos=0,
                        width=8,
                        height=6
                    ),
                    self._create_metric_widget(
                        title="Drift Severity",
                        metrics=[
                            [self.namespace, "DriftSeverity", {"stat": "Maximum", "label": "Max Severity"}]
                        ],
                        y_pos=30,
                        x_pos=8,
                        width=8,
                        height=6
                    ),
                    self._create_metric_widget(
                        title="Mean Execution Time (Drift Monitoring)",
                        metrics=[
                            [self.namespace, "MeanExecutionTime", {"stat": "Average", "label": "Mean Exec Time"}]
                        ],
                        y_pos=30,
                        x_pos=16,
                        width=8,
                        height=6
                    ),
                    
                    # Row 7: AI Analysis Quality Metrics
                    self._create_metric_widget(
                        title="Text Quality Scores",
                        metrics=[
                            [self.namespace, "TextClarityScore", {"stat": "Average", "label": "Clarity"}],
                            [self.namespace, "TextCompletenessScore", {"stat": "Average", "label": "Completeness"}],
                            [self.namespace, "TextOverallScore", {"stat": "Average", "label": "Overall"}]
                        ],
                        y_pos=36,
                        x_pos=0,
                        width=12,
                        height=6
                    ),
                    self._create_metric_widget(
                        title="Efficiency Score",
                        metrics=[
                            [self.namespace, "EfficiencyScore", {"stat": "Average", "label": "Efficiency"}]
                        ],
                        y_pos=36,
                        x_pos=12,
                        width=12,
                        height=6
                    )
                ]
            }
            
            # Create or update the dashboard
            self.cloudwatch.put_dashboard(
                DashboardName=self.dashboard_name,
                DashboardBody=json.dumps(dashboard_body)
            )
            
            dashboard_url = f"https://{self.region_name}.console.aws.amazon.com/cloudwatch/home?region={self.region_name}#dashboards:name={self.dashboard_name}"
            
            print(f"✅ CloudWatch dashboard created successfully!")
            print(f"📊 Dashboard name: {self.dashboard_name}")
            print(f"🔗 Dashboard URL: {dashboard_url}")
            
            return True
            
        except ClientError as e:
            print(f"❌ Error creating CloudWatch dashboard: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error creating CloudWatch dashboard: {e}")
            return False
    
    def _create_metric_widget(
        self,
        title: str,
        metrics: List[List],
        y_pos: int,
        x_pos: int,
        width: int = 12,
        height: int = 6,
        period: int = 300,
        stat: str = None
    ) -> Dict[str, Any]:
        """
        Create a metric widget configuration
        
        Args:
            title: Widget title
            metrics: List of metric specifications
            y_pos: Y position in dashboard grid
            x_pos: X position in dashboard grid
            width: Widget width
            height: Widget height
            period: Metric period in seconds
            stat: Default statistic (if not specified in metrics)
            
        Returns:
            Widget configuration dictionary
        """
        return {
            "type": "metric",
            "x": x_pos,
            "y": y_pos,
            "width": width,
            "height": height,
            "properties": {
                "metrics": metrics,
                "period": period,
                "stat": stat or "Average",
                "region": self.region_name,
                "title": title,
                "yAxis": {
                    "left": {
                        "showUnits": False
                    }
                },
                "view": "timeSeries",
                "stacked": False
            }
        }
    
    def delete_dashboard(self) -> bool:
        """
        Delete the CloudWatch dashboard
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.cloudwatch.delete_dashboards(
                DashboardNames=[self.dashboard_name]
            )
            print(f"✅ Dashboard '{self.dashboard_name}' deleted successfully")
            return True
            
        except ClientError as e:
            if e.response['Error']['Code'] == 'ResourceNotFound':
                print(f"Dashboard '{self.dashboard_name}' does not exist")
            else:
                print(f"❌ Error deleting dashboard: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error deleting dashboard: {e}")
            return False
    
    def list_dashboards(self) -> List[str]:
        """
        List all CloudWatch dashboards
        
        Returns:
            List of dashboard names
        """
        try:
            response = self.cloudwatch.list_dashboards()
            dashboards = [d['DashboardName'] for d in response.get('DashboardEntries', [])]
            
            if dashboards:
                print(f"📊 Found {len(dashboards)} dashboard(s):")
                for name in dashboards:
                    print(f"   • {name}")
            else:
                print("No dashboards found")
            
            return dashboards
            
        except Exception as e:
            print(f"❌ Error listing dashboards: {e}")
            return []
    
    def create_alarms(self) -> bool:
        """
        Create CloudWatch alarms for critical metrics
        
        Returns:
            True if successful, False otherwise
        """
        try:
            alarms = [
                {
                    'AlarmName': f'{self.dashboard_name}-HighExecutionTime',
                    'MetricName': 'ExecutionTime',
                    'Threshold': 30000,  # 30 seconds
                    'ComparisonOperator': 'GreaterThanThreshold',
                    'EvaluationPeriods': 2,
                    'AlarmDescription': 'Alert when execution time exceeds 30 seconds'
                },
                {
                    'AlarmName': f'{self.dashboard_name}-LowSuccessRate',
                    'MetricName': 'RequestSuccess',
                    'Threshold': 0.8,  # 80%
                    'ComparisonOperator': 'LessThanThreshold',
                    'EvaluationPeriods': 3,
                    'AlarmDescription': 'Alert when success rate drops below 80%'
                },
                {
                    'AlarmName': f'{self.dashboard_name}-DriftDetected',
                    'MetricName': 'DriftSeverity',
                    'Threshold': 3,  # High severity
                    'ComparisonOperator': 'GreaterThanOrEqualToThreshold',
                    'EvaluationPeriods': 1,
                    'AlarmDescription': 'Alert when high or critical drift is detected'
                },
                {
                    'AlarmName': f'{self.dashboard_name}-HighCost',
                    'MetricName': 'TotalCost',
                    'Threshold': 1.0,  # $1 per request
                    'ComparisonOperator': 'GreaterThanThreshold',
                    'EvaluationPeriods': 2,
                    'AlarmDescription': 'Alert when request cost exceeds $1'
                }
            ]
            
            for alarm_config in alarms:
                self.cloudwatch.put_metric_alarm(
                    AlarmName=alarm_config['AlarmName'],
                    MetricName=alarm_config['MetricName'],
                    Namespace=self.namespace,
                    Statistic='Average',
                    Period=300,  # 5 minutes
                    EvaluationPeriods=alarm_config['EvaluationPeriods'],
                    Threshold=alarm_config['Threshold'],
                    ComparisonOperator=alarm_config['ComparisonOperator'],
                    AlarmDescription=alarm_config['AlarmDescription'],
                    ActionsEnabled=False  # Enable and configure SNS topics as needed
                )
                print(f"✅ Created alarm: {alarm_config['AlarmName']}")
            
            print(f"\n✅ Created {len(alarms)} CloudWatch alarms")
            print("⚠️  Note: Alarms are created but not enabled. Configure SNS topics to receive notifications.")
            return True
            
        except Exception as e:
            print(f"❌ Error creating alarms: {e}")
            return False


def setup_cloudwatch_observability(
    region_name: str = None,
    create_dashboard: bool = True,
    create_alarms: bool = False
) -> bool:
    """
    Complete setup of CloudWatch observability
    
    Args:
        region_name: AWS region
        create_dashboard: Whether to create the dashboard
        create_alarms: Whether to create alarms
        
    Returns:
        True if successful, False otherwise
    """
    try:
        dashboard_manager = CloudWatchDashboard(region_name=region_name)
        
        success = True
        
        if create_dashboard:
            print("\n📊 Creating CloudWatch Dashboard...")
            success = dashboard_manager.create_comprehensive_dashboard() and success
        
        if create_alarms:
            print("\n🚨 Creating CloudWatch Alarms...")
            success = dashboard_manager.create_alarms() and success
        
        return success
        
    except Exception as e:
        print(f"❌ Error setting up CloudWatch observability: {e}")
        return False


if __name__ == "__main__":
    # CLI for dashboard management
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "create":
            print("🚀 Setting up CloudWatch observability...")
            success = setup_cloudwatch_observability(create_dashboard=True, create_alarms=True)
            sys.exit(0 if success else 1)
        
        elif command == "delete":
            dashboard = CloudWatchDashboard()
            dashboard.delete_dashboard()
            sys.exit(0)
        
        elif command == "list":
            dashboard = CloudWatchDashboard()
            dashboard.list_dashboards()
            sys.exit(0)
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python cloudwatch_dashboard.py [create|delete|list]")
            sys.exit(1)
    else:
        print("Usage: python cloudwatch_dashboard.py [create|delete|list]")
        sys.exit(1)

