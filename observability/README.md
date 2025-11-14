# AI Observability System

Comprehensive observability system for monitoring and analyzing multi-agent AI system performance.

## 🚀 Quick Start: CloudWatch Integration

**NEW!** Send all observability metrics to AWS CloudWatch with dashboards and alarms!

```bash
# Enable CloudWatch metrics
export ENABLE_CLOUDWATCH_METRICS=true
export AWS_DEFAULT_REGION=us-east-1

# Start service
python main.py

# Create CloudWatch dashboard
curl -X POST http://localhost:8000/api/v1/observability/cloudwatch/setup \
  -d '{"create_dashboard": true}'
```

📖 **Quick Start Guide:** [QUICKSTART_CLOUDWATCH.md](./QUICKSTART_CLOUDWATCH.md)  
📚 **Full CloudWatch Documentation:** [CLOUDWATCH_SETUP.md](./CLOUDWATCH_SETUP.md)

## 📊 Components

### 1. **Metrics Collector** (`metrics_collector.py`)
Tracks quantitative metrics for each request and agent execution:

- **Token Usage**: Input/output tokens per agent and request
- **Costs**: Estimated costs based on model pricing
- **Response Times**: Execution time for each agent
- **Success Rates**: Tracking successful vs failed executions

**Key Features:**
- Automatic token counting using `tiktoken`
- Multi-model pricing support (Claude, GPT-4, GPT-3.5)
- Agent-level and request-level metrics
- Real-time metric collection

### 2. **AI Analyzer** (`ai_analyzer.py`)
AI-powered analysis component that evaluates agent performance:

#### Text Quality Analysis
- **Coherence Score** (0-10): Logical structure and consistency
- **Completeness Score** (0-10): Whether requirements are fully addressed
- **Clarity Score** (0-10): Understandability
- **Professional Score** (0-10): Tone appropriateness

#### Reasoning Analysis
- **Logic Score** (0-10): Soundness of reasoning
- **Appropriateness Score** (0-10): Decision quality for given input
- **Justification Score** (0-10): Quality of explanations
- **Consistency Score** (0-10): Alignment with best practices

#### Performance Analysis
- Identifies bottlenecks
- Suggests optimization opportunities
- Detects anomalies
- Provides actionable recommendations

### 3. **Drift Detector** (`drift_detector.py`)
Statistical drift detection using:

#### Entropy Analysis
- **Shannon Entropy**: Measures text diversity/predictability
- **Character-level Entropy**: Detects repetitive patterns
- **Word-level Entropy**: Analyzes vocabulary diversity

#### Kolmogorov-Smirnov Test
- Compares distributions of:
  - Execution times
  - Token usage
  - Costs
- Detects significant shifts with 95% confidence

**Drift Severity Levels:**
- `none`: No drift detected
- `low`: Minor deviations
- `medium`: Noticeable changes
- `high`: Significant drift requiring attention
- `critical`: Urgent action needed

### 4. **Storage** (`storage.py`)
Persistent storage for observability data:

- **In-memory cache**: Fast access to recent data (last 100 requests)
- **File-based storage**: JSONL files organized by date
- **CloudWatch integration**: Automatic metric publishing to AWS CloudWatch
- **Automatic cleanup**: Configurable retention period
- **Thread-safe**: Supports concurrent access

### 5. **CloudWatch Publisher** (`cloudwatch_publisher.py`) 🆕
Publishes metrics to AWS CloudWatch:

- **Request metrics**: Execution time, tokens, cost, success rate
- **Agent metrics**: Per-agent performance and costs
- **Drift metrics**: Drift detection and severity
- **AI analysis metrics**: Quality scores and efficiency
- **Automatic batching**: Efficient metric publishing

### 6. **CloudWatch Dashboard** (`cloudwatch_dashboard.py`) 🆕
Creates comprehensive CloudWatch dashboards:

