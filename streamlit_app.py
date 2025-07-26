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
from utils.iri_calculator import IRICalculator
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

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
}

.stFileUploaer > div {
    background-color: #f8f9fa;
    border: 2px dashed #bdc3c7;
    border-radius: 10px;
    padding: 1rem;
    margin: 0.5rem 0;
}

.iri-metric {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 1rem;
    border-radius: 10px;
    margin: 0.5rem 0;
    text-align: center;
    border: 2px solid #ffffff;
}

.iri-value {
    font-size: 2rem;
    font-weight: bold;
    margin: 0.5rem 0;
}

.quality-assessment {
    background: #f8f9fa;
    border-left: 5px solid #28a745;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}

.quality-good { border-left-color: #28a745; }
.quality-fair { border-left-color: #ffc107; }
.quality-poor { border-left-color: #fd7e14; }
.quality-bad { border-left-color: #dc3545; }

/* Expander styling to match app design */
.streamlit-expanderHeader {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    font-weight: bold !important;
    border: 2px solid #ffffff !important;
    margin: 0.5rem 0 !important;
}

.streamlit-expanderContent {
    background: #f8f9fa !important;
    border-radius: 10px !important;
    padding: 1rem !important;
    margin: 0.5rem 0 !important;
    border: 1px solid #e9ecef !important;
}

</style>""", unsafe_allow_html=True)

# Initialize session state for data and IRI calculation
if 'vehicle_data' not in st.session_state:
    st.session_state.vehicle_data = None
if 'pothole_data' not in st.session_state:
    st.session_state.pothole_data = None
if 'iri_calculation_result' not in st.session_state:
    st.session_state.iri_calculation_result = None
if 'current_iri_file' not in st.session_state:
    st.session_state.current_iri_file = None

# Sidebar with enhanced styling
st.sidebar.markdown('<div class="sidebar-title">Project DAAN Express</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-subtitle">Digital Analytics for Asset-based Navigation of Roads</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="section-header"> 📁 Data Upload & Layer Controls </div>', unsafe_allow_html = True)

# File uploaders with styling
st.sidebar.markdown('<div class="section-header"> 📤 Upload Data Files </div>', unsafe_allow_html=True)



# Vehicle Detection Data Upload
vehicle_file = st.sidebar.file_uploader(
    "Upload Vehicle Detection Data CSV",
    type=['csv'],
    help="CSV with columns: lat, lon, vehicle_type",
    key="vehicle_upload",
)

# Pothole Detection Data Upload
pothole_file = st.sidebar.file_uploader(
    "Upload Pothole Detection Data CSV",
    type=['csv'],
    help="CSV with columns: lat, lon, image_path",
    key="pothole_upload"
)

# IRI Sensor Data Upload for calculation
iri_sensor_file = st.sidebar.file_uploader(
    "Upload IRI Sensor Data CSV",
    type=['csv'],
    help="CSV with columns: time, ax, ay, az (from Physics Toolbox Sensor Suite)",
    key="iri_sensor_upload"
)

# Automatic IRI calculation when file is uploaded
if iri_sensor_file is not None:
    # Check if this is a new file (to avoid recalculation on every rerun)
    if 'current_iri_file' not in st.session_state or st.session_state.current_iri_file != iri_sensor_file.name:
        try:
            # Initialize IRI Calculator
            iri_calc = IRICalculator()
            
            # Load and process data
            df = pd.read_csv(iri_sensor_file)
            df_processed, duration = iri_calc.preprocess_data(df)
            
            if df_processed is not None:
                # Calculate IRI with default segment length of 150
                iri_values, segments, sampling_rate, speed = iri_calc.calculate_iri_rms_method(df_processed, 150)
                
                # Check if calculation was successful
                if not iri_values or len(iri_values) == 0:
                    st.sidebar.error("❌ No IRI values calculated. Check your data format.")
                else:
                    # Calculate statistics
                    mean_iri = np.mean(iri_values)
                    std_iri = np.std(iri_values)
                    segment_centers = [s['distance_start'] + s['length']/2 for s in segments]
                    total_distance = segment_centers[-1] + (segments[-1]['length']/2) if segment_centers else 0
                    
                    # Store results in session state
                    st.session_state.iri_calculation_result = {
                        'iri_values': iri_values,
                        'segments': segments,
                        'segment_centers': segment_centers,
                        'mean_iri': mean_iri,
                        'std_iri': std_iri,
                        'sampling_rate': sampling_rate,
                        'speed': speed,
                        'duration': duration,
                        'total_distance': total_distance,
                        'df_processed': df_processed
                    }
                    
                    # Store current file name to avoid recalculation
                    st.session_state.current_iri_file = iri_sensor_file.name
                    st.sidebar.success("✅ IRI calculation completed!")
            else:
                st.sidebar.error("❌ Data preprocessing failed")
        except Exception as e:
            st.sidebar.error(f"❌ Error calculating IRI: {str(e)}")

# Display IRI Results if available
if st.session_state.iri_calculation_result:
    result = st.session_state.iri_calculation_result
    
    # IRI Results Expander
    with st.sidebar.expander("📊 IRI Results", expanded= False):
        # IRI Value
        st.markdown(f"""
        <div class="iri-metric">
            <div>🛣️ IRI Value</div>
            <div class="iri-value">{result['mean_iri']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Road Quality
        if result['mean_iri'] <= 3:
            quality = 'Good'
            quality_class = 'quality-good'
        elif result['mean_iri'] <= 5:
            quality = 'Fair'
            quality_class = 'quality-fair'
        elif result['mean_iri'] <= 7:
            quality = 'Poor'
            quality_class = 'quality-poor'
        else:
            quality = 'Bad'
            quality_class = 'quality-bad'
        
        st.markdown(f"""
        <div class="iri-metric">
            <div>⭐ Road Quality</div>
            <div class="iri-value">{quality}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Standard Deviation
        st.markdown(f"""
        <div class="iri-metric">
            <div>📊 Standard Deviation</div>
            <div class="iri-value">{result['std_iri']:.2f}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quality Assessment
        def get_quality_assessment(iri_value):
            if iri_value <= 3:
                return {
                    'rating': 'Good',
                    'description': 'Acceptable pavement condition',
                    'interpretation': 'This pavement provides good ride quality with acceptable smoothness. Vehicle operating costs are within normal range and user comfort is satisfactory.',
                    'recommendations': 'Condition with routine maintenance activities. Monitor condition annually and apply preventive treatments as needed to maintain current service level.'
                }
            elif iri_value <= 5:
                return {
                    'rating': 'Fair',
                    'description': 'Moderate pavement roughness',
                    'interpretation': 'This pavement shows moderate roughness that begins to affect ride quality. Some increase in vehicle operating costs and minor user discomfort may be experienced.',
                    'recommendations': 'Plan for rehabilitation treatments within 3-5 years. Consider surface treatments or minor structural improvements to prevent further deterioration.'
                }
            elif iri_value <= 7:
                return {
                    'rating': 'Poor',
                    'description': 'Significant pavement deterioration',
                    'interpretation': 'This pavement has significant roughness that notably impacts ride quality and increases vehicle operating costs. User comfort is compromised and maintenance costs are elevated.',
                    'recommendations': 'Prioritize major rehabilitation or reconstruction within 2-3 years. Implement interim maintenance to prevent further rapid deterioration and safety issues.'
                }
            else:
                return {
                    'rating': 'Bad',
                    'description': 'Severe pavement distress',
                    'interpretation': 'This pavement exhibits severe roughness causing substantial user discomfort, high vehicle operating costs, and potential safety concerns. Structural integrity may be compromised.',
                    'recommendations': 'Immediate major rehabilitation or full reconstruction required. Consider emergency repairs if safety is compromised. Evaluate load restrictions until permanent repairs are completed.'
                }
        
        quality_info = get_quality_assessment(result['mean_iri'])
        
        st.markdown(f"""
        <div class="quality-assessment {quality_class}">
            <h4>🎯 Quality Assessment</h4>
            <p><strong>Rating:</strong> {quality_info['rating']} ({quality_info['description']})</p>
            <p><strong>Interpretation:</strong> {quality_info['interpretation']}</p>
            <p><strong>Recommendations:</strong> {quality_info['recommendations']}</p>
        </div>
        """, unsafe_allow_html=True)

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

# Load and validate the data files
# vehicle_file, pothole_file

if vehicle_file is not None:
    st.session_state.vehicle_data = load_and_validate_csv(
        vehicle_file, ['lat', 'lon', 'vehicle_type'], "Vehicle Data"
    )

if pothole_file is not None:
    st.session_state.pothole_data = load_and_validate_csv(
        pothole_file, ['lat', 'lon', 'image_path'], "Pothole Data"
    )

# Layer toggle controls with styling
st.sidebar.markdown('<div class="section-header"> 🗺️ Data Layers </div>', unsafe_allow_html=True)

layer_controls = {}
layer_controls['iri'] = st.sidebar.checkbox("IRI Values", value=True, disabled=st.session_state.iri_calculation_result is None)
layer_controls['vehicles'] = st.sidebar.checkbox("Vehicles", value=True, disabled=st.session_state.vehicle_data is None)
layer_controls['pothole'] = st.sidebar.checkbox("Potholes", value=True, disabled=st.session_state.pothole_data is None)

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

# Collect IRI data coordinates for map centering
iri_lats = []
iri_lons = []
if st.session_state.iri_calculation_result and layer_controls['iri']:
    result = st.session_state.iri_calculation_result
    df_processed = result['df_processed']
    
    # Check if GPS data is available
    if 'latitude' in df_processed.columns and 'longitude' in df_processed.columns:
        # Get coordinates for each segment
        for i, segment in enumerate(result['segments']):
            if i < len(result['iri_values']):
                idx = segment['center_index']
                if 0 <= idx < len(df_processed):
                    lat = df_processed.iloc[idx]['latitude']
                    lon = df_processed.iloc[idx]['longitude']
                    iri_lats.append(lat)
                    iri_lons.append(lon)

# Session state for lats and lons

# Update map center based on available data
if all_lats and all_lons:
    center_lat = np.mean(all_lats)
    center_lon = np.mean(all_lons)
elif iri_lats and iri_lons:
    center_lat = np.mean(iri_lats)
    center_lon = np.mean(iri_lons)

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

# Add IRI data to map if available
if st.session_state.iri_calculation_result and layer_controls['iri']:
    result = st.session_state.iri_calculation_result
    df_processed = result['df_processed']
    
    # Check if GPS data is available
    if 'latitude' in df_processed.columns and 'longitude' in df_processed.columns:
        # Get coordinates for each segment
        for i, segment in enumerate(result['segments']):
            if i < len(result['iri_values']):
                idx = segment['center_index']
                if 0 <= idx < len(df_processed):
                    lat = df_processed.iloc[idx]['latitude']
                    lon = df_processed.iloc[idx]['longitude']
                    iri_value = result['iri_values'][i]
                    
                    # Determine color based on IRI value
                    if iri_value <= 3:
                        color = 'green'
                        quality = 'Good'
                    elif iri_value <= 5:
                        color = 'yellow'
                        quality = 'Fair'
                    elif iri_value <= 7:
                        color = 'orange'
                        quality = 'Poor'
                    else:
                        color = 'red'
                        quality = 'Bad'
                    
                    # Add marker to map
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=8,
                        popup=f'IRI: {iri_value:.2f}<br>Quality: {quality}',
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.7,
                        weight=2
                    ).add_to(m)

# Add legend for IRI values if IRI data is available
if st.session_state.iri_calculation_result and layer_controls['iri']:
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>IRI Quality Legend</b></p>
    <p><i class="fa fa-circle" style="color:green"></i> Good (≤3)</p>
    <p><i class="fa fa-circle" style="color:yellow"></i> Fair (3-5)</p>
    <p><i class="fa fa-circle" style="color:orange"></i> Poor (5-7)</p>
    <p><i class="fa fa-circle" style="color:red"></i> Bad (>7)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

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

