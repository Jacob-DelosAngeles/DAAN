import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from utils.iri_calculator import IRICalculator
import io

# Set page config
st.set_page_config(
    layout = "wide",
    initial_sidebar_state = "expanded"
)

# Custom CSS for template
st.markdown("""
<style>

    h1{
        text-align: center;
    }

    .info-box{
        background-color : #F8F9FA;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #2E4057;
        margin: 1rem 0;
    }

    .section-header{
        font-size: 1.5rem;
        font-weight: bold;
        color: #2E4057;
        margin-top: 32px;
        margin-bottom: 1rem;
        border-bottom: 2px solid #2E4057;
        padding-bottom: 0.5rem;
        text-align: left;
    }

    .metric-container{
        background-color: #E8F4FD;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 0.5rem 0;
    }

    .stButton > button[kind="primary"]{
        background-color: #2E4057 !important;
        color: white;
        border: none;
        border-radius: 5 px;
        font-weight: bold;
        padding: 0.5rem 1rem;
    }

    st.Button > button[kind="primary"]{
        background-color: #1a2633;
        color:white;
    }

    /*  Overlay background */
    [data-testid="stSidebar"] {
        background-image: url("https://github.com/Jacob-DelosAngeles/IRI-system/blob/master/images/sidebar_background.jpg?raw=true");
        background-position: center;
        background-repeat: no-repeat;
    }

    [data-testid="stSidebar"] .css-1wvake5,
    [data-testid="stSidebar"] .css-16idsys,
    [data-testid="stSidebar"] .css-10trblm,
    [data-testid="stSidebar"] .css-1v0mbdj,
    [data-testid="stSidebar"] .css-1v3fvcr,
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span {
        color: white !important;
        font-weight: bold;
        font-size: 1.1rem;
    }

    [data-testid="stSidebar"] .st-emotion-cache-1rtdyuf {
        margin: 0px auto;
    }

    [data-testid="stSidebar"] .st-emotion-cache-2s0is {
        margin: 0px auto;
    }

    [data-testid="stSidebar"] svg {
    fill: white !important;
    }

    [data-testid="stNavSectionHeader"] {
        color: white;
        font-size: 28px;
        font-weight: bold;
        text-shadow: 
            -1px -1px 0 #000, 
            1px -1px 0 #000, 
            -1px 1px 0 #000, 
            1px 1px 0 #000;
    }

    [data-testid="stSidebarNavLink"] {
        margin-top: 20px;
        margin-bottom: 100px;
        background-color: black;
        border: 2px solid wheat;
    }

</style>

""", unsafe_allow_html = True)

st.markdown('<h1 class="main-header">📱 IRI Calculator</h1>',
unsafe_allow_html = True)

# Description
st.markdown("""
<div class="info-box">
    <h3>📊 Calculate International Roughness Index</h3>
    <p>Upload CSV sensor data exported from Physics Toolbos Sensor Suite
    to calculate the International Roughness Index (IRI) for your pavement section. This tool processes accelerometer data and applies 
    the RMS IRI calculation methodology.</p>
</div>
""", unsafe_allow_html = True)

# Instructions
st.markdown("<div class='section-header'>📋 Instructions </div>", unsafe_allow_html = True)

col1, col2 = st.columns([2,1])

with col1:
    st.markdown("""
    **Data Collection Setup:**
    1. Use Physics Toolbox Sensor Suite app on your smartphone
    2. Enable the **Linear Accelerometer**,  **Gyroscope**, and **GPS**
    3. Click "**+**" to record data
    4. Record Data while driving at consistent speed (50-80 km/hr)
    5. Export data as CSV format

    **File Requirements:**
    - CSV format with headers
    - Columns: time, ax, ay, az (acceleration data)
    - Maximum file size: 200 MB
    - Minimum recording duration: 30 seconds
    """, unsafe_allow_html = True)

with col2:
    st.markdown("""
    <div class="metric-container">
        <h4>📈 Expected Results</h4>
        <p><strong>IRI Values</strong> (m/km)</p>
        <p><strong>Quality Rating<strong></p>
        <p><strong>Visualization</strong></p>
        <p><strong>Statistics</strong></p>
    """, unsafe_allow_html = True)



# File upload section
st.markdown("<div class='section-header'>📂 Upload CSV File</div>",
unsafe_allow_html = True)

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=['csv'],
    help="Upload CSV sensor data exported from Physics Toolbox Sensor Suite",
    key = "csv_uploader"
)


# ----- Functions for Map Visualization -------

