"""Streamlit UI for AI Coder."""
import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import streamlit as st
from src.services.pricing import PricingManager
from src.services.usage_tracker import UsageTracker
from src.services.code_generator import CodeGenerator
from src.services.analytics import UsageAnalytics

def main():
    st.set_page_config(
        page_title="AI Coder",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.title("AI Coder 🚀")
    
    # Initialize session state
    if 'user_id' not in st.session_state:
        st.session_state.user_id = 'demo_user'  # In production, this would be the actual user ID
    
    if 'analytics' not in st.session_state:
        st.session_state.analytics = UsageAnalytics(st.session_state.user_id)
    
    if 'usage_tracker' not in st.session_state:
        st.session_state.usage_tracker = UsageTracker(st.session_state.user_id)
    
    # Sidebar for pricing and features
    with st.sidebar:
        st.header("Pricing Plans")
        selected_tier = st.selectbox(
            "Select your plan",
            options=list(PricingManager.PRICING_TIERS.keys()),
            format_func=lambda x: PricingManager.PRICING_TIERS[x].name
        )
        
        # Display tier details
        tier = PricingManager.PRICING_TIERS[selected_tier]
        st.subheader(f"{tier.badge} {tier.name} - ${tier.price}/month")
        st.write(tier.description)
        
        # Display features in a more organized way
        st.subheader("Features")
        for category in ['basic', 'code_intelligence', 'security', 'testing', 'performance', 'collaboration', 'project', 'devops', 'ai_workflow']:
            category_features = PricingManager.FEATURES.get(category, [])
            available_features = [f for f in category_features if f['name'] in [feat['name'] for feat in tier.features]]
            if available_features:
                st.markdown(f"**{category.replace('_', ' ').title()}**")
                for feature in available_features:
                    st.write(f"{feature['icon']} {feature['name']}")
                    with st.expander("Learn more"):
                        st.write(feature['description'])
        
        # Display limits with progress bars
        st.subheader("Usage Limits")
        usage = st.session_state.usage_tracker.get_monthly_usage()
        for limit_name, limit_value in tier.limits.items():
            if limit_value == float("inf"):
                st.write(f"✨ {limit_name.replace('_', ' ').title()}: Unlimited")
            else:
                current_value = usage.get(limit_name, 0)
                progress = min(1.0, current_value / limit_value)
                st.write(f"{limit_name.replace('_', ' ').title()}")
                st.progress(progress)
                st.write(f"{current_value:,} / {limit_value:,}")

    # Main content area
    tab1, tab2, tab3 = st.tabs(["Code Generation", "Analytics", "Settings"])
    
    with tab1:
        st.header("Code Generation")
        code_input = st.text_area("Describe what you want to build", height=150)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            language = st.selectbox(
                "Programming Language",
                ["Python", "JavaScript", "TypeScript", "Java", "Go", "PHP", "Ruby", "C#"]
            )
        with col2:
            if st.button("Generate Code", use_container_width=True):
                if code_input:
                    with st.spinner("Generating code..."):
                        try:
                            generator = CodeGenerator()
                            code = generator.generate_code(code_input, language.lower())
                            st.code(code, language=language.lower())
                            
                            # Track usage and analytics
                            st.session_state.usage_tracker.add_usage(
                                model="gpt-4",
                                input_tokens=len(code_input.split()),
                                output_tokens=len(code.split()),
                                request_type="code_generation"
                            )
                            st.session_state.analytics.track_event(
                                "code_generation",
                                {
                                    "language": language.lower(),
                                    "input_length": len(code_input),
                                    "output_length": len(code),
                                    "success": True
                                }
                            )
                        except Exception as e:
                            st.error(f"Error generating code: {str(e)}")
                            st.session_state.analytics.track_event(
                                "code_generation",
                                {
                                    "language": language.lower(),
                                    "error": str(e),
                                    "success": False
                                }
                            )
                else:
                    st.warning("Please enter a description of what you want to build")
    
    with tab2:
        st.header("Analytics")
        
        # Get analytics data
        insights = st.session_state.analytics.get_usage_insights(days=30)
        
        # Usage Overview
        st.subheader("Usage Overview")
        col1, col2, col3 = st.columns(3)
        
        monthly_usage = st.session_state.usage_tracker.get_monthly_usage()
        with col1:
            st.metric(
                "Total Requests",
                f"{monthly_usage.get('total_requests', 0):,}",
                delta=None
            )
        with col2:
            st.metric(
                "Total Tokens",
                f"{monthly_usage.get('total_tokens', 0):,}",
                delta=None
            )
        with col3:
            st.metric(
                "Success Rate",
                f"{insights.get('productivity_metrics', {}).get('success_rate', 0):.1f}%",
                delta=None
            )
        
        # Language Preferences
        if 'language_preferences' in insights:
            st.subheader("Language Preferences")
            lang_prefs = insights['language_preferences']
            for lang, stats in lang_prefs.get('success_rates', {}).items():
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**{lang.title()}**")
                with col2:
                    st.progress(stats['rate'] / 100)
                    st.write(f"Success Rate: {stats['rate']:.1f}% ({stats['total']} requests)")
        
        # Performance Metrics
        if 'productivity_metrics' in insights:
            st.subheader("Performance")
            metrics = insights['productivity_metrics']
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Avg Response Time", f"{metrics.get('avg_generation_time', 0):.1f}s")
            with col2:
                st.metric("Code Quality Score", f"{metrics.get('avg_code_quality', 0):.1f}/10")
        
        # Recommendations
        st.subheader("Recommendations")
        for rec in st.session_state.analytics.get_recommendations():
            with st.expander(f"{rec['priority'].upper()}: {rec['title']}"):
                st.write(rec['message'])
                st.info(f"Suggested Action: {rec['action']}")
    
    with tab3:
        st.header("Settings")
        api_key = st.text_input("API Key", type="password", help="Enter your OpenAI or Anthropic API key")
        if st.button("Save Settings"):
            if api_key:
                # In production, we would securely store the API key
                st.session_state.api_key = api_key
                st.success("Settings saved successfully!")
            else:
                st.error("Please enter your API key")

if __name__ == "__main__":
    main()
