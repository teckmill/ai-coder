"""Streamlit UI for AI Coder - ChatGPT-like interface."""

import os
import sys
import uuid

import streamlit as st

from src.services.analytics import UsageAnalytics
from src.services.code_analyzer import CodeAnalyzer
from src.services.code_generator import CodeGenerator
from src.services.code_refactor import CodeRefactor
from src.services.pricing import PricingManager
from src.services.usage_tracker import UsageTracker

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


# Custom CSS for ChatGPT-like interface
def local_css():
    """Custom CSS for ChatGPT-like interface."""
    st.markdown(
        """
    <style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    .stButton>button {
        color: white;
        background-color: #4CAF50;
        border-radius: 10px;
    }
    .stTextArea>div>div>textarea {
        background-color: #f9f9f9;
        border: 1px solid #e0e0e0;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )


def initialize_session_state():
    """Initialize session state variables."""
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "usage_tracker" not in st.session_state:
        st.session_state.usage_tracker = UsageTracker(st.session_state.user_id)

    if "code_generator" not in st.session_state:
        st.session_state.code_generator = CodeGenerator(user_id=st.session_state.user_id)

    if "code_analyzer" not in st.session_state:
        st.session_state.code_analyzer = CodeAnalyzer()

    if "code_refactor" not in st.session_state:
        st.session_state.code_refactor = CodeRefactor()

    if "analytics" not in st.session_state:
        st.session_state.analytics = UsageAnalytics(st.session_state.user_id)


def display_message(message):
    """Display a chat message in the UI."""
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


def display_code_suggestions(code_suggestions):
    """Display code suggestions in the UI."""
    if code_suggestions:
        st.subheader("Code Suggestions")
        for idx, suggestion in enumerate(code_suggestions, 1):
            with st.expander(f"Suggestion {idx}"):
                st.code(suggestion, language="python")


def display_code_analysis(analysis_results):
    """Display code analysis results in the UI."""
    if analysis_results:
        st.subheader("Code Analysis")
        for idx, result in enumerate(analysis_results, 1):
            with st.expander(f"Analysis {idx}"):
                st.markdown(result)


def display_code_refactoring(refactoring_results):
    """Display code refactoring results in the UI."""
    if refactoring_results:
        st.subheader("Code Refactoring")
        for idx, refactored_code in enumerate(refactoring_results, 1):
            with st.expander(f"Refactored Code {idx}"):
                st.code(refactored_code, language="python")


def display_error_analysis(error_results):
    """Display code error analysis results in the UI."""
    if error_results:
        st.subheader("Error Analysis")
        for idx, error_details in enumerate(error_results, 1):
            with st.expander(f"Error {idx}"):
                st.markdown(f"**Error Type:** {error_details['type']}")
                st.markdown(f"**Description:** {error_details['description']}")
                st.code(error_details["code_snippet"], language="python")


def display_sidebar():
    """Create and display the sidebar with project options."""
    st.sidebar.title("AI Coder")
    st.sidebar.markdown("---")

    # Model selection
    st.sidebar.markdown("### Model Selection")
    model_options = {
        "AI Coder v1 (Free)": "ai_coder_v1",
        "GPT-4 Turbo": "gpt_4_turbo",
        "GPT-4": "gpt_4",
        "GPT-3.5 Turbo": "gpt_3_5_turbo",
        "Claude-3": "claude_3",
    }
    selected_model = st.sidebar.selectbox("Choose a model", options=list(model_options.keys()), index=0)
    st.session_state.model = model_options[selected_model]

    # Current Plan
    st.sidebar.markdown("### 💎 Current Plan")
    selected_tier = st.sidebar.selectbox(
        "",
        options=list(PricingManager.PRICING_TIERS.keys()),
        format_func=lambda x: PricingManager.PRICING_TIERS[x].name,
    )
    tier = PricingManager.PRICING_TIERS[selected_tier]
    st.sidebar.markdown(f"<h4>{tier.badge} {tier.name}</h4>", unsafe_allow_html=True)
    st.sidebar.markdown(f"<p>${tier.price}/month</p>", unsafe_allow_html=True)

    # Usage
    st.sidebar.markdown("### 📊 Usage")
    usage = st.session_state.usage_tracker.get_monthly_usage()
    for limit_name, limit_value in tier.limits.items():
        if limit_value == float("inf") or limit_value == 0:
            st.sidebar.write(f"✨ {limit_name.replace('_', ' ').title()}: Unlimited")
        else:
            current_value = usage.get(limit_name, 0)
            progress = min(1.0, current_value / max(1, limit_value))
            st.sidebar.write(limit_name.replace("_", " ").title())
            st.sidebar.progress(progress)
            st.sidebar.write(f"{current_value:,} / {limit_value:,}")

    # Features
    st.sidebar.markdown("### ✨ Features")
    with st.sidebar.expander("Available Features", expanded=False):
        feature_categories = [
            "basic",
            "code_intelligence",
            "security",
            "testing",
            "performance",
            "collaboration",
            "project",
            "devops",
            "ai_workflow",
        ]
        for category in feature_categories:
            category_features = PricingManager.FEATURES.get(category, [])
            available_features = [f for f in category_features if f["name"] in [feat["name"] for feat in tier.features]]
            if available_features:
                st.sidebar.markdown(f"**{category.replace('_', ' ').title()}**")
                for feature in available_features:
                    st.sidebar.markdown(
                        f"""
                    <div class="feature-card">
                        <span class="feature-icon">
                            {feature['icon']}
                        </span>
                        <strong>{feature['name']}</strong>
                        <p>
                            <small>
                                {feature['description']}
                            </small>
                        </p>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )


