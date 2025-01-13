"""Advanced analytics and insights for AI Coder."""
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class AnalyticsEvent:
    timestamp: datetime
    event_type: str
    user_id: str
    data: Dict
    session_id: str

class UsagePatternAnalyzer:
    """Analyzes user behavior and usage patterns."""
    
    def __init__(self):
        self.patterns = defaultdict(int)
    
    def analyze_language_preferences(self, events: List[AnalyticsEvent]) -> Dict:
        """Analyze most used programming languages."""
        language_usage = defaultdict(int)
        language_success = defaultdict(lambda: {"success": 0, "total": 0})
        
        for event in events:
            if event.event_type == "code_generation":
                lang = event.data.get("language")
                if lang:
                    language_usage[lang] += 1
                    if event.data.get("success", False):
                        language_success[lang]["success"] += 1
                    language_success[lang]["total"] += 1
        
        return {
            "most_used": dict(sorted(language_usage.items(), 
                                   key=lambda x: x[1], reverse=True)),
            "success_rates": {
                lang: {"rate": stats["success"] / stats["total"] * 100, 
                      "total": stats["total"]}
                for lang, stats in language_success.items()
            }
        }
    
    def analyze_model_performance(self, events: List[AnalyticsEvent]) -> Dict:
        """Analyze AI model performance and costs."""
        model_stats = defaultdict(lambda: {
            "requests": 0,
            "tokens": 0,
            "cost": 0,
            "avg_response_time": 0,
            "success_rate": 0,
            "total_time": 0
        })
        
        for event in events:
            if event.event_type == "model_usage":
                model = event.data.get("model")
                if model:
                    stats = model_stats[model]
                    stats["requests"] += 1
                    stats["tokens"] += event.data.get("total_tokens", 0)
                    stats["cost"] += event.data.get("cost", 0)
                    stats["total_time"] += event.data.get("response_time", 0)
                    if event.data.get("success", False):
                        stats["success_rate"] += 1
        
        # Calculate averages
        for model, stats in model_stats.items():
            if stats["requests"] > 0:
                stats["avg_response_time"] = stats["total_time"] / stats["requests"]
                stats["success_rate"] = (stats["success_rate"] / stats["requests"]) * 100
                stats["avg_tokens_per_request"] = stats["tokens"] / stats["requests"]
                stats["avg_cost_per_request"] = stats["cost"] / stats["requests"]
        
        return dict(model_stats)
    
    def analyze_feature_usage(self, events: List[AnalyticsEvent]) -> Dict:
        """Analyze feature usage patterns."""
        feature_usage = defaultdict(lambda: {
            "total_uses": 0,
            "unique_users": set(),
            "avg_duration": 0,
            "total_duration": 0,
            "success_rate": 0,
            "successful_uses": 0
        })
        
        for event in events:
            if event.event_type == "feature_usage":
                feature = event.data.get("feature")
                if feature:
                    stats = feature_usage[feature]
                    stats["total_uses"] += 1
                    stats["unique_users"].add(event.user_id)
                    duration = event.data.get("duration", 0)
                    stats["total_duration"] += duration
                    if event.data.get("success", False):
                        stats["successful_uses"] += 1
        
        # Calculate averages
        result = {}
        for feature, stats in feature_usage.items():
            result[feature] = {
                "total_uses": stats["total_uses"],
                "unique_users": len(stats["unique_users"]),
                "avg_duration": stats["total_duration"] / stats["total_uses"] if stats["total_uses"] > 0 else 0,
                "success_rate": (stats["successful_uses"] / stats["total_uses"] * 100) if stats["total_uses"] > 0 else 0
            }
        
        return result

