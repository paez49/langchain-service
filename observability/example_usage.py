"""
Example Usage of Observability System

This demonstrates how to use the observability system both directly
and through the API endpoints.
"""

import requests
import json
from datetime import datetime


# Base URL for the API
BASE_URL = "http://localhost:8000"


def example_1_basic_recommendation_with_observability():
    """
    Example 1: Make a recommendation request with observability enabled
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Basic Recommendation with Observability")
    print("=" * 80)
    
    request_data = {
        "requested_item": "Aspirin 500mg for headache relief",
        "country": "CO",
        "quantity": 200,
        "urgency": "high",
        "enable_observability": True,
        "enable_ai_analysis": False  # Disabled to save costs
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/recommendations",
        json=request_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✅ Request successful!")
        print(f"Strategy: {result['strategy']}")
        print(f"Recommendations: {len(result['recommendations'])}")
        
        # Check observability data
        if result.get('observability'):
            obs = result['observability']
            metrics = obs['metrics']
            
            print(f"\n📊 Observability Metrics:")
            print(f"  Request ID: {obs['request_id']}")
            print(f"  Total Time: {metrics['total_execution_time_ms']:.0f}ms")
            print(f"  Total Tokens: {metrics['total_tokens']}")
            print(f"  Total Cost: ${metrics['total_cost_usd']:.4f}")
            print(f"  Agents: {', '.join(metrics['agents_executed'])}")
            
            # Show per-agent metrics
            print(f"\n  Per-Agent Breakdown:")
            for agent in metrics['agent_metrics']:
                print(f"    • {agent['agent_name']}: {agent['execution_time_ms']:.0f}ms, "
                      f"{agent['total_tokens']} tokens, ${agent['estimated_cost_usd']:.4f}")
            
            return obs['request_id']
    else:
        print(f"\n❌ Request failed: {response.status_code}")
        print(response.text)
        return None


def example_2_get_observability_summary():
    """
    Example 2: Get observability summary for last 24 hours
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Get Observability Summary")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/api/v1/observability/summary?hours=24")
    
    if response.status_code == 200:
        summary = response.json()
        
        print(f"\n📊 Last 24 Hours Summary:")
        print(f"  Total Requests: {summary['count']}")
        print(f"  Success Rate: {summary['success_rate']:.1f}%")
        print(f"  Avg Execution Time: {summary['avg_execution_time_ms']:.0f}ms")
        print(f"  Avg Tokens/Request: {summary['avg_tokens_per_request']:.0f}")
        print(f"  Avg Cost/Request: ${summary['avg_cost_per_request_usd']:.4f}")
        print(f"  Total Cost: ${summary['total_cost_usd']:.4f}")
        
        if summary.get('most_used_agents'):
            print(f"\n  Most Used Agents:")
            for agent, count in summary['most_used_agents']:
                print(f"    • {agent}: {count} executions")
    else:
        print(f"\n❌ Failed to get summary: {response.status_code}")


def example_3_get_specific_request_metrics(request_id):
    """
    Example 3: Get detailed metrics for a specific request
    """
    if not request_id:
        print("\n⚠️  Skipping Example 3: No request ID available")
        return
    
    print("\n" + "=" * 80)
    print(f"EXAMPLE 3: Get Metrics for Request {request_id[:8]}...")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/api/v1/observability/metrics/{request_id}")
    
    if response.status_code == 200:
        metrics = response.json()
        
        print(f"\n📊 Request Details:")
        print(f"  Item: {metrics['requested_item']}")
        print(f"  Country: {metrics['country']}")
        print(f"  Urgency: {metrics['urgency']}")
        print(f"  Strategy: {metrics['strategy']}")
        print(f"  Total Time: {metrics['total_execution_time_ms']:.0f}ms")
        print(f"  Success: {metrics['success']}")
        
        print(f"\n  Agent Execution Timeline:")
        for i, agent in enumerate(metrics['agent_metrics'], 1):
            print(f"    {i}. {agent['agent_name']} ({agent['execution_time_ms']:.0f}ms)")
            if agent.get('output_text'):
                output_preview = agent['output_text'][:100].replace('\n', ' ')
                print(f"       Output: {output_preview}...")
    else:
        print(f"\n❌ Failed to get metrics: {response.status_code}")