- **Pre-built widgets**: 20+ metric visualizations
- **Alarm management**: Create CloudWatch alarms for critical metrics
- **Multi-region support**: Deploy in any AWS region
- **CLI and API**: Multiple ways to manage dashboards

### 7. **Middleware** (`middleware.py`)
Integration layer that orchestrates all components:

- Automatic tracking initialization
- Agent execution wrapping
- Request lifecycle management
- Drift detection scheduling
- Summary generation

## 🚀 Usage

### Basic Usage

```python
from observability.middleware import get_observability_middleware

# Initialize observability
observability = get_observability_middleware(enable_ai_analysis=True)

# Start tracking a request
request_id = observability.start_request_tracking(
    requested_item="Aspirin 500mg",
    country="CO",
    urgency="high"
)

# ... agent executions happen automatically via wrapper ...

# Finalize and get report
report = observability.finalize_request(
    strategy="fast",
    recommendations_count=3,
    success=True
)
```

### Wrapping Agents

```python
from observability.agent_wrapper import with_observability

@with_observability("my_agent", model_name="bedrock/...")
def my_agent(state: State) -> State:
    # Your agent logic
    return state
```

### API Endpoints

#### Get Summary
```bash
GET /api/v1/observability/summary?hours=24
```
Returns aggregated metrics for the specified time period.

#### Get Recent Metrics
```bash
GET /api/v1/observability/metrics/recent?limit=50
```
Returns detailed metrics for recent requests.

#### Get Specific Request
```bash
GET /api/v1/observability/metrics/{request_id}
```
Returns complete observability data for a specific request.

#### Drift Alerts
```bash
GET /api/v1/observability/drift/alerts
```
Returns recent drift detection alerts with severity levels.

#### Drift History
```bash
GET /api/v1/observability/drift/history?limit=20
```
Returns historical drift analysis with entropy and KS test results.

#### AI Analyses
```bash
GET /api/v1/observability/analyses/recent?limit=20
```
Returns AI-powered analysis results (quality, reasoning, performance).

#### Set Baseline
```bash
POST /api/v1/observability/drift/set-baseline?num_samples=100
```
Manually establishes a new baseline for drift detection.

### CloudWatch Endpoints 🆕

#### CloudWatch Status
```bash
GET /api/v1/observability/cloudwatch/status
```
Get CloudWatch integration status and configuration.

#### Test CloudWatch Connection
```bash
GET /api/v1/observability/cloudwatch/test
```
Test CloudWatch connection by publishing a test metric.

#### Setup CloudWatch
```bash
POST /api/v1/observability/cloudwatch/setup
```
Create CloudWatch dashboard and alarms. Request body:
```json
{
  "create_dashboard": true,
  "create_alarms": false,
  "region_name": "us-east-1"
}
```

## 📈 Metrics Tracked

### Request-Level Metrics
- Request ID and timestamp
- Total execution time (ms)
- Total tokens used
- Total cost (USD)
- Strategy applied
- Number of recommendations
- Success status
- List of agents executed

### Agent-Level Metrics
- Agent name and timestamp
- Execution time (ms)
- Input/output tokens
- Estimated cost
- Model used
- Success/failure status
- Input/output text samples

### Drift Metrics
- Character entropy (baseline vs current)
- Word entropy (baseline vs current)
- KS test statistics for:
  - Execution times
  - Token usage
  - Costs
- Statistical summaries (means, distributions)

## 🎯 AI Analysis Output

### Text Quality Report
```json
{
  "coherence_score": 8.5,
  "completeness_score": 9.0,
  "clarity_score": 8.0,
  "professional_score": 9.5,
  "overall_score": 8.75,
  "issues": ["Minor grammatical inconsistency"],
  "strengths": ["Clear structure", "Professional tone"],
  "recommendation": "Excellent output quality"
}
```

### Reasoning Analysis
```json
{
  "logic_score": 9.0,
  "appropriateness_score": 8.5,
  "justification_score": 8.0,
  "consistency_score": 9.0,
  "overall_reasoning_score": 8.6,
  "reasoning_explanation": "Sound logic with well-justified decisions",
  "potential_issues": [],
  "confidence_level": "high"
}
```