class UsageAnalytics:
    """Comprehensive usage analytics and reporting."""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.events: List[AnalyticsEvent] = []
        self.pattern_analyzer = UsagePatternAnalyzer()
        self.session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        return f"{self.user_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def track_event(self, event_type: str, data: Dict):
        """Track a new analytics event."""
        event = AnalyticsEvent(
            timestamp=datetime.now(),
            event_type=event_type,
            user_id=self.user_id,
            data=data,
            session_id=self.session_id
        )
        self.events.append(event)
    
    def get_usage_insights(self, days: int = 30) -> Dict:
        """Get comprehensive usage insights."""
        cutoff = datetime.now() - timedelta(days=days)
        recent_events = [e for e in self.events if e.timestamp >= cutoff]
        
        return {
            "language_insights": self.pattern_analyzer.analyze_language_preferences(recent_events),
            "model_performance": self.pattern_analyzer.analyze_model_performance(recent_events),
            "feature_usage": self.pattern_analyzer.analyze_feature_usage(recent_events),
            "usage_patterns": self._analyze_usage_patterns(recent_events),
            "cost_analysis": self._analyze_costs(recent_events),
            "productivity_metrics": self._calculate_productivity_metrics(recent_events)
        }
    
    def _analyze_usage_patterns(self, events: List[AnalyticsEvent]) -> Dict:
        """Analyze usage patterns and trends."""
        hourly_usage = defaultdict(int)
        daily_usage = defaultdict(int)
        session_lengths = []
        
        current_session = None
        session_start = None
        
        for event in sorted(events, key=lambda x: x.timestamp):
            # Track hourly and daily usage
            hour = event.timestamp.strftime("%H")
            day = event.timestamp.strftime("%A")
            hourly_usage[hour] += 1
            daily_usage[day] += 1
            
            # Track session lengths
            if current_session != event.session_id:
                if session_start:
                    session_length = (event.timestamp - session_start).total_seconds() / 60
                    session_lengths.append(session_length)
                current_session = event.session_id
                session_start = event.timestamp
        
        return {
            "peak_hours": dict(sorted(hourly_usage.items(), key=lambda x: x[1], reverse=True)[:5]),
            "busy_days": dict(sorted(daily_usage.items(), key=lambda x: x[1], reverse=True)),
            "avg_session_length": sum(session_lengths) / len(session_lengths) if session_lengths else 0,
            "total_sessions": len(set(e.session_id for e in events))
        }
    
    def _analyze_costs(self, events: List[AnalyticsEvent]) -> Dict:
        """Analyze cost patterns and ROI metrics."""
        daily_costs = defaultdict(float)
        model_costs = defaultdict(float)
        feature_costs = defaultdict(float)
        
        for event in events:
            date = event.timestamp.strftime("%Y-%m-%d")
            cost = event.data.get("cost", 0)
            
            daily_costs[date] += cost
            if "model" in event.data:
                model_costs[event.data["model"]] += cost
            if "feature" in event.data:
                feature_costs[event.data["feature"]] += cost
        
        return {
            "daily_spending": dict(daily_costs),
            "cost_by_model": dict(model_costs),
            "cost_by_feature": dict(feature_costs),
            "total_cost": sum(daily_costs.values()),
            "avg_daily_cost": sum(daily_costs.values()) / len(daily_costs) if daily_costs else 0
        }
    
    def _calculate_productivity_metrics(self, events: List[AnalyticsEvent]) -> Dict:
        """Calculate productivity and efficiency metrics."""
        code_generations = 0
        successful_generations = 0
        total_tokens = 0
        total_time = 0
        code_quality_scores = []
        
        for event in events:
            if event.event_type == "code_generation":
                code_generations += 1
                if event.data.get("success", False):
                    successful_generations += 1
                total_tokens += event.data.get("total_tokens", 0)
                total_time += event.data.get("duration", 0)
                if "quality_score" in event.data:
                    code_quality_scores.append(event.data["quality_score"])
        
        return {
            "success_rate": (successful_generations / code_generations * 100) if code_generations > 0 else 0,
            "avg_generation_time": total_time / code_generations if code_generations > 0 else 0,
            "tokens_per_generation": total_tokens / code_generations if code_generations > 0 else 0,
            "avg_code_quality": sum(code_quality_scores) / len(code_quality_scores) if code_quality_scores else 0,
            "total_generations": code_generations,
            "time_saved_estimate": total_time * 3  # Assuming each generation saves 3x the time
        }
    
    def get_recommendations(self) -> List[Dict]:
        """Get personalized recommendations based on usage patterns."""
        insights = self.get_usage_insights()
        recommendations = []
        
        # Model usage recommendations
        model_perf = insights["model_performance"]
        for model, stats in model_perf.items():
            if stats["success_rate"] < 80:
                recommendations.append({
                    "type": "model_usage",
                    "priority": "high",
                    "message": f"Consider using alternative models for {model} tasks (current success rate: {stats['success_rate']:.1f}%)",
                    "action": "try_alternative_model"
                })
        
        # Cost optimization
        costs = insights["cost_analysis"]
        if costs["avg_daily_cost"] > 50:  # Threshold for high daily cost
            recommendations.append({
                "type": "cost_optimization",
                "priority": "high",
                "message": "Daily costs are high. Consider using more efficient models or implementing caching",
                "action": "optimize_costs"
            })
        
        # Feature usage optimization
        feature_usage = insights["feature_usage"]
        for feature, stats in feature_usage.items():
            if stats["success_rate"] < 70:
                recommendations.append({
                    "type": "feature_optimization",
                    "priority": "medium",
                    "message": f"Users are struggling with {feature}. Consider adding more documentation or tutorials",
                    "action": "improve_feature_docs"
                })
        
        return recommendations
