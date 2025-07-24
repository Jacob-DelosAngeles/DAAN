import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from PIL import Image
import os
import base64
from io import BytesIO
from folium import plugins

# Page configuration
st.set_page_config(
    page_title="Project DAAN: Digital Analytics for Asset-based Navigation of Roads",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Enhanced sidebar styling
st.markdown("""
<style>
.sidebar .sidebar-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

.stSidebar > div:first-child {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.sidebar-title {
    font-size: 24px;
    font-weight: bold;
    color: #2c3e50;
    margin-bottom: 0.5rem;
    text-align: center;
    border-bottom: 2px solid #3498db;
    padding-bottom: 0.5rem;
}

.sidebar-subtitle {
    font-size: 14px;
    color: #7f8cd8d;
    text-align: center;
    margin-bottom: 1.5rem;
    font-style: italic;
}

.section-header {
    background: #34495e;
    color: white;
    padding: 0.5rem;
    border-radius: 5px;
    margin: 1rem 0 0.5rem 0;
    font-weight: bold;
    text-align: center;

.stFileUploaer > div {
    background-color: #f8f9fa;
    border: 2px dashed #bdc3c7;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
}

</style>""", unsafe_allow_html=True)


# Initialize session state for sorting data
if 'iri_data' not in st.session_state:
    st.session_state.iri_data = None
if 'object_data' not in st.session_state:
    st.session_state.object_data = None
if 'pavement_data' not in st.session_state:
    st.session_state.pavement_data = None

# Sidebar with enhanced styling
st.sidebar.markdown('<div class="sidebar-title">Project DAAN Express</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-subtitle">Digital Analytics for Asset-based Navigation of Roads</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="section-header"> 📁 Data Upload & Layer Controls </div>', unsafe_allow_html = True)

# File uploaders with styling
st.sidebar.markdown('<div class="section-header"> 📤 Upload Data Files </div>', unsafe_allow_html=True)

# IRI Data Upload
iri_file = st.sidebar.file_uploader(
    "Upload IRI Data CSV",
    type=['csv'],
    help="CSV with columns: lat, lon, iri_score",
    key = "iri_upload"
)

# Vehicle Detection Data Upload
vehicle_file = st.sidebar.file_uploader(
    "Upload Vehicle Detection Data CSV",
    type=['csv'],
    help="CSV with columns: lat, lon, type of vehicle",
    key="vehicle_upload",
)

# Pothole Detection Data Upload
pothole_file = st.sidebar.file_uploader(
    "Upload Pothole Detection Data CSV",
    type=['csv'],
    help="CSV with columns: lat, lon, image_path",
    key="pothole_upload"
)


