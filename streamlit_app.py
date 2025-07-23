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

</style>""", unsafe_allow_html=True)


# Initialize session state for sorting data
if 'iri_data' not in st.session_state:
    st.session_state.iri_data = None
if 'object_data' not in st.session_state:
    st.session_state.object_data = None
if 'pavement_data' not in st.session_state:
    st.session_state.pavement_data = None

# Sidebar with enhanced styling
st.sidebar.markdown('<div class="sidebar-title">Project DAAN</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-subtitle">Digital Analytics for Asset-based Navigation of Roads</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="section-header"> 📁 Data Upload & Layer Controls </div>', unsafe_allow_html = True)

# File uploaders with styling
st.sidebar.markdown('<div class="section-header"> 📤 Upload Data Files </div>', unsafe_allow_html=True)
