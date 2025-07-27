import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

# Page configuration
st.set_page_config(
    page_title="Pothole Detection Map",
    page_icon="",
    layout="wide"
)

# Title
st.title("Road Distress Detection Map")
st.markdown("Interactive map showing detected potholes with GPS coordinates")

# Load data
@st.cache_data
def load_data():
    csv_path = os.path.join("data", "pothole_detections.csv")
    return pd.read_csv(csv_path)

try:
    df = load_data()
    st.success(f"Loaded {len(df)} pothole detections")
    
    # Display basic statistics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Detections", len(df))
    with col2:
        st.metric("Average Confidence", f"{df['confidence_score'].mean():.2f}")
    with col3:
        st.metric("Highest Confidence", f"{df['confidence_score'].max():.2f}")
    with col4:
        st.metric("Unique Images", df['image_path'].nunique())
    
    # Create map
    st.subheader("Interactive Map")
    
    # Calculate map center
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    # Create Folium map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=15,
        tiles="OpenStreetMap"
    )
    
    # Add markers for each detection
    for idx, row in df.iterrows():
        # Create popup content
        popup_html = f"""
        <div style="width: 200px;">
            <h4>Pothole #{idx+1}</h4>
            <p><strong>Confidence:</strong> {row['confidence_score']:.2f}</p>
            <p><strong>Timestamp:</strong> {row['timestamp']}</p>
            <p><strong>Coordinates:</strong> {row['latitude']:.6f}, {row['longitude']:.6f}</p>
        </div>
        """
        
        # Add marker
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"Pothole #{idx+1} (Confidence: {row['confidence_score']:.2f})",
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # Display map
    st_folium(m, width=800, height=600)
    
    # Display data table
    st.subheader("Detection Data")
    st.dataframe(df[['latitude', 'longitude', 'confidence_score', 'timestamp']].head(10))
    
    # Confidence filter
    st.subheader("Filter by Confidence")
    min_confidence = st.slider(
        "Minimum Confidence Score",
        min_value=float(df['confidence_score'].min()),
        max_value=float(df['confidence_score'].max()),
        value=float(df['confidence_score'].min()),
        step=0.1
    )
    
    filtered_df = df[df['confidence_score'] >= min_confidence]
    st.write(f"Showing {len(filtered_df)} detections with confidence >= {min_confidence}")
    
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Make sure the package folder is in the same directory as this Streamlit app")