def example_4_check_drift_alerts():
    """
    Example 4: Check for drift detection alerts
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Check Drift Alerts")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/api/v1/observability/drift/alerts")
    
    if response.status_code == 200:
        data = response.json()
        alerts = data['alerts']
        
        if alerts:
            print(f"\n⚠️  {len(alerts)} Drift Alert(s) Detected:")
            for i, alert in enumerate(alerts, 1):
                print(f"\n  Alert {i}:")
                print(f"    Timestamp: {alert['timestamp']}")
                print(f"    Severity: {alert['severity'].upper()}")
                print(f"    Indicators:")
                for indicator in alert['indicators']:
                    print(f"      • {indicator}")
                if alert['recommendations']:
                    print(f"    Recommendations:")
                    for rec in alert['recommendations']:
                        print(f"      {rec}")
        else:
            print(f"\n✅ No drift alerts - system behavior is stable")
    else:
        print(f"\n❌ Failed to get drift alerts: {response.status_code}")


def example_5_recommendation_with_ai_analysis():
    """
    Example 5: Make a recommendation with AI analysis enabled
    (More expensive - uses additional LLM calls)
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Recommendation with AI Analysis")
    print("=" * 80)
    
    request_data = {
        "requested_item": "Ibuprofen 400mg for inflammation",
        "country": "PE",
        "quantity": 150,
        "urgency": "medium",
        "enable_observability": True,
        "enable_ai_analysis": True  # Enable AI analysis
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/recommendations",
        json=request_data
    )
    
    if response.status_code == 200:
        result = response.json()
        
        print(f"\n✅ Request successful with AI analysis!")
        
        if result.get('observability', {}).get('ai_analysis'):
            ai_analysis = result['observability']['ai_analysis']
            
            # Text quality results
            if ai_analysis.get('text_quality'):
                print(f"\n📝 Text Quality Analysis:")
                for quality in ai_analysis['text_quality'][:2]:  # Show first 2
                    print(f"\n  Agent: {quality['agent_name']}")
                    print(f"    Overall Score: {quality['overall_score']:.1f}/10")
                    print(f"    Coherence: {quality['coherence_score']:.1f}/10")
                    print(f"    Completeness: {quality['completeness_score']:.1f}/10")
                    print(f"    Clarity: {quality['clarity_score']:.1f}/10")
            
            # Performance analysis
            if ai_analysis.get('performance_analysis'):
                perf = ai_analysis['performance_analysis']
                print(f"\n⚡ Performance Analysis:")
                print(f"  Performance Score: {perf['performance_score']:.1f}/10")
                print(f"  Cost Efficiency: {perf['cost_efficiency_score']:.1f}/10")
                if perf.get('optimization_suggestions'):
                    print(f"  Suggestions:")
                    for suggestion in perf['optimization_suggestions'][:3]:
                        print(f"    • {suggestion}")
    else:
        print(f"\n❌ Request failed: {response.status_code}")


def example_6_set_drift_baseline():
    """
    Example 6: Set a new baseline for drift detection
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Set Drift Baseline")
    print("=" * 80)
    
    response = requests.post(
        f"{BASE_URL}/api/v1/observability/drift/set-baseline?num_samples=50"
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ {result['message']}")
        print(f"  Samples used: {result['samples_used']}")
    else:
        print(f"\n❌ Failed to set baseline: {response.status_code}")
        print(response.text)


def main():
    """
    Run all examples in sequence
    """
    print("\n" + "=" * 80)
    print("🔬 OBSERVABILITY SYSTEM - EXAMPLE USAGE")
    print("=" * 80)
    print("\nThis script demonstrates the observability features.")
    print("Make sure the API server is running on http://localhost:8000")
    print("=" * 80)
    
    try:
        # Example 1: Basic recommendation with observability
        request_id = example_1_basic_recommendation_with_observability()
        
        # Example 2: Get summary
        example_2_get_observability_summary()
        
        # Example 3: Get specific request metrics
        example_3_get_specific_request_metrics(request_id)
        
        # Example 4: Check drift alerts
        example_4_check_drift_alerts()
        
        # Example 5: AI analysis (optional - more expensive)
        # Uncomment to run:
        # example_5_recommendation_with_ai_analysis()
        
        # Example 6: Set baseline (optional)
        # Uncomment to run:
        # example_6_set_drift_baseline()
        
        print("\n" + "=" * 80)
        print("✅ All examples completed!")
        print("=" * 80 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server")
        print("   Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()

