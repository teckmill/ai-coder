import streamlit as st
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import sys
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.services.base_service import BaseService
from src.services.code_generator import CodeGenerator
from src.services.code_analyzer import CodeAnalyzer
from src.services.template_manager import TemplateManager
from src.services.project_generator import ProjectGenerator
from src.services.api_doc_generator import APIDocGenerator
from src.services.performance_profiler import PerformanceProfiler
from src.services.db_schema_generator import DBSchemaGenerator

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define available models
FREE_MODELS = ["codellama", "llama2", "mistral"]
PREMIUM_MODELS = ["gpt-4", "gpt-3.5-turbo", "claude-2"]

# Initialize session state for storing API key and model selection
if 'api_key' not in st.session_state:
    st.session_state.api_key = None
if 'selected_model' not in st.session_state:
    st.session_state.selected_model = "codellama"
if 'services_initialized' not in st.session_state:
    st.session_state.services_initialized = False

# Configure page
st.set_page_config(
    page_title="AI Auto-Coder",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize services
def initialize_services():
    try:
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
    except Exception as e:
        st.error(f"Error initializing services: {str(e)}")
        st.session_state.services_initialized = False

# Custom CSS
st.markdown("""
<style>
    /* Main container */
    .main {
        padding: 2rem;
        background-color: #222831;
    }
    
    /* Headers */
    h1 {
        color: #00ADB5 !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 1.5rem !important;
        text-shadow: 0 0 10px rgba(0, 173, 181, 0.3);
    }
    
    h2 {
        color: #EEEEEE !important;
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
    }
    
    h3 {
        color: #00ADB5 !important;
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        margin-top: 1.5rem !important;
        border-left: 4px solid #00ADB5;
        padding-left: 1rem;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: #2B2B2B !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin: 1.5rem 0 !important;
        border: 1px solid #393E46;
    }
    
    /* Text areas */
    .stTextArea textarea {
        background-color: #2B2B2B !important;
        color: #EEEEEE !important;
        border-radius: 12px !important;
        border: 1px solid #393E46 !important;
        padding: 1rem !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.95rem !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #00ADB5 !important;
        box-shadow: 0 0 0 2px rgba(0, 173, 181, 0.2) !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #00ADB5 !important;
        color: #EEEEEE !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.75rem 2.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
    }
    
    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 16px rgba(0, 173, 181, 0.2) !important;
        background-color: #00BEC7 !important;
    }
    
    .stButton button:active {
        transform: translateY(0) !important;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #393E46 !important;
        color: #EEEEEE !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem !important;
        margin: 1rem 0 !important;
        border-left: 4px solid #00ADB5 !important;
    }
    
    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background-color: #393E46 !important;
        padding: 2rem 1.5rem !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background-color: #393E46 !important;
        padding: 1rem !important;
        border-radius: 12px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        color: #EEEEEE !important;
        border-radius: 8px !important;
        padding: 1rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #00ADB5 !important;
        color: #EEEEEE !important;
    }
    
    /* Spinners */
    .stSpinner {
        text-align: center;
        padding: 2rem;
    }
    
    /* Select boxes */
    .stSelectbox select {
        background-color: #2B2B2B !important;
        color: #EEEEEE !important;
        border: 1px solid #393E46 !important;
        border-radius: 8px !important;
    }
    
    /* Links */
    a {
        color: #00ADB5 !important;
        text-decoration: none !important;
        transition: all 0.3s ease !important;
    }
    
    a:hover {
        color: #00BEC7 !important;
        text-decoration: underline !important;
    }
    
    /* Custom info box */
    .custom-info-box {
        background-color: #393E46;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border: 1px solid #00ADB5;
    }
    
    .custom-info-box h4 {
        color: #00ADB5;
        margin: 0;
        font-size: 1.2rem;
    }
    
    .custom-info-box p {
        color: #EEEEEE;
        margin: 0.5rem 0 0 0;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    
    /* High contrast theme */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        font-size: 1.1em !important;
    }
    
    /* Focus indicators */
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus,
    .stButton > button:focus {
        outline: 3px solid #0096FF !important;
        box-shadow: 0 0 0 3px rgba(0, 150, 255, 0.3) !important;
    }
    
    /* Larger click targets */
    .stButton > button {
        min-height: 3em !important;
        font-size: 1.1em !important;
    }
    
    /* Better contrast for tabs */
    .stTabs [role="tab"] {
        background-color: #2D2D2D !important;
        color: #FFFFFF !important;
        font-size: 1.1em !important;
        padding: 1em 2em !important;
    }
    
    .stTabs [role="tab"][aria-selected="true"] {
        background-color: #0096FF !important;
        border-radius: 4px !important;
    }
    
    /* Improved form labels */
    label {
        font-size: 1.2em !important;
        font-weight: 500 !important;
        color: #FFFFFF !important;
        margin-bottom: 0.5em !important;
    }
    
    /* Keyboard focus styles */
    *:focus {
        outline: 3px solid #0096FF !important;
        outline-offset: 2px !important;
    }
    
    /* Accessibility helper classes */
    .sr-only {
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        border: 0;
    }
    
    /* Better contrast for code blocks */
    pre {
        background-color: #1E1E1E !important;
        border: 1px solid #444444 !important;
        border-radius: 4px !important;
    }
    
    /* Improved error messages */
    .stAlert {
        font-size: 1.1em !important;
        padding: 1em !important;
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.title("🤖 AI Auto-Coder")
    st.subheader("Your AI-powered coding assistant")
    
    # Sidebar for model selection and API key
    with st.sidebar:
        st.header("Model Settings")
        
        # Model selection
        model_type = st.radio("Select Model Type", ["Free", "Premium"])
        
        if model_type == "Free":
            model_list = FREE_MODELS
        else:
            model_list = PREMIUM_MODELS
            st.info("Premium models require an API key")
            api_key = st.text_input("Enter API Key", type="password")
            if api_key:
                st.session_state.api_key = api_key
            else:
                st.session_state.api_key = None
        
        selected_model = st.selectbox("Select Model", model_list)
        
        if selected_model != st.session_state.selected_model:
            st.session_state.selected_model = selected_model
            st.session_state.services_initialized = False
        
        if not st.session_state.services_initialized:
            initialize_services()
    
    if not st.session_state.services_initialized:
        st.error("Services not initialized. Please check your model settings and API key if using a premium model.")
        return
    
    # Constants
    API_URL = "http://localhost:8000/api"
    SUPPORTED_LANGUAGES = ["python", "javascript", "java", "cpp", "typescript", "html", "css"]
    REQUEST_TIMEOUT = 120

    def send_request(endpoint: str, data: Optional[Dict] = None, method: str = "POST") -> Optional[Dict]:
        """Send a request to the backend service."""
        try:
            if method == "GET":
                if endpoint == "templates":
                    return st.session_state.template_manager.list_templates()
                elif endpoint == "languages":
                    return {"languages": ["python", "javascript", "typescript", "java", "go"]}
            else:
                if endpoint == "generate":
                    return st.session_state.code_generator.generate_code(data["prompt"], data["language"])
                elif endpoint == "analyze":
                    return st.session_state.code_analyzer.analyze_code(data["code"], data["language"])
                elif endpoint == "templates":
                    if "name" in data:
                        return st.session_state.template_manager.create_template(data["name"], data["description"], data["code"])
                    else:
                        return st.session_state.template_manager.generate_template(data["description"])
                elif endpoint == "optimize":
                    return st.session_state.performance_profiler.optimize_performance(data["code"], {})
                elif endpoint == "generate-docs":
                    return st.session_state.api_doc_generator.generate_api_documentation([data["code"]], data["doc_format"])
                elif endpoint == "generate-schema":
                    return st.session_state.db_schema_generator.generate_schema(data["description"], data["db_type"])
        
            return None
        
        except requests.exceptions.ConnectionError:
            st.error("⚠️ Failed to connect to the backend service. Please try again.")
            return None
        except Exception as e:
            st.error(f"⚠️ An error occurred: {str(e)}")
            return None

    # Load models
    model_types = CodeGenerator.get_model_types()
    
    # Header with glowing effect
    st.markdown("""
        <h1 style='text-align: center; margin-bottom: 0.5rem;'>
            🤖 AI Auto-Coder
            <div style='font-size: 1rem; color: #00ADB5; margin-top: 0.5rem;'>
                Powered by Local LLM
            </div>
        </h1>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='custom-info-box' style='text-align: center;'>
        <p style='font-size: 1.1rem; color: #EEEEEE;'>
            Generate, analyze, and refactor code using AI, all processed locally for enhanced security.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load templates
    try:
        templates_result = send_request("templates", method="GET")
        templates = templates_result.get("templates", []) if templates_result else []
        
        # Collect all unique tags
        all_tags = set()
        for template in templates:
            if isinstance(template, dict):
                all_tags.update(template.get("tags", []))
        all_tags = ["All"] + sorted(list(all_tags))
        
    except Exception as e:
        logger.error(f"Error loading templates: {str(e)}")
        templates = []
        all_tags = ["All"]

    # Load languages
    try:
        languages = send_request("languages", method="GET")
        if languages is None:
            languages = {"languages": SUPPORTED_LANGUAGES}
    except Exception as e:
        logger.error(f"Error loading languages: {str(e)}")
        languages = {"languages": SUPPORTED_LANGUAGES}

    # Main tabs with icons and ARIA labels
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "Code Generation", "Code Analysis", "Templates", 
        "Project Generator", "API Docs", "Performance", "Database"
    ])
    
    # Code Generation Tab
    with tab1:
        st.header("Generate Code")
        prompt = st.text_area(
            "Describe what you want to build",
            height=100,
            placeholder="Example: Create a function that sorts a list of numbers using quicksort",
            help="Describe your coding task in natural language",
            key="generate_input",
            max_chars=1000,
            label_visibility="visible"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            generate_button = st.button("✨ Generate", use_container_width=True)
        
        if generate_button and prompt:
            with st.spinner("🔮 Generating code..."):
                result = send_request("generate", {
                    "prompt": prompt,
                    "language": selected_language
                })
                
                if result:
                    st.markdown("### 📝 Generated Code")
                    st.code(result["code"], language=selected_language)
                    if "explanation" in result:
                        st.markdown("### 💡 Explanation")
                        st.info(result["explanation"])
    
    # Code Analysis Tab
    with tab2:
        st.header("Analyze Code")
        code_to_analyze = st.text_area(
            "Enter code to analyze",
            height=200,
            placeholder="Paste your code here...",
            help="Paste the code you want to analyze"
        )
        
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analyze_button = st.button("🔍 Analyze", use_container_width=True)
        
        if analyze_button and code_to_analyze:
            with st.spinner("🔍 Analyzing code... (This may take a few seconds)"):
                progress_text = st.empty()
                progress_text.markdown('<span class="sr-only">Analysis in progress...</span>', unsafe_allow_html=True)
                result = send_request("analyze", {
                    "code": code_to_analyze,
                    "language": selected_language
                })
                
                if result:
                    if "formatted_code" in result:
                        st.markdown("### 📝 Formatted Code")
                        st.code(result["formatted_code"], language=selected_language)
                    
                    if "linter_output" in result:
                        st.markdown("### 🔍 Analysis Results")
                        for issue in result["linter_output"]:
                            if issue["type"] == "error":
                                st.error(f"Line {issue['line']}: {issue['message']}")
                            else:
                                st.info(f"Line {issue['line']}: {issue['message']}")
                    
                    if "ai_suggestions" in result:
                        st.markdown("### 💡 AI Suggestions")
                        st.success(result["ai_suggestions"])
    
    # Templates Tab
    with tab3:
        st.header("Code Templates")
        
        template_tab1, template_tab2 = st.tabs(["🔍 Browse Templates", "✨ Create Template"])
        
        with template_tab1:
            st.subheader("Browse Templates")
            
            # Template filters
            col1, col2 = st.columns(2)
            with col1:
                filter_language = st.selectbox(
                    "Filter by Language",
                    ["All"] + languages.get("languages", SUPPORTED_LANGUAGES)
                )
            
            with col2:
                filter_tag = st.selectbox(
                    "Filter by Tag",
                    all_tags
                )
            
            # Display templates
            if templates:
                filtered_templates = templates
                
                # Apply language filter
                if filter_language != "All":
                    filtered_templates = [t for t in filtered_templates 
                                       if isinstance(t, dict) and t.get("language") == filter_language]
                
                # Apply tag filter
                if filter_tag != "All":
                    filtered_templates = [t for t in filtered_templates 
                                       if isinstance(t, dict) and filter_tag in t.get("tags", [])]
                
                for template in filtered_templates:
                    if isinstance(template, dict):
                        with st.expander(f"📄 {template.get('name', 'Unnamed Template')}"):
                            st.markdown(f"**Description:** {template.get('description', 'No description')}")
                            st.code(template.get('code', ''), language=template.get('language', 'python'))
                            if template.get('tags'):
                                st.markdown(f"**Tags:** {', '.join(template['tags'])}")
                            
                            if st.button("Use Template", key=f"use_{template.get('name', 'template')}"):
                                st.session_state["code_input"] = template.get("code", "")
                                st.experimental_rerun()
            else:
                st.info("No templates found. Create one in the 'Create Template' tab!")

        with template_tab2:
            st.markdown("### Create New Template")
            
            # Manual creation
            template_name = st.text_input(
                "Template Name",
                help="Enter a unique name for your template",
                key="new_template_name"
            )
            
            template_desc = st.text_area(
                "Template Description",
                help="Describe what this template does and how to use it",
                key="new_template_desc"
            )
            
            template_code = st.text_area(
                "Template Code",
                height=200,
                help="Enter the code for your template",
                key="new_template_code"
            )
            
            template_tags = st.text_input(
                "Template Tags",
                help="Enter comma-separated tags",
                key="new_template_tags"
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("💾 Save Template", use_container_width=True):
                    if all([template_name, template_desc, template_code, template_tags]):
                        try:
                            result = send_request("templates", {
                                "name": template_name,
                                "code": template_code,
                                "language": selected_language,
                                "description": template_desc,
                                "tags": [tag.strip() for tag in template_tags.split(",")]
                            })
                            
                            if result:
                                st.success("Template saved successfully!")
                                # Clear the form
                                for key in ["new_template_name", "new_template_desc", "new_template_code", "new_template_tags"]:
                                    st.session_state[key] = ""
                        except Exception as e:
                            st.error(f"Error saving template: {str(e)}")
                    else:
                        st.error("Please fill in all fields")
            
            st.markdown("### Or Generate Template with AI")
            
            template_prompt = st.text_area(
                "Describe the template you want",
                placeholder="Example: Create a template for a REST API endpoint with error handling and input validation",
                help="Describe what kind of template you want to generate"
            )
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("✨ Generate Template", use_container_width=True):
                    if template_prompt:
                        with st.spinner("🔮 Generating template..."):
                            try:
                                result = send_request("templates", {
                                    "description": template_prompt,
                                    "language": selected_language
                                })
                                
                                if result:
                                    st.success("Template generated and saved!")
                                    # Show the generated template
                                    st.markdown(f"### Generated Template: {result['name']}")
                                    st.markdown(f"**Description:** {result['description']}")
                                    st.markdown("**Tags:** " + ", ".join(f"`{tag}`" for tag in result['tags']))
                                    st.code(result['code'], language=result['language'])
                            except Exception as e:
                                st.error(f"Error generating template: {str(e)}")
                    else:
                        st.error("Please enter a template description")
    
    # Project Generator Tab
    with tab4:
        st.header("Project Generator")
        st.write("Generate new project structures with best practices")
        
        project_type = st.selectbox(
            "Project Type",
            ["python-fastapi", "react-typescript", "django-rest", "node-express"]
        )
        
        project_name = st.text_input("Project Name")
        project_description = st.text_area("Project Description")
        
        features = st.multiselect(
            "Features",
            ["Authentication", "Database", "API", "Testing", "Docker", "CI/CD"],
            default=["Authentication", "Testing"]
        )
        
        if st.button("Generate Project"):
            with st.spinner("Generating project structure..."):
                try:
                    project_generator = ProjectGenerator()
                    result = project_generator.generate_project_structure(
                        project_type, project_name, project_description, features
                    )
                    st.success(f"Project generated at: {result['path']}")
                    st.json(result)
                except Exception as e:
                    st.error(f"Error generating project: {str(e)}")

    # API Documentation Tab
    with tab5:
        st.header("API Documentation")
        st.write("Generate comprehensive API documentation")
        
        source_files = st.file_uploader(
            "Upload API Source Files",
            accept_multiple_files=True,
            type=["py", "json", "yaml", "yml"]
        )
        
        doc_format = st.selectbox(
            "Documentation Format",
            ["markdown", "openapi", "postman"]
        )
        
        if st.button("Generate Documentation"):
            with st.spinner("Generating API documentation..."):
                try:
                    doc_generator = APIDocGenerator()
                    result = doc_generator.generate_api_documentation(
                        [f.name for f in source_files],
                        output_format=doc_format
                    )
                    st.markdown(result["documentation"])
                    st.download_button(
                        "Download Documentation",
                        result["documentation"],
                        file_name=f"api_docs.{doc_format}"
                    )
                except Exception as e:
                    st.error(f"Error generating documentation: {str(e)}")

    # Performance Profiler Tab
    with tab6:
        st.header("Performance Profiler")
        st.write("Analyze and optimize code performance")
        
        code_to_profile = st.text_area("Code to Profile", height=200)
        test_input = st.text_area("Test Input (Optional JSON)", height=100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Profile Code"):
                with st.spinner("Profiling code..."):
                    try:
                        profiler = PerformanceProfiler()
                        test_data = json.loads(test_input) if test_input else None
                        profile_results = profiler.profile_code(code_to_profile, test_data)
                        st.subheader("Profile Results")
                        st.json(profile_results)
                    except Exception as e:
                        st.error(f"Error profiling code: {str(e)}")
        
        with col2:
            if st.button("Optimize Code"):
                with st.spinner("Optimizing code..."):
                    try:
                        profiler = PerformanceProfiler()
                        test_data = json.loads(test_input) if test_input else None
                        profile_results = profiler.profile_code(code_to_profile, test_data)
                        optimization = profiler.optimize_performance(code_to_profile, profile_results)
                        st.subheader("Optimization Results")
                        st.code(optimization["code"], language="python")
                        st.json({k: v for k, v in optimization.items() if k != "code"})
                    except Exception as e:
                        st.error(f"Error optimizing code: {str(e)}")

    # Database Schema Generator Tab
    with tab7:
        st.header("Database Schema Generator")
        st.write("Generate and manage database schemas")
        
        db_type = st.selectbox(
            "Database Type",
            ["postgresql", "mysql", "sqlite", "mongodb"]
        )
        
        schema_description = st.text_area(
            "Schema Description",
            "Describe your database schema here...",
            height=200
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Generate Schema"):
                with st.spinner("Generating schema..."):
                    try:
                        schema_generator = DBSchemaGenerator()
                        schema = schema_generator.generate_schema(schema_description, db_type)
                        st.subheader("Generated Schema")
                        st.json(schema)
                        
                        if db_type != "mongodb":
                            sql = schema_generator.generate_sql(schema, db_type)
                            st.subheader("SQL Script")
                            st.code(sql, language="sql")
                            st.download_button(
                                "Download SQL Script",
                                sql,
                                file_name="schema.sql"
                            )
                    except Exception as e:
                        st.error(f"Error generating schema: {str(e)}")
        
        with col2:
            orm_type = st.selectbox(
                "ORM Type",
                ["sqlalchemy", "django", "mongoose"]
            )
            
            if st.button("Generate ORM Models"):
                with st.spinner("Generating ORM models..."):
                    try:
                        schema_generator = DBSchemaGenerator()
                        schema = schema_generator.generate_schema(schema_description, db_type)
                        models = schema_generator.generate_orm_models(schema, orm_type)
                        st.subheader("ORM Models")
                        st.code(models["models"], language="python")
                        st.download_button(
                            "Download Models",
                            models["models"],
                            file_name=f"models.{'py' if orm_type != 'mongoose' else 'js'}"
                        )
                    except Exception as e:
                        st.error(f"Error generating ORM models: {str(e)}")

    # Footer with accessibility information
    st.markdown("---")
    st.markdown("""
    <footer role="contentinfo" style="text-align: center; padding: 1rem;">
        <p>Made with ❤️ by the AI Auto-Coder team</p>
        <p style="font-size: 0.9em; color: #666;">
            Having trouble? Press <kbd>?</kbd> for help or email support@aicoder.com
        </p>
        <p class="sr-only">End of content. Press Tab to continue to navigation.</p>
    </footer>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
