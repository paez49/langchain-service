"""
AI Observability Analyzer - Uses AI to analyze agent outputs, reasoning quality, and text quality
"""

from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from config import llm
import json


class AIObservabilityAnalyzer:
    """
    AI-powered analyzer for observability metrics
    
    Analyzes:
    - Quality of generated text (coherence, accuracy, completeness)
    - Reasoning analysis (logic, decision quality)
    - Agent performance patterns
    - Anomaly detection
    """
    
    def __init__(self):
        self.llm = llm
        
    def analyze_text_quality(self, text: str, context: str = "") -> Dict[str, Any]:
        """
        Analyze the quality of generated text
        
        Returns scores for:
        - Coherence (0-10)
        - Completeness (0-10)
        - Clarity (0-10)
        - Professional tone (0-10)
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert AI quality analyst. Analyze the quality of AI-generated text "
             "and provide scores from 0-10 for the following dimensions:\n"
             "- Coherence: How logically structured and consistent is the text?\n"
             "- Completeness: Does it fully address the requirements?\n"
             "- Clarity: How clear and understandable is it?\n"
             "- Professional: Does it maintain appropriate professional tone?\n\n"
             "Return ONLY a JSON object with this exact format:\n"
             "{{\n"
             '  "coherence_score": <0-10>,\n'
             '  "completeness_score": <0-10>,\n'
             '  "clarity_score": <0-10>,\n'
             '  "professional_score": <0-10>,\n'
             '  "overall_score": <0-10>,\n'
             '  "issues": ["issue1", "issue2"],\n'
             '  "strengths": ["strength1", "strength2"],\n'
             '  "recommendation": "brief recommendation"\n'
             "}}"),
            ("user", 
             f"Context: {context}\n\n"
             f"Text to analyze:\n{text}\n\n"
             "Provide your analysis in JSON format:")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({}).content
            
            # Extract JSON from response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                analysis = json.loads(json_str)
            else:
                # Fallback if JSON extraction fails
                analysis = {
                    "coherence_score": 7,
                    "completeness_score": 7,
                    "clarity_score": 7,
                    "professional_score": 7,
                    "overall_score": 7,
                    "issues": ["Unable to fully analyze"],
                    "strengths": ["Response generated"],
                    "recommendation": "Manual review recommended"
                }
            
            return analysis
            
        except Exception as e:
            return {
                "coherence_score": 5,
                "completeness_score": 5,
                "clarity_score": 5,
                "professional_score": 5,
                "overall_score": 5,
                "issues": [f"Analysis error: {str(e)}"],
                "strengths": [],
                "recommendation": "Error during analysis"
            }
    
    def analyze_reasoning(self, agent_name: str, input_data: str, output_data: str, 
                         decision_made: str = "") -> Dict[str, Any]:
        """
        Analyze the reasoning quality of an agent's decision
        
        Returns:
        - Logic quality score (0-10)
        - Decision appropriateness (0-10)
        - Reasoning explanation
        - Potential biases or issues
        """
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert in analyzing AI reasoning and decision-making processes. "
             "Evaluate the agent's reasoning quality based on:\n"
             "- Logic: Is the reasoning logically sound?\n"
             "- Appropriateness: Is the decision appropriate for the input?\n"
             "- Justification: Is the reasoning well-explained?\n"
             "- Consistency: Is the decision consistent with best practices?\n\n"
             "Return ONLY a JSON object with this format:\n"
             "{{\n"
             '  "logic_score": <0-10>,\n'
             '  "appropriateness_score": <0-10>,\n'
             '  "justification_score": <0-10>,\n'
             '  "consistency_score": <0-10>,\n'
             '  "overall_reasoning_score": <0-10>,\n'
             '  "reasoning_explanation": "brief explanation",\n'
             '  "potential_issues": ["issue1", "issue2"],\n'
             '  "confidence_level": "high|medium|low"\n'
             "}}"),
            ("user", 
             f"Agent: {agent_name}\n\n"
             f"Input:\n{input_data}\n\n"
             f"Output:\n{output_data}\n\n"
             f"Decision Made: {decision_made}\n\n"
             "Analyze the reasoning quality in JSON format:")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({}).content
            
            # Extract JSON
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                analysis = json.loads(json_str)
            else:
                analysis = {
                    "logic_score": 7,
                    "appropriateness_score": 7,
                    "justification_score": 7,
                    "consistency_score": 7,
                    "overall_reasoning_score": 7,
                    "reasoning_explanation": "Standard reasoning applied",
                    "potential_issues": [],
                    "confidence_level": "medium"
                }
            
            return analysis
            
        except Exception as e:
            return {
                "logic_score": 5,
                "appropriateness_score": 5,
                "justification_score": 5,
                "consistency_score": 5,
                "overall_reasoning_score": 5,
                "reasoning_explanation": f"Analysis error: {str(e)}",
                "potential_issues": ["Could not complete analysis"],
                "confidence_level": "low"
            }
    
    def analyze_request_performance(self, request_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze overall request performance and identify patterns or issues
        """
        
        agents_data = "\n".join([
            f"- {am['agent_name']}: {am['execution_time_ms']:.0f}ms, "
            f"{am['total_tokens']} tokens, ${am['estimated_cost_usd']:.4f}"
            for am in request_metrics.get("agent_metrics", [])
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an expert in analyzing AI system performance. "
             "Review the execution metrics and provide insights about:\n"
             "- Performance bottlenecks\n"
             "- Cost optimization opportunities\n"
             "- Efficiency improvements\n"
             "- Unusual patterns or anomalies\n\n"
             "Return ONLY a JSON object:\n"
             "{{\n"
             '  "performance_score": <0-10>,\n'
             '  "cost_efficiency_score": <0-10>,\n'
             '  "bottlenecks": ["bottleneck1"],\n'
             '  "optimization_suggestions": ["suggestion1"],\n'
             '  "anomalies_detected": ["anomaly1"],\n'
             '  "summary": "brief summary"\n'
             "}}"),
            ("user", 
             f"Request Metrics:\n"
             f"- Total Time: {request_metrics.get('total_execution_time_ms', 0):.0f}ms\n"
             f"- Total Tokens: {request_metrics.get('total_tokens', 0)}\n"
             f"- Total Cost: ${request_metrics.get('total_cost_usd', 0):.4f}\n"
             f"- Strategy: {request_metrics.get('strategy', 'unknown')}\n"
             f"- Success: {request_metrics.get('success', False)}\n\n"
             f"Agent Executions:\n{agents_data}\n\n"
             "Analyze in JSON format:")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({}).content
            
            # Extract JSON
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                analysis = json.loads(json_str)
            else:
                analysis = {
                    "performance_score": 7,
                    "cost_efficiency_score": 7,
                    "bottlenecks": [],
                    "optimization_suggestions": [],
                    "anomalies_detected": [],
                    "summary": "Standard performance"
                }
            
            return analysis
            
        except Exception as e:
            return {
                "performance_score": 5,
                "cost_efficiency_score": 5,
                "bottlenecks": [],
                "optimization_suggestions": [],
                "anomalies_detected": [f"Analysis error: {str(e)}"],
                "summary": "Could not complete performance analysis"
            }
    
    def generate_comprehensive_report(
        self,
        request_metrics: Dict[str, Any],
        text_quality_results: List[Dict[str, Any]],
        reasoning_results: List[Dict[str, Any]],
        performance_analysis: Dict[str, Any]
    ) -> str:
        """
        Generate a comprehensive observability report using AI
        """
        text_quality_json = json.dumps(text_quality_results, indent=2)
        reasoning_json = json.dumps(reasoning_results, indent=2)
        performance_json = json.dumps(performance_analysis, indent=2)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", 
             "You are an AI Observability expert. Generate a comprehensive, actionable report "
             "summarizing the AI system's performance, quality, and areas for improvement."),
            ("user", 
             f"Generate an observability report for request {request_metrics.get('request_id', 'N/A')}:\n\n"
             f"**Performance Metrics:**\n"
             f"- Total execution time: {request_metrics.get('total_execution_time_ms', 0):.0f}ms\n"
             f"- Total tokens used: {request_metrics.get('total_tokens', 0)}\n"
             f"- Total cost: ${request_metrics.get('total_cost_usd', 0):.4f}\n"
             f"- Agents executed: {len(request_metrics.get('agent_metrics', []))}\n\n"
             f"**Quality Analysis:**\n"
             "{text_quality_json}\n\n"
             f"**Reasoning Analysis:**\n"
             "{reasoning_json}\n\n"
             f"**Performance Analysis:**\n"
             "{performance_json}\n\n"
             "Provide a clear, structured report with key findings and recommendations.")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "text_quality_json": text_quality_json,
                "reasoning_json": reasoning_json,
                "performance_json": performance_json,
            }).content
            return response
        except Exception as e:
            return f"Error generating comprehensive report: {str(e)}"

