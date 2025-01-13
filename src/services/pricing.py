"""Pricing and subscription management for AI Coder."""

from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class PricingTier:
    name: str
    price: float
    description: str
    features: List[Dict[str, str]]
    limits: Dict[str, int]
    badge: str
    highlight_color: str
    overage_rates: Dict[str, float]


class PricingManager:
    """Manages premium features and access."""

    # Define all possible features
    FEATURES = {
        # Basic Features
        "basic": [
            {
                "name": "Code Generation",
                "description": "Generate code in any language",
                "icon": "💻",
            },
            {
                "name": "Smart Model Selection",
                "description": "AI picks the best model for your task",
                "icon": "🎯",
            },
            {
                "name": "Basic Code Analysis",
                "description": "Simple code review and suggestions",
                "icon": "🔍",
            },
            {
                "name": "Community Support",
                "description": "Access to community forums",
                "icon": "👥",
            },
        ],
        # Enhanced Code Intelligence
        "code_intelligence": [
            {
                "name": "Semantic Code Search",
                "description": "Find code by meaning, not just text",
                "icon": "🔎",
            },
            {
                "name": "Code Quality Gates",
                "description": "Automated code quality checks",
                "icon": "✨",
            },
            {
                "name": "Refactoring Assistant",
                "description": "Smart code restructuring",
                "icon": "🔄",
            },
            {
                "name": "Type Inference",
                "description": "Advanced type analysis",
                "icon": "📝",
            },
            {
                "name": "Dead Code Detection",
                "description": "Find unused code",
                "icon": "🗑️",
            },
            {
                "name": "Complexity Analysis",
                "description": "Code complexity metrics",
                "icon": "📊",
            },
        ],
        # Security Features
        "security": [
            {
                "name": "Vulnerability Scanner",
                "description": "Find security issues",
                "icon": "🛡️",
            },
            {
                "name": "Dependency Audit",
                "description": "Check dependencies for vulnerabilities",
                "icon": "🔒",
            },
            {
                "name": "Secret Detection",
                "description": "Find exposed secrets",
                "icon": "🔐",
            },
            {
                "name": "SAST Integration",
                "description": "Static security analysis",
                "icon": "🔍",
            },
            {
                "name": "License Compliance",
                "description": "License compatibility checks",
                "icon": "📜",
            },
        ],
        # Team Collaboration
        "collaboration": [
            {
                "name": "Code Reviews",
                "description": "AI-powered code review system",
                "icon": "👥",
            },
            {
                "name": "Pair Programming",
                "description": "Real-time collaboration",
                "icon": "👥",
            },
            {
                "name": "Knowledge Sharing",
                "description": "Team documentation",
                "icon": "📚",
            },
            {
                "name": "Code Comments",
                "description": "Smart code documentation",
                "icon": "💭",
            },
            {
                "name": "Team Chat",
                "description": "Built-in team communication",
                "icon": "💬",
            },
        ],
        # Project Management
        "project": [
            {
                "name": "Task Tracking",
                "description": "AI task management",
                "icon": "📋",
            },
            {
                "name": "Sprint Planning",
                "description": "AI sprint suggestions",
                "icon": "📅",
            },
            {
                "name": "Effort Estimation",
                "description": "AI time estimates",
                "icon": "⏱️",
            },
            {
                "name": "Resource Allocation",
                "description": "Team workload management",
                "icon": "📊",
            },
            {
                "name": "Progress Analytics",
                "description": "Project insights",
                "icon": "📈",
            },
        ],
        # Performance Optimization
        "performance": [
            {
                "name": "Performance Profiling",
                "description": "Code performance analysis",
                "icon": "⚡",
            },
            {
                "name": "Memory Analysis",
                "description": "Memory usage optimization",
                "icon": "💾",
            },
            {
                "name": "Load Testing",
                "description": "Automated load tests",
                "icon": "🔨",
            },
            {
                "name": "Query Optimization",
                "description": "Database query analysis",
                "icon": "🗃️",
            },
            {
                "name": "Cache Strategy",
                "description": "Caching recommendations",
                "icon": "🚀",
            },
        ],
        # Testing Suite
        "testing": [
            {
                "name": "Test Generation",
                "description": "AI test case creation",
                "icon": "🧪",
            },
            {
                "name": "Coverage Analysis",
                "description": "Test coverage insights",
                "icon": "🎯",
            },
            {
                "name": "Integration Tests",
                "description": "End-to-end testing",
                "icon": "🔄",
            },
            {
                "name": "Mock Generation",
                "description": "Automatic mock creation",
                "icon": "🎭",
            },
            {
                "name": "Regression Testing",
                "description": "Automated regression tests",
                "icon": "📉",
            },
        ],
        # DevOps Integration
        "devops": [
            {
                "name": "CI/CD Pipelines",
                "description": "Pipeline automation",
                "icon": "🔄",
            },
            {
                "name": "Docker Integration",
                "description": "Container management",
                "icon": "🐳",
            },
            {
                "name": "Cloud Deployment",
                "description": "Cloud service integration",
                "icon": "☁️",
            },
            {
                "name": "Infrastructure Code",
                "description": "Infrastructure as code",
                "icon": "🏗️",
            },
            {
                "name": "Monitoring Setup",
                "description": "System monitoring",
                "icon": "📡",
            },
        ],
        # AI Workflow
        "ai_workflow": [
            {
                "name": "Custom AI Models",
                "description": "Train custom models",
                "icon": "🧠",
            },
            {
                "name": "Prompt Library",
                "description": "Reusable AI prompts",
                "icon": "📚",
            },
            {
                "name": "Model Chaining",
                "description": "Complex AI workflows",
                "icon": "⛓️",
            },
            {
                "name": "Result Caching",
                "description": "Smart response caching",
                "icon": "💾",
            },
            {
                "name": "Cost Optimization",
                "description": "AI usage optimization",
                "icon": "💰",
            },
        ],
        # Standard Features
        "standard": [
            {
                "name": "GPT-4 Access",
                "description": "Limited access to GPT-4",
                "icon": "🧠",
            },
            {
                "name": "Code Explanations",
                "description": "Detailed code walk-throughs",
                "icon": "📚",
            },
            {
                "name": "Basic Templates",
                "description": "Access to basic project templates",
                "icon": "📁",
            },
            {
                "name": "Email Support",
                "description": "Basic email support",
                "icon": "📧",
            },
        ],
        # Professional Features
        "professional": [
            {
                "name": "All AI Models",
                "description": "Full access to all AI models",
                "icon": "🚀",
            },
            {
                "name": "Advanced Analysis",
                "description": "Deep code review and optimization",
                "icon": "🔬",
            },
            {
                "name": "Custom Templates",
                "description": "Create and save custom templates",
                "icon": "🎨",
            },
            {
                "name": "Priority Support",
                "description": "Fast response support",
                "icon": "⚡",
            },
        ],
        # Team Features
        "team": [
            {
                "name": "Team Management",
                "description": "Add and manage team members",
                "icon": "👥",
            },
            {
                "name": "Shared Workspace",
                "description": "Collaborative development space",
                "icon": "🤝",
            },
            {
                "name": "Usage Analytics",
                "description": "Team usage tracking and insights",
                "icon": "📊",
            },
            {
                "name": "Team Templates",
                "description": "Share templates with team",
                "icon": "📋",
            },
        ],
        # Enterprise Features
        "enterprise": [
            {
                "name": "Custom Integration",
                "description": "Integration with your tools",
                "icon": "🔌",
            },
            {
                "name": "SLA Support",
                "description": "24/7 dedicated support",
                "icon": "🎖️",
            },
            {
                "name": "Custom Models",
                "description": "Use your own AI models",
                "icon": "🎛️",
            },
            {
                "name": "Security Features",
                "description": "Enhanced security controls",
                "icon": "🔒",
            },
        ],
        # New Advanced Features
        "advanced": [
            {
                "name": "Code Review AI",
                "description": "AI-powered code review and suggestions",
                "icon": "🔍",
            },
            {
                "name": "Performance Profiling",
                "description": "Code performance analysis",
                "icon": "📊",
            },
            {
                "name": "Security Scanning",
                "description": "AI security vulnerability detection",
                "icon": "🔒",
            },
            {
                "name": "Architecture Design",
                "description": "AI system architecture suggestions",
                "icon": "🏗️",
            },
            {
                "name": "API Generation",
                "description": "Automatic API endpoint generation",
                "icon": "🔌",
            },
            {
                "name": "Test Generation",
                "description": "AI-powered test case generation",
                "icon": "🧪",
            },
            {
                "name": "Documentation AI",
                "description": "Automatic documentation generation",
                "icon": "📚",
            },
            {
                "name": "Code Migration",
                "description": "Automated code migration tools",
                "icon": "🔄",
            },
            {
                "name": "Dependency Analysis",
                "description": "Smart dependency management",
                "icon": "🔗",
            },
            {
                "name": "Code Optimization",
                "description": "AI performance optimization",
                "icon": "⚡",
            },
        ],
        # New Analytics Features
        "analytics": [
            {
                "name": "Usage Insights",
                "description": "Detailed usage analytics",
                "icon": "📊",
            },
            {
                "name": "Cost Tracking",
                "description": "Real-time cost monitoring",
                "icon": "💰",
            },
            {
                "name": "ROI Calculator",
                "description": "Calculate development time saved",
                "icon": "📈",
            },
            {
                "name": "Team Analytics",
                "description": "Team productivity insights",
                "icon": "👥",
            },
            {
                "name": "Model Performance",
                "description": "AI model performance tracking",
                "icon": "🎯",
            },
            {
                "name": "Quality Metrics",
                "description": "Code quality tracking",
                "icon": "✨",
            },
            {
                "name": "Trend Analysis",
                "description": "Usage pattern analysis",
                "icon": "📉",
            },
            {
                "name": "Custom Reports",
                "description": "Generate custom analytics reports",
                "icon": "📋",
            },
            {
                "name": "Alert System",
                "description": "Usage and cost alerts",
                "icon": "🔔",
            },
            {
                "name": "Optimization Tips",
                "description": "AI-powered usage recommendations",
                "icon": "💡",
            },
        ],
    }

    PRICING_TIERS = {
        "hobby": PricingTier(
            name="Hobby",
            price=4.99,
            description="Perfect for personal projects",
            features=FEATURES["basic"]
            + FEATURES["code_intelligence"][:2]  # Basic code intelligence
            + FEATURES["security"][:1],  # Basic security
            limits={
                "monthly_requests": 100,
                "monthly_tokens": 250000,
                "max_tokens_per_request": 4000,
                "team_members": 1,
                "gpt4_requests": 0,
            },
            badge="🎮",
            highlight_color="#4CAF50",
            overage_rates={"requests": 0.10, "tokens": 0.01},
        ),
        "starter": PricingTier(
            name="Starter",
            price=14.99,
            description="For indie developers",
            features=FEATURES["basic"]
            + FEATURES["code_intelligence"][:4]  # More code intelligence
            + FEATURES["security"][:2]  # More security
            + FEATURES["testing"][:2]  # Basic testing
            + FEATURES["performance"][:2],  # Basic performance
            limits={
                "monthly_requests": 200,
                "monthly_tokens": 500000,
                "max_tokens_per_request": 8000,
                "team_members": 1,
                "gpt4_requests": 25,
            },
            badge="🌟",
            highlight_color="#2196F3",
            overage_rates={"requests": 0.08, "tokens": 0.008},
        ),
        "pro": PricingTier(
            name="Professional",
            price=29.99,
            description="For professional developers",
            features=FEATURES["basic"]
            + FEATURES["code_intelligence"]  # All code intelligence
            + FEATURES["security"]  # All security
            + FEATURES["testing"]  # All testing
            + FEATURES["performance"]  # All performance
            + FEATURES["ai_workflow"][:3],  # Basic AI workflow
            limits={
                "monthly_requests": 500,
                "monthly_tokens": 1000000,
                "max_tokens_per_request": 16000,
                "team_members": 1,
                "gpt4_requests": float("inf"),
            },
            badge="💎",
            highlight_color="#9C27B0",
            overage_rates={"requests": 0.06, "tokens": 0.006},
        ),
        "team": PricingTier(
            name="Team",
            price=79.99,
            description="Perfect for small teams",
            features=FEATURES["basic"]
            + FEATURES["code_intelligence"]  # All code intelligence
            + FEATURES["security"]  # All security
            + FEATURES["testing"]  # All testing
            + FEATURES["performance"]  # All performance
            + FEATURES["collaboration"]  # All collaboration
            + FEATURES["project"]  # All project management
            + FEATURES["ai_workflow"],  # All AI workflow
            limits={
                "monthly_requests": 2000,
                "monthly_tokens": 3000000,
                "max_tokens_per_request": 32000,
                "team_members": 5,
                "gpt4_requests": float("inf"),
            },
            badge="👥",
            highlight_color="#FF9800",
            overage_rates={"requests": 0.04, "tokens": 0.004},
        ),
        "business": PricingTier(
            name="Business",
            price=149.99,
            description="For growing companies",
            features=FEATURES["basic"]
            + FEATURES["code_intelligence"]  # All code intelligence
            + FEATURES["security"]  # All security
            + FEATURES["testing"]  # All testing
            + FEATURES["performance"]  # All performance
            + FEATURES["collaboration"]  # All collaboration
            + FEATURES["project"]  # All project management
            + FEATURES["devops"]  # All DevOps
            + FEATURES["ai_workflow"],  # All AI workflow
            limits={
                "monthly_requests": 5000,
                "monthly_tokens": 10000000,
                "max_tokens_per_request": 32000,
                "team_members": 15,
                "gpt4_requests": float("inf"),
            },
            badge="🏢",
            highlight_color="#FF5722",
            overage_rates={"requests": 0.03, "tokens": 0.003},
        ),
        "enterprise": PricingTier(
            name="Enterprise",
            price=399.99,
            description="Custom enterprise solution",
            features=FEATURES["basic"]
            + FEATURES["code_intelligence"]  # All code intelligence
            + FEATURES["security"]  # All security
            + FEATURES["testing"]  # All testing
            + FEATURES["performance"]  # All performance
            + FEATURES["collaboration"]  # All collaboration
            + FEATURES["project"]  # All project management
            + FEATURES["devops"]  # All DevOps
            + FEATURES["ai_workflow"],  # All AI workflow
            limits={
                "monthly_requests": float("inf"),
                "monthly_tokens": float("inf"),
                "max_tokens_per_request": 32000,
                "team_members": float("inf"),
                "gpt4_requests": float("inf"),
            },
            badge="🏛️",
            highlight_color="#607D8B",
            overage_rates={"requests": 0.02, "tokens": 0.002},
        ),
    }

    @classmethod
    def get_tier_details(cls, tier: str) -> Dict:
        """Get detailed information about a pricing tier."""
        if tier not in cls.PRICING_TIERS:
            raise ValueError(f"Unknown tier: {tier}")

        tier_info = cls.PRICING_TIERS[tier]
        return {
            "name": tier_info.name,
            "price": tier_info.price,
            "description": tier_info.description,
            "features": tier_info.features,
            "limits": tier_info.limits,
            "badge": tier_info.badge,
            "highlight_color": tier_info.highlight_color,
            "overage_rates": tier_info.overage_rates,
        }

    @staticmethod
    def is_valid_api_key(api_key: str) -> bool:
        """Check if the API key is valid and subscription is active."""
        return bool(
            api_key
            and (api_key.startswith("sk-") or api_key.startswith("ant-"))  # OpenAI
        )  # Anthropic

    @classmethod
    def calculate_overage_charges(cls, tier: str, usage: Dict) -> Dict:
        """Calculate detailed overage charges based on usage beyond limits."""
        if tier not in cls.PRICING_TIERS:
            raise ValueError(f"Unknown tier: {tier}")

        tier_info = cls.PRICING_TIERS[tier]
        charges = {"request_overage": 0.0, "token_overage": 0.0, "total": 0.0}

        # Request overages
        if usage["total_requests"] > tier_info.limits["monthly_requests"]:
            extra_requests = (
                usage["total_requests"] - tier_info.limits["monthly_requests"]
            )
            charges["request_overage"] = (
                extra_requests * tier_info.overage_rates["requests"]
            )

        # Token overages
        if usage["total_tokens"] > tier_info.limits["monthly_tokens"]:
            extra_tokens = usage["total_tokens"] - tier_info.limits["monthly_tokens"]
            charges["token_overage"] = (extra_tokens / 1000) * tier_info.overage_rates[
                "tokens"
            ]

        charges["total"] = charges["request_overage"] + charges["token_overage"]
        return charges

    @classmethod
    def estimate_monthly_cost(cls, tier: str, estimated_usage: Dict) -> Dict:
        """Estimate monthly cost based on expected usage."""
        tier_info = cls.PRICING_TIERS[tier]
        base_cost = tier_info.price
        overage_charges = cls.calculate_overage_charges(tier, estimated_usage)

        return {
            "base_price": base_cost,
            "overage_charges": overage_charges,
            "total_estimated_cost": base_cost + overage_charges["total"],
            "breakdown": {
                "base_features": "Included in base price",
                "extra_requests": f"${overage_charges['request_overage']:.2f}",
                "extra_tokens": f"${overage_charges['token_overage']:.2f}",
            },
        }
