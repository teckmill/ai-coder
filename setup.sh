#!/bin/bash

# Install the package in development mode
pip install -e .

# Run streamlit app
cd src/ui
streamlit run streamlit_app.py
