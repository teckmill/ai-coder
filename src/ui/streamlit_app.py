"""Streamlit UI for AI Coder - ChatGPT-like interface."""

import os
import sys
import uuid
from datetime import datetime

import streamlit as st

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.services.analytics import UsageAnalytics
from src.services.code_analyzer import CodeAnalyzer
from src.services.code_generator import CodeGenerator
from src.services.code_refactor import CodeRefactor
from src.services.pricing import PricingManager
from src.services.usage_tracker import UsageTracker


# Custom CSS for ChatGPT-like interface
def local_css():
    st.markdown(
        """
    <style>
        /* Chat container */
        .chat-container {
            padding: 1rem;
            margin-bottom: 1rem;
            border-radius: 0.5rem;
        }
        
        /* User message */
        .user-message {
            background-color: #343541;
            color: #ECECF1;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        }
        
        /* Assistant message */
        .assistant-message {
            background-color: #444654;
            color: #ECECF1;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
            border-left: 4px solid #19c37d;
        }
        
        /* Welcome message */
        .welcome-message {
            background-color: #444654;
            color: #ECECF1;
            padding: 2rem;
            margin: 2rem auto;
            border-radius: 1rem;
            max-width: 800px;
            text-align: center;
        }
        
        .welcome-message h1 {
            color: #19c37d;
            margin-bottom: 1.5rem;
        }
        
        .welcome-message ul {
            list-style: none;
            padding: 0;
            margin: 1.5rem 0;
        }
        
        .welcome-message li {
            margin: 0.75rem 0;
            font-size: 1.1rem;
        }
        
        .welcome-message p {
            color: #ECECF1;
            font-size: 1.1rem;
        }
        
        /* Code blocks */
        .code-block {
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 1rem;
            border-radius: 0.5rem;
            font-family: 'Consolas', monospace;
        }
        
        /* Sidebar */
        .sidebar-content {
            padding: 1rem;
        }
        
        /* Features */
        .feature-card {
            background-color: #343541;
            color: #ECECF1;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0.5rem;
            border: 1px solid #4d4d4d;
        }
        
        .feature-icon {
            font-size: 1.5rem;
            margin-right: 0.5rem;
        }
        
        /* Input area */
        .input-area {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            padding: 1rem;
            background-color: #343541;
            border-top: 1px solid #4d4d4d;
        }
        
        /* Model selector */
        .model-selector {
            margin-bottom: 1rem;
            padding: 0.5rem;
            border-radius: 0.5rem;
            border: 1px solid #4d4d4d;
            background-color: #343541;
            color: #ECECF1;
        }
        
        /* Progress bars */
        .stProgress > div > div > div {
            background-color: #19c37d;
        }

        /* Override Streamlit's theme */
        .stApp {
            background-color: #343541;
            color: #ECECF1;
        }

        .stTextArea > div > div > textarea {
            background-color: #444654;
            color: #ECECF1;
            border: 1px solid #4d4d4d;
        }

        .stTextArea > div > div > textarea:focus {
            box-shadow: 0 0 0 2px #19c37d;
        }

        .stButton > button {
            background-color: #19c37d;
            color: white;
            border: none;
        }

        .stButton > button:hover {
            background-color: #15a76c;
        }

        .sidebar .stButton > button {
            background-color: #444654;
            border: 1px solid #4d4d4d;
        }

        .sidebar .stButton > button:hover {
            background-color: #515262;
        }
    </style>
    """,
        unsafe_allow_html=True,
    )


def initialize_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())

    if "analytics" not in st.session_state:
        st.session_state.analytics = UsageAnalytics(st.session_state.user_id)

    if "usage_tracker" not in st.session_state:
        st.session_state.usage_tracker = UsageTracker(st.session_state.user_id)

    if "code_generator" not in st.session_state:
        st.session_state.code_generator = CodeGenerator()

    if "code_analyzer" not in st.session_state:
        st.session_state.code_analyzer = CodeAnalyzer()

    if "code_refactor" not in st.session_state:
        st.session_state.code_refactor = CodeRefactor()


def display_message(message):
    """Display a chat message."""
    role = message["role"]
    content = message["content"]

    if role == "user":
        st.markdown(
            f"""
        <div class="user-message">
            <strong>You:</strong><br/>
            {content}
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
        <div class="assistant-message">
            <strong>AI Coder:</strong><br/>
            {content}
        </div>
        """,
            unsafe_allow_html=True,
        )


def main():
    st.set_page_config(
        page_title="AI Coder",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    local_css()
    initialize_session_state()

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)

        # Model selection
        st.markdown("### Model Selection")
        model_options = {
            "AI Coder v1 (Free)": "ai_coder_v1",
            "GPT-4 Turbo": "gpt_4_turbo",
            "GPT-4": "gpt_4",
            "GPT-3.5 Turbo": "gpt_3_5_turbo",
            "Claude-3": "claude_3",
        }
        selected_model = st.selectbox(
            "Choose a model",
            options=list(model_options.keys()),
            index=0,  # Set AI Coder as default
        )
        st.session_state.model = model_options[selected_model]

        # Current Plan
        st.markdown("### 💎 Current Plan")
        selected_tier = st.selectbox(
            "",
            options=list(PricingManager.PRICING_TIERS.keys()),
            format_func=lambda x: PricingManager.PRICING_TIERS[x].name,
        )
        tier = PricingManager.PRICING_TIERS[selected_tier]
        st.markdown(f"<h4>{tier.badge} {tier.name}</h4>", unsafe_allow_html=True)
        st.markdown(f"<p>${tier.price}/month</p>", unsafe_allow_html=True)

        # Usage
        st.markdown("### 📊 Usage")
        usage = st.session_state.usage_tracker.get_monthly_usage()
        for limit_name, limit_value in tier.limits.items():
            if limit_value == float("inf") or limit_value == 0:
                st.write(f"✨ {limit_name.replace('_', ' ').title()}: Unlimited")
            else:
                current_value = usage.get(limit_name, 0)
                progress = min(1.0, current_value / max(1, limit_value))
                st.write(f"{limit_name.replace('_', ' ').title()}")
                st.progress(progress)
                st.write(f"{current_value:,} / {limit_value:,}")

        # Features
        st.markdown("### ✨ Features")
        with st.expander("Available Features", expanded=False):
            for category in [
                "basic",
                "code_intelligence",
                "security",
                "testing",
                "performance",
                "collaboration",
                "project",
                "devops",
                "ai_workflow",
            ]:
                category_features = PricingManager.FEATURES.get(category, [])
                available_features = [
                    f
                    for f in category_features
                    if f["name"] in [feat["name"] for feat in tier.features]
                ]
                if available_features:
                    st.markdown(f"**{category.replace('_', ' ').title()}**")
                    for feature in available_features:
                        st.markdown(
                            f"""
                        <div class="feature-card">
                            <span class="feature-icon">{feature['icon']}</span>
                            <strong>{feature['name']}</strong>
                            <p><small>{feature['description']}</small></p>
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )

        st.markdown("</div>", unsafe_allow_html=True)

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
