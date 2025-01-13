"""Track and manage user usage and costs."""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class UsageRecord:
    timestamp: datetime
    model: str
    input_tokens: int
    output_tokens: int
    request_type: str  # 'code', 'analysis', 'docs', etc.
    cost: float


class ModelCosts:
    """Model-specific costs and limits."""

    COSTS = {
        # OpenAI Models
        "gpt-4-turbo-preview": {
            "input": 0.01,  # per 1K tokens
            "output": 0.03,
            "context_length": 128000,
        },
        "gpt-4": {"input": 0.03, "output": 0.06, "context_length": 8192},
        "gpt-3.5-turbo-16k": {"input": 0.001, "output": 0.002, "context_length": 16384},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015, "context_length": 4096},
        # Anthropic Models
        "claude-3-opus-20240229": {
            "input": 0.015,
            "output": 0.075,
            "context_length": 200000,
        },
        "claude-3-sonnet-20240229": {
            "input": 0.003,
            "output": 0.015,
            "context_length": 200000,
        },
        "claude-2.1": {"input": 0.008, "output": 0.024, "context_length": 100000},
    }

    @classmethod
    def calculate_cost(cls, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate the cost for a specific usage."""
        if model not in cls.COSTS:
            raise ValueError(f"Unknown model: {model}")

        costs = cls.COSTS[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        return input_cost + output_cost

    @classmethod
    def get_context_length(cls, model: str) -> int:
        """Get the context length for a model."""
        return cls.COSTS[model]["context_length"]


class UsageTracker:
    """Track and manage user usage."""

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.usage_records: List[UsageRecord] = []
        self.last_reset = datetime.now()

    def add_usage(self, model: str, input_tokens: int, output_tokens: int, request_type: str) -> float:
        """Add a usage record and return the cost."""
        cost = ModelCosts.calculate_cost(model, input_tokens, output_tokens)

        record = UsageRecord(
            timestamp=datetime.now(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            request_type=request_type,
            cost=cost,
        )

        self.usage_records.append(record)
        return cost

    def get_monthly_usage(self) -> Dict:
        """Get usage statistics for the current month."""
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_records = [r for r in self.usage_records if r.timestamp >= month_start]

        total_cost = sum(r.cost for r in monthly_records)
        total_requests = len(monthly_records)
        total_tokens = sum(r.input_tokens + r.output_tokens for r in monthly_records)

        usage_by_model = {}
        for record in monthly_records:
            if record.model not in usage_by_model:
                usage_by_model[record.model] = {"requests": 0, "tokens": 0, "cost": 0}
            usage_by_model[record.model]["requests"] += 1
            usage_by_model[record.model]["tokens"] += record.input_tokens + record.output_tokens
            usage_by_model[record.model]["cost"] += record.cost

        return {
            "total_cost": total_cost,
            "total_requests": total_requests,
            "total_tokens": total_tokens,
            "usage_by_model": usage_by_model,
        }

    def check_limits(self, plan_limits: Dict) -> Dict:
        """Check if the user has exceeded any limits."""
        monthly_usage = self.get_monthly_usage()

        exceeded_limits = {}
        if monthly_usage["total_requests"] >= plan_limits.get("monthly_requests", float("inf")):
            exceeded_limits["requests"] = True

        if monthly_usage["total_tokens"] >= plan_limits.get("monthly_tokens", float("inf")):
            exceeded_limits["tokens"] = True

        if monthly_usage["total_cost"] >= plan_limits.get("monthly_cost", float("inf")):
            exceeded_limits["cost"] = True

        return exceeded_limits

    def get_smart_model_selection(self, request_type: str, code_complexity: float) -> str:
        """Select the most cost-effective model based on request type and complexity."""
        if request_type == "code":
            if code_complexity > 0.8:
                return "gpt-4-turbo-preview"
            elif code_complexity > 0.6:
                return "claude-3-sonnet-20240229"
            else:
                return "gpt-3.5-turbo-16k"
        elif request_type == "analysis":
            if code_complexity > 0.7:
                return "claude-3-opus-20240229"
            else:
                return "claude-3-sonnet-20240229"
        else:  # docs, schema, etc.
            return "gpt-3.5-turbo-16k"

    def estimate_complexity(self, prompt: str) -> float:
        """Estimate code complexity based on prompt analysis."""
        # Simple heuristic - can be enhanced with ML
        complexity_indicators = [
            "optimization",
            "algorithm",
            "complex",
            "scalable",
            "enterprise",
            "security",
            "concurrent",
            "async",
            "distributed",
            "real-time",
            "performance",
        ]

        count = sum(1 for indicator in complexity_indicators if indicator in prompt.lower())
        return min(1.0, count / len(complexity_indicators))

    def get_usage_alerts(self) -> List[Dict]:
        """Get usage alerts for the user."""
        monthly_usage = self.get_monthly_usage()
        alerts = []

        # Cost alerts
        if monthly_usage["total_cost"] > 50:
            alerts.append(
                {
                    "type": "cost",
                    "level": "warning",
                    "message": f"Monthly cost (${monthly_usage['total_cost']:.2f}) is high",
                }
            )

        # Request alerts
        if monthly_usage["total_requests"] > 80:
            alerts.append(
                {
                    "type": "requests",
                    "level": "warning",
                    "message": f"Used {monthly_usage['total_requests']}/100 monthly requests",
                }
            )

        return alerts
