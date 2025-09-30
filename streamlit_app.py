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
    initial_sidebar_state="collapsed",
)

# Enhanced sidebar styling
st.markdown("""
<style>
.sidebar .sidebar-content {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
}

/* Style only the content part of the sidebar, not the toggle button */
.stSidebar > div:nth-child(2) {
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

/* Ensure the sidebar toggle button is always visible */
[data-testid="collapsedControl"] {
    display: flex !important;
    visibility: visible !important;
    color: black !important;  /* Adjust if blending with background */
    z-index: 999 !important;
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
    margin: 64px 0 0.5rem 0; /* Updated margin-top to 64px */
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
if 'pothole_images_data' not in st.session_state:
    st.session_state.pothole_images_data = None
if 'current_pothole_file' not in st.session_state:
    st.session_state.current_pothole_file = None
if 'iri_calculation_result' not in st.session_state:
    st.session_state.iri_calculation_result = None
if 'current_iri_file' not in st.session_state:
    st.session_state.current_iri_file = None

# Sidebar with enhanced styling
st.sidebar.markdown('<div class="sidebar-title">Project DAAN Express</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="sidebar-subtitle">Digital Analytics for Asset-based Navigation of Roads</div>', unsafe_allow_html=True)
#st.sidebar.markdown('<div class="section-header"> 📁 Data Upload & Layer Controls </div>', unsafe_allow_html = True)

# File uploaders with styling
st.sidebar.markdown('<div class="section-header"> 📤 Upload Data Files </div>', unsafe_allow_html=True)



# Vehicle Detection Data Upload
vehicle_file = st.sidebar.file_uploader(
    "Upload Vehicle Detection Data CSV",
    type=['csv'],
    help="CSV with columns: latitude, longitude, vehicle_type",
    key="vehicle_upload",
)

# Pothole Images Data Upload (with image paths)
pothole_images_file = st.sidebar.file_uploader(
    "Upload Pothole Images Data CSV",
    type=['csv'],
    help="CSV with columns: latitude, longitude, image_path, confidence_score",
    key="pothole_images_upload"
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
                iri_values, segments, sampling_rate, speed = iri_calc.calculate_iri_rms_method(df_processed, 25)
                
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

# Function to validate and load CSV data
# To validate and change if plottable
def load_and_validate_csv(file, required_columns, data_type):
    """Load and validate CSV file with required columns"""
    try:
        df = pd.read_csv(file)
        
        # Debug: Show available columns
        st.sidebar.info(f"📋 Available columns in {data_type}: {list(df.columns)}")

        # Check if required columns  exist
        missing_cols = [
            col for col in required_columns if col not in df.columns
        ]

        if missing_cols:
            st.error(f"Missing columns in {data_type} file: {missing_cols}")
            st.error(f"Available columns: {list(df.columns)}")
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
        elif 'latitude' in df.columns and 'longitude' in df.columns:
            df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
            df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
            
            # Remove rows with invalid coordinates
            invalid_coords = df[df['latitude'].isna() | df['longitude'].isna()]
            if len(invalid_coords) > 0:
                st.warning(
                    f"Removed {len(invalid_coords)} rows with invalid coordinates from {data_type}"
                )
                df = df.dropna(subset=['latitude', 'longitude'])
        
        if len(df) == 0:
            st.error(f"No valid data found in {data_type} file")
            return None
        
        return df 
    
    except Exception as e:
        st.error(f"Error loading {data_type} file: {str(e)}")
        return None

# Automatic vehicle data loading when file is uploaded
if vehicle_file is not None:
    # Check if this is a new file (to avoid reloading on every rerun)
    if 'current_vehicle_file' not in st.session_state or st.session_state.current_vehicle_file != vehicle_file.name:
        try:
            # Load and validate vehicle data
            vehicle_df = load_and_validate_csv(
                vehicle_file, 
                ['latitude', 'longitude', 'vehicle_type'], 
                "Vehicle Detection Data"
            )
            
            if vehicle_df is not None:
                # Filter to only include car, bicycle, and truck
                valid_vehicle_types = ['car', 'bicycle', 'truck']
                vehicle_df_filtered = vehicle_df[vehicle_df['vehicle_type'].isin(valid_vehicle_types)].copy()
                
                # Change 'bicycle' to 'motorcycle' in the data
                vehicle_df_filtered['vehicle_type'] = vehicle_df_filtered['vehicle_type'].replace('bicycle', 'motorcycle')
                
                # Count vehicles by type
                vehicle_counts = vehicle_df_filtered['vehicle_type'].value_counts()
                
                # Store data in session state
                st.session_state.vehicle_data = vehicle_df_filtered
                st.session_state.current_vehicle_file = vehicle_file.name
                st.sidebar.success(f"✅ Loaded {len(vehicle_df_filtered)} vehicle detections!")
            else:
                st.sidebar.error("❌ Failed to load vehicle detection data")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading vehicle detection data: {str(e)}")

# Automatic pothole images data loading when file is uploaded
if pothole_images_file is not None:
    # Check if this is a new file (to avoid reloading on every rerun)
    if 'current_pothole_file' not in st.session_state or st.session_state.current_pothole_file != pothole_images_file.name:
        try:
            # Smart relative path detection system
            def find_images_folder():
                """Intelligently find images folder relative to common CSV locations"""
                
                # First priority: Look for ../images folder relative to current working directory
                parent_images_path = os.path.join("..", "images")
                if os.path.exists(parent_images_path):
                    image_count = len([f for f in os.listdir(parent_images_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
                    if image_count > 0:
                        return parent_images_path, image_count
                
                # Second priority: Look for images folder in current directory
                current_images_path = "images"
                if os.path.exists(current_images_path):
                    image_count = len([f for f in os.listdir(current_images_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
                    if image_count > 0:
                        return current_images_path, image_count
                
                # Third priority: Look for images folder in streamlit_package directory
                streamlit_images_path = "streamlit_package/images"
                if os.path.exists(streamlit_images_path):
                    image_count = len([f for f in os.listdir(streamlit_images_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
                    if image_count > 0:
                        return streamlit_images_path, image_count
                
                # Fourth priority: Common CSV locations and their corresponding images folders
                csv_image_pairs = [
                    ("UPLB/streamlit_package/data/", "UPLB/streamlit_package/images/"),
                    ("streamlit_package/data/", "streamlit_package/images/"),
                    ("UPLB/data/", "UPLB/images/"),
                    ("data/", "images/"),
                    ("UPLB/streamlit_package/", "UPLB/streamlit_package/images/"),
                    ("streamlit_package/", "streamlit_package/images/"),
                    ("UPLB/", "UPLB/images/"),
                    ("./", "images/")
                ]
                
                # Check each pair for images folder
                for csv_path, images_path in csv_image_pairs:
                    if os.path.exists(images_path):
                        image_count = len([f for f in os.listdir(images_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
                        if image_count > 0:
                            return images_path, image_count
                
                # If no pairs found, search recursively for any images folder
                for root, dirs, files in os.walk("."):
                    if "images" in dirs:
                        potential_path = os.path.join(root, "images")
                        if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(potential_path)):
                            image_count = len([f for f in os.listdir(potential_path) if f.endswith(('.jpg', '.jpeg', '.png'))])
                            return potential_path, image_count
                
                # Final fallback
                return "UPLB/streamlit_package/images/", 0
            
            # Find the best images folder
            images_base_path, image_count = find_images_folder()
            
            # Show which images folder was found
            st.sidebar.info(f"🔍 Found images folder: {images_base_path} ({image_count} images)")
            
            # Load available images from the found folder
            available_images = []
            if os.path.exists(images_base_path):
                available_images = [f for f in os.listdir(images_base_path) if f.endswith(('.jpg', '.jpeg', '.png'))]
                available_images.sort()
            
            # Store the found images path in session state for reuse
            st.session_state.images_base_path = images_base_path
            
            # Load and validate pothole images data
            pothole_df = load_and_validate_csv(
                pothole_images_file, 
                ['latitude', 'longitude', 'image_path', 'confidence_score'], 
                "Pothole Images Data"
            )
            
            if pothole_df is not None:
                # Extract frame numbers from image_path and sort the data
                def extract_frame_number(image_path):
                    """Extract frame number from image path like 'frame_123.jpg'"""
                    try:
                        # Extract the number after 'frame_' and before '.jpg'
                        frame_part = image_path.split('frame_')[1].split('.')[0]
                        return int(frame_part)
                    except (IndexError, ValueError):
                        # If extraction fails, return a large number to put it at the end
                        return 999999
                
                # Add frame number column for sorting
                pothole_df['frame_number'] = pothole_df['image_path'].apply(extract_frame_number)
                
                # Validate that images exist and show debugging info
                # Use the same images_base_path that was found above
                missing_images = []
                valid_images = []
                
                for idx, row in pothole_df.iterrows():
                    full_image_path = os.path.join(images_base_path, row['image_path'])
                    if os.path.exists(full_image_path):
                        valid_images.append(row['image_path'])
                    else:
                        missing_images.append(row['image_path'])
                
                # Show validation results (minimal info)
                if missing_images:
                    st.sidebar.warning(f"⚠️ {len(missing_images)} images not found")
                else:
                    st.sidebar.success(f"✅ All {len(valid_images)} images found")
                
                # Sort by frame number (ascending order)
                pothole_df = pothole_df.sort_values('frame_number').reset_index(drop=True)
                
                # Store data in session state
                st.session_state.pothole_images_data = pothole_df
                st.session_state.current_pothole_file = pothole_images_file.name
                
                st.sidebar.success(f"✅ Loaded {len(pothole_df)} pothole detections")
            else:
                st.sidebar.error("❌ Failed to load pothole images data")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading pothole images data: {str(e)}")

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

# Display Vehicle Statistics if available
if st.session_state.vehicle_data is not None:
    vehicle_df = st.session_state.vehicle_data
    
    # Vehicle Statistics Expander
    with st.sidebar.expander("🚗 Vehicle Detections", expanded=False):
        # Total detections
        st.markdown(f"""
        <div class="iri-metric">
            <div>📊 Total Vehicles</div>
            <div class="iri-value">{len(vehicle_df)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Vehicle type breakdown
        vehicle_counts = vehicle_df['vehicle_type'].value_counts()
        
        # Cars
        car_count = vehicle_counts.get('car', 0)
        st.markdown(f"""
        <div class="iri-metric">
            <div>🚗 Cars</div>
            <div class="iri-value">{car_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Trucks
        truck_count = vehicle_counts.get('truck', 0)
        st.markdown(f"""
        <div class="iri-metric">
            <div>🚛 Trucks</div>
            <div class="iri-value">{truck_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Motorcycles
        motorcycle_count = vehicle_counts.get('motorcycle', 0)
        st.markdown(f"""
        <div class="iri-metric">
            <div>🏍️ Motorcycles</div>
            <div class="iri-value">{motorcycle_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Coverage area (approximate)
        lat_range = vehicle_df['latitude'].max() - vehicle_df['latitude'].min()
        lon_range = vehicle_df['longitude'].max() - vehicle_df['longitude'].min()
        coverage_km = max(lat_range, lon_range) * 111  # Rough conversion to km
        st.markdown(f"""
        <div class="iri-metric">
            <div>🗺️ Coverage Area</div>
            <div class="iri-value">{coverage_km:.1f} km</div>
        </div>
        """, unsafe_allow_html=True)

# Display Pothole Images Statistics if available
if st.session_state.pothole_images_data is not None:
    pothole_df = st.session_state.pothole_images_data
    
    # Pothole Images Statistics Expander
    with st.sidebar.expander("🚧 Pothole Detections", expanded=False):
        # Total detections
        st.markdown(f"""
        <div class="iri-metric">
            <div>📊 Total Detections</div>
            <div class="iri-value">{len(pothole_df)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Average confidence
        avg_confidence = pothole_df['confidence_score'].mean()
        st.markdown(f"""
        <div class="iri-metric">
            <div>🎯 Average Confidence</div>
            <div class="iri-value">{avg_confidence:.1%}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # High confidence detections (>80%)
        high_conf_count = len(pothole_df[pothole_df['confidence_score'] > 0.8])
        st.markdown(f"""
        <div class="iri-metric">
            <div>⭐ High Confidence (>80%)</div>
            <div class="iri-value">{high_conf_count}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Coverage area (approximate)
        lat_range = pothole_df['latitude'].max() - pothole_df['latitude'].min()
        lon_range = pothole_df['longitude'].max() - pothole_df['longitude'].min()
        coverage_km = max(lat_range, lon_range) * 111  # Rough conversion to km
        st.markdown(f"""
        <div class="iri-metric">
            <div>🗺️ Coverage Area</div>
            <div class="iri-value">{coverage_km:.1f} km</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Image viewer section
        st.markdown("---")
        st.markdown("**🔍 Current Page Images**")
        
        # Get current page of images
        page_size = 10
        page = st.session_state.pothole_page if 'pothole_page' in st.session_state else 0
        start_idx = page * page_size
        end_idx = min(start_idx + page_size, len(pothole_df))
        current_page_df = pothole_df.iloc[start_idx:end_idx]
        
        # Display images for current page
        for idx, row in current_page_df.iterrows():
            # Create a container for each image
            with st.container():
                frame_num = row.get('frame_number', 'N/A')
                st.markdown(f"**Image {idx-start_idx+1}:** Frame {frame_num} - {row['image_path']} ({row['confidence_score']:.1%})")
                st.write(f"**Location:** {row['latitude']:.6f}, {row['longitude']:.6f}")
                
                # Load and display the image
                # Use the stored images_base_path from session state, with smart fallback
                sidebar_images_base_path = st.session_state.get('images_base_path')
                if not sidebar_images_base_path:
                    # Smart fallback detection using the same logic
                    def find_images_folder_sidebar():
                        # First priority: Look for ../images folder relative to current working directory
                        parent_images_path = os.path.join("..", "images")
                        if os.path.exists(parent_images_path):
                            if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(parent_images_path)):
                                return parent_images_path
                        
                        # Second priority: Look for images folder in current directory
                        current_images_path = "images"
                        if os.path.exists(current_images_path):
                            if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(current_images_path)):
                                return current_images_path
                        
                        # Third priority: Look for images folder in streamlit_package directory
                        streamlit_images_path = "streamlit_package/images"
                        if os.path.exists(streamlit_images_path):
                            if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(streamlit_images_path)):
                                return streamlit_images_path
                        
                        # Fourth priority: Common CSV locations and their corresponding images folders
                        csv_image_pairs = [
                            ("UPLB/streamlit_package/data/", "UPLB/streamlit_package/images/"),
                            ("streamlit_package/data/", "streamlit_package/images/"),
                            ("UPLB/data/", "UPLB/images/"),
                            ("data/", "images/"),
                            ("UPLB/streamlit_package/", "UPLB/streamlit_package/images/"),
                            ("streamlit_package/", "streamlit_package/images/"),
                            ("UPLB/", "UPLB/images/"),
                            ("./", "images/")
                        ]
                        
                        for csv_path, images_path in csv_image_pairs:
                            if os.path.exists(images_path):
                                if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(images_path)):
                                    return images_path
                        
                        # Recursive search fallback
                        for root, dirs, files in os.walk("."):
                            if "images" in dirs:
                                potential_path = os.path.join(root, "images")
                                if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(potential_path)):
                                    return potential_path
                        
                        return "UPLB/streamlit_package/images/"
                    
                    sidebar_images_base_path = find_images_folder_sidebar()
                    st.sidebar.info(f"🔍 Sidebar using images folder: {sidebar_images_base_path}")
                
                full_image_path = os.path.join(sidebar_images_base_path, row['image_path'])
                if os.path.exists(full_image_path):
                    try:
                        image = Image.open(full_image_path)
                        st.image(image, caption=f"Pothole Detection: Frame {frame_num} - {row['image_path']}", use_container_width=True)
                    except Exception as e:
                        st.error(f"Error loading image: {str(e)}")
                else:
                    st.error(f"Image file not found: {full_image_path}")
                
                # Add separator between images
                st.markdown("---")



# Load and validate the data files
# Note: Vehicle data is now handled in the automatic loading section above



# Layer toggle controls with styling
st.sidebar.markdown('<div class="section-header"> 🗺️ Data Layers </div>', unsafe_allow_html=True)

layer_controls = {}
layer_controls['iri'] = st.sidebar.checkbox("IRI Values", value=True, disabled=st.session_state.iri_calculation_result is None)
layer_controls['vehicles'] = st.sidebar.checkbox("Vehicles", value=True, disabled=st.session_state.vehicle_data is None)
# Remove the old Potholes checkbox
# layer_controls['pothole'] = st.sidebar.checkbox("Potholes", value=True, disabled=st.session_state.pothole_data is None)
layer_controls['pothole_images'] = st.sidebar.checkbox("Pothole Images", value=True, disabled=st.session_state.pothole_images_data is None)

# Configuration for pothole images display
if st.session_state.pothole_images_data is not None:
    st.sidebar.markdown('<div class="section-header"> ⚙️ Pothole Image Viewer </div>', unsafe_allow_html=True)
    
    # Fixed page size of 10 images for better performance
    page_size = 10
    
    # Pagination state
    if 'pothole_page' not in st.session_state:
        st.session_state.pothole_page = 0
    total_markers = len(st.session_state.pothole_images_data)
    total_pages = (total_markers - 1) // page_size + 1
    
    # Navigation buttons
    col1, col2, col3 = st.sidebar.columns([1,2,1])
    with col1:
        if st.button('⬅️ Previous', key='prev_pothole_page'):
            if st.session_state.pothole_page > 0:
                st.session_state.pothole_page -= 1
    with col3:
        if st.button('Next ➡️', key='next_pothole_page'):
            if st.session_state.pothole_page < total_pages - 1:
                st.session_state.pothole_page += 1
    
    # Show current page info
    start_idx = st.session_state.pothole_page * page_size
    end_idx = min(start_idx + page_size, total_markers)
    st.sidebar.markdown(f"<div style='text-align:center; margin-bottom:8px;'>Showing images <b>{start_idx+1}–{end_idx}</b> of <b>{total_markers}</b></div>", unsafe_allow_html=True)

# ---------------------------- MAP ------------------------------------------------

# NOTE: In Streamlit, any widget interaction (including map zoom/pan) triggers a rerun of the script.
# This is expected behavior. To minimize performance impact, cache heavy data and limit marker/image rendering.
# For persistent, non-refreshing maps, consider using Dash or a JS-based framework.

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

# Collect vehicle data coordinates for map centering
vehicle_lats = []
vehicle_lons = []
if st.session_state.vehicle_data is not None and layer_controls['vehicles']:
    vehicle_lats = st.session_state.vehicle_data['latitude'].tolist()
    vehicle_lons = st.session_state.vehicle_data['longitude'].tolist()

# Collect pothole images data coordinates for map centering
pothole_images_lats = []
pothole_images_lons = []
if st.session_state.pothole_images_data is not None and layer_controls['pothole_images']:
    pothole_images_lats = st.session_state.pothole_images_data['latitude'].tolist()
    pothole_images_lons = st.session_state.pothole_images_data['longitude'].tolist()

# Session state for lats and lons

# Update map center based on available data (Priority: 1. Pothole, 2. Vehicles, 3. IRI)
if pothole_images_lats and pothole_images_lons:
    center_lat = np.mean(pothole_images_lats)
    center_lon = np.mean(pothole_images_lons)
elif vehicle_lats and vehicle_lons:
    center_lat = np.mean(vehicle_lats)
    center_lon = np.mean(vehicle_lons)
elif iri_lats and iri_lons:
    center_lat = np.mean(iri_lats)
    center_lon = np.mean(iri_lons)
elif all_lats and all_lons:
    center_lat = np.mean(all_lats)
    center_lon = np.mean(all_lons)

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
        # Create color-changing continuous line based on IRI values
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
                    
                    # Create a small line segment for this IRI value
                    # Get the next coordinate for the line segment
                    if i + 1 < len(result['segments']):
                        next_idx = result['segments'][i + 1]['center_index']
                        if next_idx < len(df_processed):
                            next_lat = df_processed.iloc[next_idx]['latitude']
                            next_lon = df_processed.iloc[next_idx]['longitude']
                            
                            # Create line segment with color based on IRI value
                            folium.PolyLine(
                                locations=[[lat, lon], [next_lat, next_lon]],
                                popup=f'IRI: {iri_value:.2f}<br>Quality: {quality}',
                                color=color,
                                weight=6,
                                opacity=0.8
                            ).add_to(m)
                    else:
                        # For the last segment, create a small line in the same direction
                        # Use the previous segment's direction
                        if i > 0:
                            prev_idx = result['segments'][i - 1]['center_index']
                            if prev_idx < len(df_processed):
                                prev_lat = df_processed.iloc[prev_idx]['latitude']
                                prev_lon = df_processed.iloc[prev_idx]['longitude']
                                
                                # Calculate direction vector
                                dlat = lat - prev_lat
                                dlon = lon - prev_lon
                                
                                # Create a small line segment in the same direction
                                end_lat = lat + dlat * 0.5
                                end_lon = lon + dlon * 0.5
                                
                                folium.PolyLine(
                                    locations=[[lat, lon], [end_lat, end_lon]],
                                    popup=f'IRI: {iri_value:.2f}<br>Quality: {quality}',
                                    color=color,
                                    weight=6,
                                    opacity=0.8
                                ).add_to(m)

# Add pothole images to map if available
if st.session_state.pothole_images_data is not None and layer_controls['pothole_images']:
    pothole_df = st.session_state.pothole_images_data
    
    # Use the stored images_base_path from session state, with smart fallback detection
    images_base_path = st.session_state.get('images_base_path')
    if not images_base_path:
        # Smart fallback detection using the same logic
        def find_images_folder_fallback():
            # First priority: Look for ../images folder relative to current working directory
            parent_images_path = os.path.join("..", "images")
            if os.path.exists(parent_images_path):
                if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(parent_images_path)):
                    return parent_images_path
            
            # Second priority: Look for images folder in current directory
            current_images_path = "images"
            if os.path.exists(current_images_path):
                if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(current_images_path)):
                    return current_images_path
            
            # Third priority: Look for images folder in streamlit_package directory
            streamlit_images_path = "streamlit_package/images"
            if os.path.exists(streamlit_images_path):
                if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(streamlit_images_path)):
                    return streamlit_images_path
            
            # Fourth priority: Common CSV locations and their corresponding images folders
            csv_image_pairs = [
                ("UPLB/streamlit_package/data/", "UPLB/streamlit_package/images/"),
                ("streamlit_package/data/", "streamlit_package/images/"),
                ("UPLB/data/", "UPLB/images/"),
                ("data/", "images/"),
                ("UPLB/streamlit_package/", "UPLB/streamlit_package/images/"),
                ("streamlit_package/", "streamlit_package/images/"),
                ("UPLB/", "UPLB/images/"),
                ("./", "images/")
            ]
            
            for csv_path, images_path in csv_image_pairs:
                if os.path.exists(images_path):
                    if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(images_path)):
                        return images_path
            
            # Recursive search fallback
            for root, dirs, files in os.walk("."):
                if "images" in dirs:
                    potential_path = os.path.join(root, "images")
                    if any(f.endswith(('.jpg', '.jpeg', '.png')) for f in os.listdir(potential_path)):
                        return potential_path
            
            return "UPLB/streamlit_package/images/"
        
        images_base_path = find_images_folder_fallback()
        st.sidebar.info(f"🔍 Using fallback images folder: {images_base_path}")
    
    # Show progress for loading ALL markers
    with st.spinner(f"Loading {len(pothole_df)} pothole markers on map..."):
        # Display ALL markers on the map
        for idx, row in pothole_df.iterrows():
            try:
                lat = row['latitude']
                lon = row['longitude']
                image_path = row['image_path']
                confidence = row['confidence_score']
                
                # Check if this marker is in the current page for image loading
                page_size = 10
                page = st.session_state.pothole_page if 'pothole_page' in st.session_state else 0
                start_idx = page * page_size
                end_idx = min(start_idx + page_size, len(pothole_df))
                is_in_current_page = start_idx <= idx < end_idx
                
                full_image_path = os.path.join(images_base_path, image_path)
                
                # Only load image data for markers in the current page (for performance)
                if is_in_current_page and os.path.exists(full_image_path):
                    with open(full_image_path, 'rb') as img_file:
                        img_data = img_file.read()
                        img_base64 = base64.b64encode(img_data).decode()
                    popup_html = f"""
                    <div style=\"text-align: center;\">
                        <h4>🚧 Pothole Detection</h4>
                        <img src=\"data:image/jpeg;base64,{img_base64}\" style=\"width: 250px; height: auto; border-radius: 8px; margin: 10px 0;\">
                        <p><strong>Confidence:</strong> {confidence:.2%}</p>
                        <p><strong>Image:</strong> {image_path}</p>
                    </div>
                    """
                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_html, max_width=300),
                        icon=folium.Icon(
                            color='red',
                            icon='exclamation-triangle',
                            prefix='fa'
                        ),
                        tooltip=f"Pothole Detection ({confidence:.1%})"
                    ).add_to(m)
                elif os.path.exists(full_image_path):
                    # For markers not in current page, just show basic info without image
                    popup_html = f"""
                    <div style=\"text-align: center;\">
                        <h4>🚧 Pothole Detection</h4>
                        <p><strong>Confidence:</strong> {confidence:.2%}</p>
                        <p><strong>Image:</strong> {image_path}</p>
                        <p><em>Use sidebar to view image</em></p>
                    </div>
                    """
                    folium.Marker(
                        location=[lat, lon],
                        popup=folium.Popup(popup_html, max_width=300),
                        icon=folium.Icon(
                            color='red',
                            icon='exclamation-triangle',
                            prefix='fa'
                        ),
                        tooltip=f"Pothole Detection ({confidence:.1%})"
                    ).add_to(m)
                else:
                    folium.Marker(
                        location=[lat, lon],
                        popup=f"Pothole Detection<br>Confidence: {confidence:.2%}<br>Image: {image_path}<br><em>Image file not found</em>",
                        icon=folium.Icon(
                            color='orange',
                            icon='exclamation-triangle',
                            prefix='fa'
                        ),
                        tooltip=f"Pothole Detection ({confidence:.1%}) - No Image"
                    ).add_to(m)
            except Exception as e:
                continue

# Add vehicle markers to map if available
if st.session_state.vehicle_data is not None and layer_controls['vehicles']:
    vehicle_df = st.session_state.vehicle_data
    
    # Show progress for loading vehicle markers
    with st.spinner(f"Loading {len(vehicle_df)} vehicle markers on map..."):
        for idx, row in vehicle_df.iterrows():
            try:
                lat = row['latitude']
                lon = row['longitude']
                vehicle_type = row['vehicle_type']
                
                # Define colors and icons for different vehicle types
                vehicle_config = {
                    'car': {'color': 'blue', 'icon': 'car', 'tooltip': '🚗 Car'},
                    'truck': {'color': 'orange', 'icon': 'truck', 'tooltip': '🚛 Truck'},
                    'motorcycle': {'color': 'green', 'icon': 'motorcycle', 'tooltip': '🏍️ Motorcycle'}
                }
                
                config = vehicle_config.get(vehicle_type, {'color': 'gray', 'icon': 'question', 'tooltip': '❓ Unknown'})
                
                # Get total count for this vehicle type
                vehicle_counts = vehicle_df['vehicle_type'].value_counts()
                total_count = vehicle_counts.get(vehicle_type, 0)
                
                popup_html = f"""
                <div style=\"text-align: center;\">
                    <h4>{config['tooltip']}</h4>
                    <p><strong>Type:</strong> {vehicle_type.title()}</p>
                    <p><strong>Total Count:</strong> {total_count}</p>
                </div>
                """
                
                folium.Marker(
                    location=[lat, lon],
                    popup=folium.Popup(popup_html, max_width=250),
                    icon=folium.Icon(
                        color=config['color'],
                        icon=config['icon'],
                        prefix='fa'
                    ),
                    tooltip=config['tooltip']
                ).add_to(m)
            except Exception as e:
                continue

# Add legend for IRI values if IRI data is available
if st.session_state.iri_calculation_result and layer_controls['iri']:
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 220px; height: 180px; 
                background-color: white; border: 2px solid #333; border-radius: 8px; z-index:9999; 
                font-size:14px; padding: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
    <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 16px; text-align: center; border-bottom: 1px solid #ccc; padding-bottom: 5px;">IRI Quality Legend</p>
    <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: green; border-radius: 50%; margin-right: 8px;"></span> Good (≤3)</p>
    <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: yellow; border-radius: 50%; margin-right: 8px;"></span> Fair (3-5)</p>
    <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: orange; border-radius: 50%; margin-right: 8px;"></span> Poor (5-7)</p>
    <p style="margin: 5px 0;"><span style="display: inline-block; width: 12px; height: 12px; background-color: red; border-radius: 50%; margin-right: 8px;"></span> Bad (>7)</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

# Add legend for vehicle markers if available
if st.session_state.vehicle_data is not None and layer_controls['vehicles']:
    vehicle_legend_html = '''
    <div style="position: fixed; 
                top: 50px; right: 50px; width: 200px; height: 160px; 
                background-color: white; border: 2px solid #333; border-radius: 8px; z-index:9999; 
                font-size:14px; padding: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
    <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 16px; text-align: center; border-bottom: 1px solid #ccc; padding-bottom: 5px;">🚗 Vehicle Detections</p>
    <p style="margin: 5px 0;"><span style="display: inline-block; width: 16px; height: 16px; background-color: blue; border-radius: 50%; margin-right: 8px;"></span> 🚗 Car</p>
    <p style="margin: 5px 0;"><span style="display: inline-block; width: 16px; height: 16px; background-color: orange; border-radius: 50%; margin-right: 8px;"></span> 🚛 Truck</p>
    <p style="margin: 5px 0;"><span style="display: inline-block; width: 16px; height: 16px; background-color: green; border-radius: 50%; margin-right: 8px;"></span> 🏍️ Motorcycle</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(vehicle_legend_html))

# Add legend for pothole images if available
if st.session_state.pothole_images_data is not None and layer_controls['pothole_images']:
    pothole_legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 240px; height: 170px; 
                background-color: white; border: 2px solid #333; border-radius: 8px; z-index:9999; 
                font-size:14px; padding: 15px; box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
    <p style="margin: 0 0 10px 0; font-weight: bold; font-size: 16px; text-align: center; border-bottom: 1px solid #ccc; padding-bottom: 5px;">🚧 Pothole Detections</p>
    <p style="margin: 5px 0;"><span style="display: inline-block; width: 16px; height: 16px; background-color: red; border-radius: 50%; margin-right: 8px;"></span> Pothole with Image</p>
    <p style="margin: 5px 0;"><span style="display: inline-block; width: 16px; height: 16px; background-color: orange; border-radius: 50%; margin-right: 8px;"></span> Pothole (No Image)</p>
    <p style="margin: 5px 0; font-size: 12px; color: #666;">All markers shown on map</p>
    <p style="margin: 5px 0; font-size: 12px; color: #666;">Use sidebar to view images</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(pothole_legend_html))

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

