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

# Function to validate and load CSV data
# To validate and change if plottable
def load_and_validate_csv(file, required_columns, data_type):
    """Load and validate CSV file with required columns"""
    try:
        df = pd.read_csv(file)

        # Check if required columns  exist
        missing_cols = [
            col for col in required_columns if col not in df.columns
        ]

        if missing_cols:
            st.error(f"Missing columns in {data_type} file: {missing_cols}")
            return None
        
        # Validate lat/lon are numeric
        if  'lat' in df.columns and 'lon' in df.columns:
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lon'] = pd.to_numeric(df['lon'], errors='coerce')
            
            # Remove rows with invalid coordinates
            invalid_coords = df[df['lat'].isna() | df['lon'].isna()]
            if len(invalid_coords) > 0:
                st.warning(
                    f"Removed {len(invalid_coords)} rows with invalid coordinates from {data_type}"
                )
                df = df.dropna(subset=['lat', 'lon'])
        
        if len(df) == 0:
            st.error(f"No valid data found in {data_type} file")
            return None
        
        return df 
    
    except Exception as e:
        st.error(f"Error loading {data_type} file: {str(e)}")
        return None

# ---------------------------- MAP ------------------------------------------------

# Create a map selection option in the sidebar
st.sidebar.markdown('<div class="section-header"> 🌍 Map Style </div>', unsafe_allow_html=True)
map_style = st.sidebar.selectbox(
    "Choose map style:",
    ["OpenStreetMap", "Satellite", "3D Terrain", "Dark Mode"],
    index=0
)

# Determine map center
center_lat, center_lon = 14.5995, 120.9842  # Default to Manila

# If we have data, center on the data
all_lats, all_lons = [], []

# Session state for lats and lons


# Select tile layer based on user choice
tile_configs = {
    "OpenStreetMap": {
        "tiles": "OpenStreetMap",
        "attr": "© OpenStreetMap contributors"
    },

    "Satellite": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attr": "Esri, Maxar, Earthstar Geographics"
    },

    "3D Terrain": {
        "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        "attr": "Esri, HERE, Garmin, Intermap, increment P Corp."
    },

    "Dark Mode": {
        "tiles": "CartoDB dark_matter",
        "attr": "© OpenStreetMap contributors, © CartoDB"
    }
}

tile_config = tile_configs[map_style]

# Create base map with selected style and enhanced controls
if map_style == "Satellite" or map_style == "3D Terrain":
    m = folium.Map(location=[float(center_lat), float(center_lon)],
                    zoom_start = 15,
                    tiles=None,
                    control_scale=True
    )
    folium.TileLayer(tiles=tile_config["tiles"],
                    attr = tile_config["attr"],
                    name=map_style,
                    overlay = False,
                    control = False
    ).add_to(m)

else: 
    m = folium.Map(location = [float(center_lat), float(center_lon)],
                    zoom_start=15,
                    tiles = tile_config["tiles"],
                    attr=tile_config["attr"],
                    control_scale=True
    )




# Add comprehensive CSS to make map cover full main area
st.markdown("""
<style>
/* Remove all padding and margins from main container */
.main .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
}

/* Main app container styling */
.stApp {
    overflow: hidden !important;
}

.main {
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Remove padding from app view container */
div[data-testid="stAppViewContainer"] {
    padding: 0 !important;
    margin: 0 !important;
}

/* Hide decoration, toolbar, and header */
div[data-testid="stDecoration"] {
    display: none !important;
}

div[data-testid="stToolbar"] {
    visibility: hidden !important;
    height: 0 !important;
}

div[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
}

.stAppHeader {
    display: none !important;
    height: 0 !important;
}

header[data-testid="stHeader"] {
    display: none !important;
    height: 0 !important;
}

/* Target the main content area specifically */
.main > div {
    padding: 0 !important;
    margin: 0 !important;
}

/* Remove any gaps around the map */
.element-container {
    margin: 0 !important;
    padding: 0 !important;
}

.stMarkdown {
    margin: 0 !important;
    padding: 0 !important;
}

/* Make folium map container full screen */
.folium-map {
    width: 100vw !important;
    height: 100vh !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Target streamlit folium component */
iframe {
    width: 100% !important;
    height: 100vh !important;
    border: none !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Hide main area scrollbar and ensure full coverage */
section[data-testid="stSidebar"] + div {
    overflow: hidden !important;
    padding: 0 !important;
    margin: 0 !important;
}

/* Force full width for main content */
.css-1d391kg, .css-18e3th9, .css-1lcbmhc {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* Remove any bottom padding or spacing */
.css-1y4p8pa {
    padding: 0 !important;
}

/* Additional specific targeting for Streamlit components */
div[data-testid="block-container"] {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* Target the specific streamlit container classes */
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}

/* Ensure map container takes full space */
.stContainer {
    padding: 0 !important;
    margin: 0 !important;
}

/* Force the map component to be full width */
div.stMarkdown + div {
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Additional header removal targeting */
.css-18ni7ap {
    display: none !important;
}

.css-2trqyj {
    display: none !important;
}

/* Remove any top spacing or margins */
.stApp > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}

/* Ensure main content starts at top */
.main > div:first-child {
    margin-top: 0 !important;
    padding-top: 0 !important;
}
</style>

<script>
// JavaScript to ensure full viewport coverage and remove header
function resizeMapAndRemoveHeader() {
    // Remove header elements
    const headers = document.querySelectorAll('[data-testid="stHeader"], .stAppHeader, header');
    headers.forEach(header => {
        header.style.display = 'none';
        header.style.height = '0';
        header.style.visibility = 'hidden';
    });
    
    // Remove top margins and padding from main containers
    const mainContainers = document.querySelectorAll('.main, .stApp, [data-testid="stAppViewContainer"]');
    mainContainers.forEach(container => {
        container.style.marginTop = '0';
        container.style.paddingTop = '0';
    });
    
    // Resize map containers
    const mapContainers = document.querySelectorAll('iframe');
    mapContainers.forEach(container => {
        container.style.width = '100vw';
        container.style.height = '100vh';
        container.style.margin = '0';
        container.style.padding = '0';
        container.style.border = 'none';
        container.style.position = 'absolute';
        container.style.top = '0';
        container.style.left = '0';
        container.style.zIndex = '1';
    });
}

// Run resize function multiple times to ensure it takes effect
setTimeout(resizeMapAndRemoveHeader, 500);
setTimeout(resizeMapAndRemoveHeader, 1000);
setTimeout(resizeMapAndRemoveHeader, 2000);
window.addEventListener('resize', resizeMapAndRemoveHeader);
</script>
""",
            unsafe_allow_html=True)

# Display the full-screen map covering the entire main area
map_data = st_folium(m, width=None, height=1000)