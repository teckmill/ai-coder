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
            features = [f for f in tier.features if f in PricingManager.FEATURES.get(category, [])]
            if features:
                st.markdown(f"**{category.replace('_', ' ').title()}**")
                for feature in features:
                    st.write(f"{feature['icon']} {feature['name']}")
                    with st.expander("Learn more"):
                        st.write(feature['description'])
        
        # Display limits with progress bars
        st.subheader("Usage Limits")
        usage = st.session_state.usage_tracker.get_current_usage()
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
                            
                            # Track usage
                            st.session_state.usage_tracker.track_request(
                                request_type="code_generation",
                                tokens_used=len(code_input.split()) + len(code.split()),
                                model_used="gpt-4"
                            )
                        except Exception as e:
                            st.error(f"Error generating code: {str(e)}")
                else:
                    st.warning("Please enter a description of what you want to build")
    
    with tab2:
        st.header("Analytics")
        
        # Get analytics data
        insights = st.session_state.analytics.get_usage_insights(days=30)
        
        # Usage Overview
        st.subheader("Usage Overview")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Requests Used",
                f"{usage.get('total_requests', 0):,}",
                f"{usage.get('total_requests', 0) - usage.get('previous_requests', 0):+,}"
            )
        with col2:
            st.metric(
                "Tokens Used",
                f"{usage.get('total_tokens', 0):,}",
                f"{usage.get('total_tokens', 0) - usage.get('previous_tokens', 0):+,}"
            )
        with col3:
            st.metric(
                "Cost Estimate",
                f"${insights['cost_analysis']['total_cost']:.2f}",
                f"${insights['cost_analysis']['avg_daily_cost']:.2f}/day"
            )
        
        # Detailed Analytics
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Usage Patterns")
            st.write("Peak Hours:", insights["usage_patterns"]["peak_hours"])
            st.write("Busy Days:", insights["usage_patterns"]["busy_days"])
            st.write(f"Avg Session Length: {insights['usage_patterns']['avg_session_length']:.1f} min")
        
        with col2:
            st.subheader("Performance Metrics")
            st.write(f"Success Rate: {insights['productivity_metrics']['success_rate']:.1f}%")
            st.write(f"Avg Generation Time: {insights['productivity_metrics']['avg_generation_time']:.1f}s")
            st.write(f"Code Quality Score: {insights['productivity_metrics']['avg_code_quality']:.1f}/10")
        
        # Recommendations
        st.subheader("Recommendations")
        for rec in st.session_state.analytics.get_recommendations():
            with st.expander(f"{rec['priority'].upper()}: {rec['message']}"):
                st.write(f"Suggested Action: {rec['action']}")
    
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