def main():
    """Main Streamlit application entry point."""
    st.set_page_config(page_title="AI Coder", page_icon="🤖", layout="wide")

    local_css()
    initialize_session_state()
    display_sidebar()

    # Page title and description
    st.title("AI Coder: Your Intelligent Code Companion")
    st.write("Generate, analyze, and refactor code " "with advanced AI-powered assistance.")

    # Main chat area
    st.markdown('<div style="margin-bottom: 100px">', unsafe_allow_html=True)

    # Display welcome message if no messages
    if not st.session_state.messages:
        st.markdown(
            """
        <div class="welcome-message">
            <h1>👋 Welcome to AI Coder!</h1>
            <p>I'm your AI coding assistant. I can help you with:</p>
            <ul>
                <li>🚀 Generating code in any language</li>
                <li>🔍 Code analysis and optimization</li>
                <li>🛠️ Refactoring and improvements</li>
                <li>📝 Documentation generation</li>
                <li>🐛 Debugging assistance</li>
                <li>🔒 Security scanning</li>
            </ul>
            <p>How can I help you today?</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Display chat messages
    for message in st.session_state.messages:
        display_message(message)

    # Input area
    st.markdown('<div class="input-area">', unsafe_allow_html=True)

    # Create two columns for input and buttons
    col1, col2 = st.columns([4, 1])

    with col1:
        user_input = st.text_area(
            "",
            placeholder="Ask me anything about coding...",
            key="user_input",
            height=100,
        )

    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            clear = st.button("Clear")
        with col2_2:
            submit = st.button("Submit")

    if submit and user_input:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": user_input})

        # Generate response
        try:
            # Track usage
            st.session_state.usage_tracker.add_usage(
                model=st.session_state.model,
                input_tokens=len(user_input.split()),
                output_tokens=0,  # Will be updated after generation
                request_type="chat",
            )

            # Process the request
            if "generate" in user_input.lower() or "create" in user_input.lower():
                response = st.session_state.code_generator.generate_code(user_input)
            elif "analyze" in user_input.lower() or "review" in user_input.lower():
                response = st.session_state.code_analyzer.analyze_code(user_input)
            elif "refactor" in user_input.lower() or "improve" in user_input.lower():
                response = st.session_state.code_refactor.refactor_code(user_input)
            else:
                response = st.session_state.code_generator.chat(user_input)

            # Add assistant message
            st.session_state.messages.append({"role": "assistant", "content": response})

            # Track analytics
            st.session_state.analytics.track_event(
                "chat",
                {
                    "input_length": len(user_input),
                    "output_length": len(response),
                    "success": True,
                },
            )

            # Clear input
            st.session_state.user_input = ""

        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.session_state.analytics.track_event(
                "chat",
                {"input_length": len(user_input), "error": str(e), "success": False},
            )

    if clear:
        st.session_state.messages = []

    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
