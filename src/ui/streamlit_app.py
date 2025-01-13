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

MODEL_DESCRIPTIONS = {
    "gpt-4-turbo-preview": "🚀 Latest & fastest GPT-4 model, optimized for complex coding tasks",
    "gpt-4": "🧠 Most capable GPT-4 model for highest quality code generation",
    "gpt-3.5-turbo-16k": "💪 Extended context GPT-3.5 for larger codebases",
    "gpt-3.5-turbo": "⚡ Fast and efficient for standard coding tasks"
}

def setup_page():
    """Configure the Streamlit page settings."""
    st.set_page_config(
        page_title="AI Coder Pro",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for a more professional look
    st.markdown("""
        <style>
        .stApp {
            background: linear-gradient(to bottom right, #1a1a1a, #2d2d2d);
            color: #ffffff;
        }
        .stTextInput, .stSelectbox {
            background-color: #333333;
            color: #ffffff;
            border-radius: 5px;
        }
        .stButton > button {
            background: linear-gradient(to right, #00ff87, #60efff);
            color: #000000;
            font-weight: bold;
            border: none;
            border-radius: 5px;
            padding: 0.5rem 2rem;
        }
        .premium-card {
            background: linear-gradient(45deg, #2d2d2d, #1a1a1a);
            border: 1px solid #333333;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
        }
        .model-card {
            background: rgba(45, 45, 45, 0.7);
            border: 1px solid #404040;
            border-radius: 8px;
            padding: 1rem;
            margin: 0.5rem 0;
            transition: transform 0.2s;
        }
        .model-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }
        </style>
    """, unsafe_allow_html=True)

def render_header():
    """Render the app header."""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🤖 AI Coder Pro")
        st.markdown("*Elevate your coding with advanced AI-powered assistance*")
    with col2:
        if 'api_key' in st.session_state and st.session_state.api_key:
            st.success("✨ Premium Access")
        else:
            st.warning("🔑 API Key Required")

def render_api_key_section():
    """Render the API key input section."""
    with st.expander("🔑 API Key Configuration", expanded='api_key' not in st.session_state):
        st.markdown("""
        <div class='premium-card'>
            <h3>🌟 Premium Access</h3>
            <p>Enter your OpenAI API key to unlock premium features:</p>
            <ul>
                <li>Access to latest GPT-4 models</li>
                <li>Enhanced code generation capabilities</li>
                <li>Priority processing</li>
                <li>Extended context handling</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.get('api_key', ''),
            help="Your OpenAI API key is required to use the premium features"
        )
        
        if api_key:
            st.session_state.api_key = api_key
            st.success("✅ API Key configured successfully!")

def render_model_selection():
    """Render the model selection section."""
    st.markdown("### 🎯 Select AI Model")
    
    for model in CLOUD_MODELS:
        with st.container():
            st.markdown(f"""
            <div class='model-card'>
                <h4>{model}</h4>
                <p>{MODEL_DESCRIPTIONS[model]}</p>
            </div>
            """, unsafe_allow_html=True)
    
    selected_model = st.selectbox(
        "Choose your preferred model",
        options=CLOUD_MODELS,
        index=0,
        help="Select the AI model that best suits your needs"
    )
    st.session_state.selected_model = selected_model

def initialize_services():
    """Initialize the application services."""
    try:
        logger.debug(f"Initializing services with model={st.session_state.selected_model}, has_api_key={bool(st.session_state.api_key)}")
        
        if not st.session_state.api_key:
            raise ValueError("Please configure your OpenAI API key to access premium features.")
        
        # Initialize services with API key
        st.session_state.code_generator = CodeGenerator(
            model_name=st.session_state.selected_model,
            api_key=st.session_state.api_key
        )
        
        # Initialize other services
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
    
    # Sidebar for configuration
    with st.sidebar:
        render_api_key_section()
        if 'api_key' in st.session_state and st.session_state.api_key:
            render_model_selection()
    
    # Main content area
    if 'api_key' not in st.session_state or not st.session_state.api_key:
        st.info("👋 Welcome to AI Coder Pro! Please enter your API key to get started.")
        return
    
    if not st.session_state.get('services_initialized', False):
        initialize_services()
    
    # Add your main app content here
    st.markdown("### 🚀 Ready to Code")
    st.markdown("""
    <div class='premium-card'>
        <h4>Premium Features Available:</h4>
        <ul>
            <li>🎯 Smart Code Generation</li>
            <li>📊 Code Analysis & Optimization</li>
            <li>📝 API Documentation</li>
            <li>🔍 Performance Profiling</li>
            <li>🗃️ Database Schema Design</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

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
        templates_result = st.session_state.template_manager.list_templates()
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
        languages = {"languages": ["python", "javascript", "typescript", "java", "go"]}
    except Exception as e:
        logger.error(f"Error loading languages: {str(e)}")
        languages = {"languages": ["python", "javascript", "typescript", "java", "go"]}

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
                result = st.session_state.code_generator.generate_code(prompt, "python")
                
                if result:
                    st.markdown("### 📝 Generated Code")
                    st.code(result["code"], language="python")
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
                result = st.session_state.code_analyzer.analyze_code(code_to_analyze, "python")
                
                if result:
                    if "formatted_code" in result:
                        st.markdown("### 📝 Formatted Code")
                        st.code(result["formatted_code"], language="python")
                    
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
                    ["All"] + languages.get("languages", ["python", "javascript", "typescript", "java", "go"])
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
                            result = st.session_state.template_manager.create_template(template_name, template_desc, template_code, ["python"], [tag.strip() for tag in template_tags.split(",")])
                            
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
                                result = st.session_state.template_manager.generate_template(template_prompt, "python")
                                
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