### Drift Detection
```json
{
  "drift_detected": true,
  "drift_indicators": [
    "Text entropy changed by 18.2%",
    "Execution time distribution has drifted"
  ],
  "entropy_analysis": {
    "baseline_char_entropy": 4.52,
    "recent_char_entropy": 5.34,
    "char_entropy_change_pct": 18.2
  },
  "ks_tests": {
    "execution_time": {
      "statistic": 0.32,
      "p_value": 0.023,
      "drift_detected": true,
      "confidence": "medium"
    }
  },
  "recommendations": [
    "⚠️ Performance degradation: Average execution time increased by 25.3%"
  ]
}
```

## ⚙️ Configuration

### Enable/Disable Features

In API requests:
```json
{
  "requested_item": "Aspirin 500mg",
  "country": "CO",
  "enable_observability": true,
  "enable_ai_analysis": false
}
```

**Note:** AI analysis is more expensive as it makes additional LLM calls to analyze outputs.

### CloudWatch Configuration 🆕

Enable CloudWatch metrics publishing:

```bash
# Environment variables
export ENABLE_CLOUDWATCH_METRICS=true
export AWS_DEFAULT_REGION=us-east-1

# AWS credentials (if not using IAM role)
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
```

Or configure programmatically:
```python
from observability.middleware import get_observability_middleware

observability = get_observability_middleware(
    enable_ai_analysis=True,
    enable_cloudwatch=True,
    cloudwatch_region='us-east-1'
)
```

### Storage Configuration

Default storage directory: `./observability_data/`

Configure in code:
```python
from observability.storage import ObservabilityStorage

storage = ObservabilityStorage(
    storage_dir="custom_path",
    enable_cloudwatch=True,
    cloudwatch_region="us-east-1"
)
```

### Cleanup Old Data

```python
# Remove files older than 30 days
storage.cleanup_old_files(days_to_keep=30)
```

## 📊 Monitoring Best Practices

1. **Establish Baseline**: Run 50-100 requests before enabling drift detection
2. **Set Alerts**: Monitor drift alerts endpoint for critical issues
3. **Review Costs**: Check cost trends to optimize token usage
4. **Analyze Quality**: Use AI analysis periodically (not every request) to verify output quality
5. **Update Baseline**: After major system changes, reset the drift baseline
6. **Track Trends**: Monitor execution times for performance degradation

## 🔍 Troubleshooting

### High Costs
- Check `total_cost_usd` in metrics
- Review token usage per agent
- Disable AI analysis if not needed
- Optimize agent prompts to reduce tokens

### Drift Detected
- Review drift indicators
- Check for model updates or changes
- Verify input data quality hasn't changed
- Consider resetting baseline if changes are intentional

### Missing Metrics
- Verify `enable_observability=True` in requests
- Check that agents are wrapped with `@with_observability`
- Ensure storage directory is writable

## 📚 Dependencies

- `tiktoken>=0.5.0`: Token counting
- `scipy>=1.11.0`: Statistical tests (KS test)
- `numpy>=1.24.0`: Numerical operations
- `boto3>=1.26.0`: AWS CloudWatch integration (optional)

## 🎓 Architecture

```
Request → Middleware → Wrapped Agents → Metrics Collector
                                            ↓
                                    Storage (Memory + Disk)
                                            ↓
                        ┌───────────────────┼────────────────────┬──────────────────┐
                        ↓                   ↓                    ↓                  ↓
                  AI Analyzer        Drift Detector      Summary Stats    CloudWatch Publisher 🆕
                        ↓                   ↓                    ↓                  ↓
                    Reports            Alerts            Dashboards         AWS CloudWatch
                                                                                   ↓
                                                                      CloudWatch Dashboard & Alarms
```

## 📝 License

Part of the Multi-Agent Pharmaceutical Substitute Recommender System.