def plot_iri_map(df, iri_values, segments):
    latitudes = []
    longitudes = []
    qualities = []

    for iri, seg in zip(iri_values, segments):
        idx = seg['center_index']

        if 0 <= idx < len(df):
            lat = df.iloc[idx]['latitude']
            lon = df.iloc[idx]['longitude']
            latitudes.append(lat)
            longitudes.append(lon)

            if iri <= 3:
                qualities.append("Good")
            elif iri <= 5:
                qualities.append("Fair")
            elif iri <=7:
                qualities.append("Poor")
            else:
                qualities.append("Bad")
        else:
            continue
    
    map_df = pd.DataFrame({
        'Latitude': latitudes,
        'Longitude': longitudes,
        'IRI': iri_values[:len(latitudes)],
        'Quality': qualities
    })

    color_map = {
        "Good": "#28a745",
        "Fair": "#ffc107",
        "Poor": "#fd7e14",
        "Bad": "#dc3545"
    }

    fig = px.scatter_mapbox(
        map_df,
        lat = "Latitude",
        lon = "Longitude",
        color = "Quality",
        size = "IRI",
        size_max = 10,
        color_discrete_map = color_map,
        hover_name = "IRI",
        zoom = 14,
        height = 500
    )

    fig.update_layout(mapbox_style="carto-positron")
    fig.update_layout(margin={"r":0, "t":0, "l":0, "b":0}
    )

    st.markdown('<div class="section-header">🗺️ IRI Map Visualization</div>', unsafe_allow_html = True)
    st.plotly_chart(fig, use_container_width = True)

    


# Variables Initialization
if 'recalculate' not in st.session_state:
    st.session_state.recalculate = False 

# Initialization of segment length and threshold value
if 'segment_length' not in st.session_state:
    st.session_state.segment_length = 150
if 'threshold_value' not in st.session_state:
    st.session_state.threshold_value = 0.0

# Calculation Result Initialization
if 'calculation_result' not in st.session_state:
    st.session_state.calculation_result=None


