import streamlit as st
import logging
from typing import Optional
import os
from src.services.code_generator import CodeGenerator
from src.services.code_analyzer import CodeAnalyzer
from src.services.template_manager import TemplateManager
from src.services.project_generator import ProjectGenerator
from src.services.api_doc_generator import APIDocGenerator
from src.services.performance_profiler import PerformanceProfiler
from src.services.db_schema_generator import DBSchemaGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
CLOUD_MODELS = [
    "gpt-4-turbo-preview",
    "gpt-4",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo",
]

MODEL_FEATURES = {
    "gpt-4-turbo-preview": {
        "name": "GPT-4 Turbo",
        "description": "Latest & fastest GPT-4 model",
        "features": [
            "128k context window",
            "Most up-to-date knowledge",
            "Fastest response time",
            "Best for complex projects"
        ],
        "icon": "🚀"
    },
    "gpt-4": {
        "name": "GPT-4",
        "description": "Most capable GPT-4 model",
        "features": [
            "32k context window",
            "Highest accuracy",
            "Best for critical code",
            "Advanced reasoning"
        ],
        "icon": "🧠"
    },
    "gpt-3.5-turbo-16k": {
        "name": "GPT-3.5 Turbo 16K",
        "description": "Extended context GPT-3.5",
        "features": [
            "16k context window",
            "Balanced performance",
            "Good for larger files",
            "Cost-effective"
        ],
        "icon": "💪"
    },
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "description": "Fast and efficient",
        "features": [
            "4k context window",
            "Fastest model",
            "Most cost-effective",
            "Great for quick tasks"
        ],
        "icon": "⚡"
    }
}

def load_css():
    """Load custom CSS."""
    with open(os.path.join(os.path.dirname(__file__), 'styles', 'main.css')) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def setup_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="AI Coder Pro",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    load_css()

def render_header():
    """Render the app header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown('<h1>🤖 AI Coder <span style="font-size: 0.5em; vertical-align: middle; background: linear-gradient(45deg, #FFD700, #FFA500); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">PRO</span></h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Transform your ideas into production-ready code with AI</p>', unsafe_allow_html=True)
    with col2:
        if 'api_key' in st.session_state and st.session_state.api_key:
            st.markdown('<div class="status-premium">✨ Premium Active</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-warning">🔑 API Key Required</div>', unsafe_allow_html=True)

def render_api_key_section():
    """Render the API key input section."""
    with st.sidebar:
        st.markdown("### 🔐 Authentication")
        with st.expander("Configure API Key", expanded='api_key' not in st.session_state):
            st.markdown("""
            <div class='premium-card'>
                <div class="feature-icon">✨</div>
                <h3>Premium Access</h3>
                <p>Enter your OpenAI API key to unlock:</p>
                <ul>
                    <li>🔥 Latest GPT-4 Models</li>
                    <li>💡 Advanced Code Generation</li>
                    <li>⚡ Priority Processing</li>
                    <li>📚 Extended Context Support</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                value=st.session_state.get('api_key', ''),
                help="Your OpenAI API key is required for premium features"
            )
            
            if api_key:
                st.session_state.api_key = api_key
                st.success("✅ API Key configured successfully!")

def render_model_selection():
    """Render the model selection section."""
    with st.sidebar:
        st.markdown("### 🎯 Model Selection")
        
        for model_id in CLOUD_MODELS:
            model = MODEL_FEATURES[model_id]
            st.markdown(f"""
            <div class='model-card' onclick="this.classList.toggle('selected')">
                <div style="display: flex; align-items: center; gap: 0.5rem;">
                    <span style="font-size: 1.5rem;">{model['icon']}</span>
                    <h4>{model['name']}</h4>
                </div>
                <p>{model['description']}</p>
                <div style="margin-top: 0.75rem; font-size: 0.8rem;">
                    {''.join(f'<div style="margin: 0.25rem 0;">• {feature}</div>' for feature in model['features'])}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        selected_model = st.selectbox(
            "Select Model",
            options=CLOUD_MODELS,
            format_func=lambda x: MODEL_FEATURES[x]['name'],
            index=0
        )
        st.session_state.selected_model = selected_model

def render_main_content():
    """Render the main content area."""
    if 'api_key' not in st.session_state or not st.session_state.api_key:
        st.markdown("""
        <div class='premium-card animate-fade-in'>
            <div style="text-align: center;">
                <div class="feature-icon">👋</div>
                <h2>Welcome to AI Coder Pro!</h2>
                <p>Get started by adding your API key in the sidebar.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    tabs = st.tabs([
        "🎯 Code Generation",
        "🔍 Code Analysis",
        "📝 Documentation",
        "⚡ Performance",
        "🗃️ Database Schema"
    ])

    with tabs[0]:
        st.markdown("### Generate Code")
        col1, col2 = st.columns([2, 1])
        
        with col1:
            prompt = st.text_area(
                "Describe what you want to build",
                height=150,
                placeholder="Example: Create a Python function that sorts a list using quicksort algorithm"
            )
            
            col_lang, col_btn = st.columns([2, 1])
            with col_lang:
                language = st.selectbox(
                    "Programming Language",
                    ["Python", "JavaScript", "TypeScript", "Java", "Go"]
                )
            with col_btn:
                generate_btn = st.button("Generate Code", use_container_width=True)
        
        with col2:
            st.markdown("""
            <div class='premium-card'>
                <h4>💡 Tips for better results:</h4>
                <ul>
                    <li>Be specific about the functionality</li>
                    <li>Mention edge cases to handle</li>
                    <li>Specify any dependencies</li>
                    <li>Include performance requirements</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        if generate_btn and prompt:
            with st.spinner("🔮 Generating your code..."):
                try:
                    result = st.session_state.code_generator.generate_code(prompt, language.lower())
                    
                    st.markdown("### 📝 Generated Code")
                    st.code(result["code"], language=language.lower())
                    
                    st.markdown("""
                    <div class='premium-card'>
                        <h4>🚀 What's next?</h4>
                        <ul>
                            <li>Review the generated code</li>
                            <li>Test edge cases</li>
                            <li>Optimize if needed</li>
                            <li>Generate documentation</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error generating code: {str(e)}")

def initialize_services():
    """Initialize the application services."""
    try:
        if not st.session_state.api_key:
            raise ValueError("Please configure your OpenAI API key to access premium features.")
        
        st.session_state.code_generator = CodeGenerator(
            model_name=st.session_state.selected_model,
            api_key=st.session_state.api_key
        )
        
        st.session_state.code_analyzer = CodeAnalyzer()
        st.session_state.template_manager = TemplateManager()
        st.session_state.project_generator = ProjectGenerator()
        st.session_state.api_doc_generator = APIDocGenerator()
        st.session_state.performance_profiler = PerformanceProfiler()
        st.session_state.db_schema_generator = DBSchemaGenerator()
        
        st.session_state.services_initialized = True
        logger.debug("Services initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing services: {str(e)}")
        st.error(f"Error initializing services: {str(e)}")
        st.session_state.services_initialized = False

def main():
    """Main application entry point."""
    setup_page()
    render_header()
    render_api_key_section()
    
    if 'api_key' in st.session_state and st.session_state.api_key:
        render_model_selection()
        if not st.session_state.get('services_initialized', False):
            initialize_services()
    
    render_main_content()

if __name__ == "__main__":
    main()
