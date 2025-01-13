from setuptools import setup, find_packages

setup(
    name="ai-coder",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "python-dotenv>=1.0.0",
        "streamlit>=1.28.2",
        "langchain>=0.0.339",
        "langchain-community>=0.0.10",
        "pydantic>=2.5.1",
        "requests>=2.31.0",
        "python-multipart>=0.0.6",
        "black>=23.11.0",
        "pylint>=3.0.2",
        "pytest>=7.4.3",
        "httpx>=0.25.2",
        "jinja2>=3.1.2",
    ],
    python_requires=">=3.8",
)