if uploaded_file is not None:
    # Display file info
    st.success(f"✅ File Uploaded: {uploaded_file.name}")
    st.info(f"📊 File size: {uploaded_file.size / 1024 / 1024:.2f} MB")

    # Show processing status
    st.markdown('<div class="section-header">📊 Processing Status</div>', 
    unsafe_allow_html = True)

    st.info("""
    **File Analysis Complete:**
    
    Your CSV file has been successfully uploaded and is ready for processing.
    The IRI Calculation engine will analyze your acclerometer data using the 
    Root Mean Squared(RMS) model methodology to determine pavement roughness.

    **Processing Steps:**
    1. ✅ File validation and format verification
    2. ✅ Data cleaning and outlier removal
    3. ✅ Signal filtering and noise reduction
    4. ✅ Coordinate system alignment
    5. ✅ RMS model application
    6. ✅ IRI calculation and quality assessment
    """)
    
    # Calculate Button and algorithm
    if st.button("🧮 Caculate IRI", type="primary", use_container_width = True) or st.session_state.recalculate:
        with st.spinner("Processing accelerometer data and calculating IRI..."):
            import time
            time.sleep(2) # Simulate processing time

            # Include the Program for calculation
            iri_calc = IRICalculator()
            df = pd.read_csv(uploaded_file)
            df_processed, duration = iri_calc.preprocess_data(df)
            df_filtered, _ = iri_calc.filter_accelerometer_data(df_processed)
            vertical_accel = iri_calc.extract_vertical_acceleration(df_filtered)

            if df_processed is not None:
                
                # For recomputation of segment length and threshold value
                segment_length = st.session_state.segment_length
                threshold_value = st.session_state.threshold_value

                # For IRI Calculation
                iri_values, segments, sampling_rate, speed = iri_calc.calculate_iri_rms_method(df_processed, segment_length)

                mean_iri = np.mean(iri_values)

                # For Total Distance
                segment_centers = [s['distance_start'] + s['length']/2 for s in segments]

                st.session_state.calculation_result ={
                    'iri_values': iri_values,
                    'segments': segments,
                    'segment_centers': segment_centers,
                    'mean_iri': mean_iri,
                    'sampling_rate': sampling_rate,
                    'speed': speed,
                    'duration': duration,
                    'df': df,
                    'df_filtered': df_filtered,
                    'vertical_accel': vertical_accel,
                    'df_processed': df_processed
                }
                st.session_state.recalculate = False
            else:
                st.error("❌ Data preprocessing failed")

    if st.session_state.calculation_result:
        result = st.session_state.calculation_result
        iri_values = result['iri_values']
        segments = result['segments']
        segment_centers = result['segment_centers']
        mean_iri = result['mean_iri']
        sampling_rate =  result['sampling_rate']
        speed = result['speed']
        duration = result['duration']
        df = result['df']
        df_filtered = result['df_filtered']
        vertical_accel = result['vertical_accel']
        df_processed = result['df_processed']

        total_distance = segment_centers[-1] + (segments[-1]['length']/2)


        # Formatted Results
        st.markdown('<div class="section-header">🏆 IRI Calculation Results</div>',
        unsafe_allow_html = True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🛣️ IRI Value", f"{mean_iri:.2f}", help="International Roughness Index")
        with col2:
            if mean_iri <= 3:
                classification = 'Good'
            elif mean_iri <= 5:
                classification = 'Fair'
            elif mean_iri <= 7:
                classification = 'Poor'
            else:
                classification = 'Bad'
            st.metric("⭐ Road Quality", f"{classification}", help="Pavement quality assessment")
        with col3:
            st.metric("📊 Standard Deviation", f"{np.std(iri_values):.2f}", help="IRI spread")
        
        # Quality Assessment
        def get_sample_quality_rating(iri_value):
            if iri_value <= 3:
                return{
                    'rating': 'Good',
                    'description': 'Acceptable pavement condition',
                    'color': '#28a745',
                    'interpretation': """This pavement provides good ride quality
                    with acceptable smoothness. Vehicle operating costs are within
                    normal range and user comfort is satisfactory.""",
                    'recommendations': """Condition with routine maintenance activities.
                    Monitor condition annually and apply preventive treatments as needed to maintain
                    current service level."""
                }
            elif iri_value <=5:
                return{
                    'rating' : 'Fair',
                    'description': 'Moderate pavement roughness',
                    'color': '#ffc107',
                    'interpretation': """This pavement shows moderate roughness that begins
                    to affect ride quality. Some increase in vehicle operating costs and minor
                    user discomfort may be experienced.""",
                    'recommendations': """Plan for rehabilitation treatments within 3-5 years. Consider
                    surface treatments or minor structural improvements to prevent further deterioration."""
                }
            
            elif iri_value <= 7:
                return{
                    'rating': 'Poor',
                    'description': 'Significant pavement deterioration',
                    'color': '#fd7e14',
                    'interpretation': """This pavement has significant roughness that
                    notably impacts ride quality and increases vehicle operating costs. User
                    comfort is compromised  and maintenance costs are elevated.""",
                    'recommendations': """Prioritize major rehabilitation or reconstruction within 2-3 years.
                    Implement interim maintenance to prevent further rapid deterioration and safety issues."""
                }
            
            else:
                return{
                    'rating': 'Bad',
                    'description': 'Severe pavement distress',
                    'color': '#dc3545',
                    'interpretation': """This pavement exhibits severe roughness causing substantial user discomfort, high vehicle operating costs, 
                    and potential safety concerns. Structural integrity may be compromised.""",
                    'recommendations': """Immediate major rehabilitation or full reconstruction required. Consider emergency repairs if safety is compromised. Evaluate load restrictions
                    until permanent repairs are completed."""
                }

        
        quality = get_sample_quality_rating(mean_iri)

        st.markdown(f"""
        <div class='info-box' style="border-left-color: {quality['color']};">
            <h4>🎯 Quality Assessment</h4>
            <p><strong>Rating:</strong> {quality['rating']} ({quality['description']})</p>
            <p><strong>Interpretation:</strong> {quality['interpretation']}</p>
            <p><strong>Recommendations:</strong> {quality['recommendations']}</p>
        </div>
        """, unsafe_allow_html=True)


        # Statistical Summary
        st.markdown('<div class="section-header">📊 Statistical Summary</div>', unsafe_allow_html = True)

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Calculation Parameters:**")
            st.write(f"- Data Duration: {duration:.2f} seconds ")
            st.write(f"- Sampling Rate: {sampling_rate:.2f} Hz")
            st.write(f"- Speed Estimate: {(speed*3.6):.2f} km/h")
            st.write(f"- Distance Covered: {(total_distance/1000):.2f} km")
        
        with col2:
            st.markdown("**Data Quality Metrics:**")
            st.write(f"- Min IRI: {np.min(iri_values):.2f} m/km ")
            st.write(f"- Max IRI: {np.max(iri_values):.2f}  m/km")
            st.write(f"- Standard Deviation: {np.std(iri_values):.2f} m/km")
            st.write(f"- Road IRI: {mean_iri:.2f} m/km")


        # Plotting Results
        st.markdown('<div class="section-header">📈 IRI Data Visualization </div>', unsafe_allow_html = True)

        # Create Plotly Subplots
        fig = make_subplots(
            rows =3, cols = 1,
            shared_xaxes = False,
            vertical_spacing = 0.12,
            subplot_titles = (
                "Raw Accelerometer Data",
                "Filtered Vertical Acceleration",
                "International Roughness Index (IRI)"
            )
        )

        # Plot Raw Accelerometer Data
        fig.add_trace(go.Scattergl(x=df['time'], y=df['ax'], mode='lines', name='X-axis', line=dict(color='blue')), row=1, col=1)
        fig.add_trace(go.Scattergl(x=df['time'], y=df['ay'], mode='lines', name='Y-axis', line=dict(color='orange')), row=1, col=1)
        fig.add_trace(go.Scattergl(x=df['time'], y=df['az'], mode='lines', name='Z-axis', line=dict(color='green')), row=1, col=1)

        # Plot Filtered Vertical Acceleration
        fig.add_trace(go.Scattergl(x=df_filtered['time'], y=vertical_accel, mode='lines', name='Vertical Accel', line=dict(color = '#FFBF00')), row=2, col=1)


        # Plot IRI Values
        fig.add_trace(go.Scattergl(
            x=segment_centers, y=iri_values,
            mode = 'lines+markers', name='IRI', line=dict(color='red'),
            marker = dict(color='red')
        ), row=3, col=1)

        fig.add_trace(go.Scattergl(
            x=segment_centers, y=[st.session_state.threshold_value]*len(segment_centers), mode ='lines',
            name='Threshold', line=dict(color='black', dash='dash')
        ), row=3, col=1)

        # Layout Settings
        fig.update_layout(
            height = 1000,
            showlegend = True,
            plot_bgcolor= 'white',
            paper_bgcolor='white',
            font=dict(color='black', size=12),
            margin=dict(t=60, b=40, l=40, r=40),
        )

        # Adding Axes Titles
        fig.update_xaxes(title_text="Time (s)", row=1, col=1)
        fig.update_xaxes(title_text="Time (s)", row=2, col=1)
        fig.update_xaxes(title_text="Distance (m)", row=3, col=1)
        fig.update_yaxes(title_text="Acceleration (m/s²)", row=1, col=1)
        fig.update_yaxes(title_text="Vertical Accel(m/s²)", row=2, col=1)
        fig.update_yaxes(title_text="IRI (m/km)", row=3, col=1)
        
        # Title styling (force black instead of grey)
        for i in range(1,4):
            fig['layout']['annotations'][i-1]['font'] = dict(size=14, color='black')

        # Add black border using shapes
        fig.update_layout(
            shapes=[
                # Row 1 (top)
                dict(type='rect', xref='paper', yref='paper',
                x0=0, x1=1, y0=0.70, y1=1,
                line=dict(color="black", width=2)),

                # Row 2 (middle)
                dict(type='rect', xref="paper", yref="paper",
                x0=0, x1=1, y0=0.38, y1=0.62,
                line=dict(color="black", width=2)),

                # Row 3 (bottom)
                dict(type='rect', xref='paper', yref='paper',
                x0=0, x1=1, y0=0, y1=0.25,
                line=dict(color="black", width=2)),
            ]
        )

        # Showing the Plot
        st.plotly_chart(fig, use_container_width=True)



        # Map Visualization 
        plot_iri_map(df_processed, iri_values, segments)

        # Prepare DataFrame for download
        download_df = pd.DataFrame({
            "Distance": segment_centers,
            "IRI": iri_values
        })

        csv_buffer = io.StringIO()
        download_df.to_csv(csv_buffer, index=False)
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="⬇️ Download IRI vs Distance CSV",
            data=csv_data,
            file_name="iri_rms.csv",
            mime="text/csv"
        )


        # Addition of Advanced Settings
        st.markdown('<div class="section-header">⚙️ Advanced Settings</div>',
        unsafe_allow_html = True)

        # Getting the Inpput
        new_segment_length = st.number_input("Segment Length (m)", value=st.session_state.segment_length, step=10, min_value = 100)
        new_threshold_value = st.number_input("IRI Threshold (m/km)", value=st.session_state.threshold_value, step=0.1, min_value=0.0)

        # Recalculation button
        if st.button("🔁 Recalculate with Advanced Settings",  type="primary", use_container_width = True):
            st.session_state.segment_length = new_segment_length
            st.session_state.threshold_value = new_threshold_value
            st.session_state.recalculate = True
            st.rerun()

else:
    # Upload placeholder
    st.markdown("""
    <div style="border: 2px dashed #ccc; border-radius: 10px; padding: 2rem;
    text-align:center; margin: 2rem 0;">
        <h3>📁 Drag and Drop File Here</h3>
        <p>or use the file browser</p>
        <p><em>Limit 200MB per file  •  CSV format only</em></p>
    </div>
    """, unsafe_allow_html = True)
