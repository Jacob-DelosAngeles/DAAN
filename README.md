# Project DAAN Express

Digital Analytics for Asset-based Navigation of Roads

## Overview

Project DAAN Express is a comprehensive road analytics platform that integrates IRI (International Roughness Index) calculation, vehicle detection, and pothole detection for road quality assessment.

## Features

### 🧮 IRI Calculator (New!)
- **Real-time IRI Calculation**: Upload sensor data from Physics Toolbox Sensor Suite to calculate road roughness
- **Quality Assessment**: Automatic road quality classification (Good, Fair, Poor, Bad)
- **Interactive Visualization**: Plot IRI values on map with color-coded quality indicators
- **Detailed Analysis**: Comprehensive quality assessment with recommendations

### 🗺️ Interactive Map
- Multiple map styles (OpenStreetMap, Satellite, 3D Terrain, Dark Mode)
- Layer controls for IRI values, vehicle detection, and pothole detection
- Real-time data visualization

### 📊 Data Integration
- Support for multiple data formats
- Vehicle detection using YOLOv8
- Pothole detection using CNN
- IRI calculation using RMS methodology

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
streamlit run streamlit_app.py
```

## Usage

### IRI Calculator
1. **Upload Sensor Data**: Use the "Upload IRI Sensor Data CSV" option in the sidebar
2. **Data Format**: CSV with columns: `time`, `ax`, `ay`, `az` (from Physics Toolbox Sensor Suite)
3. **Set Parameters**: Adjust segment length (default: 150m)
4. **Calculate**: Click "Calculate IRI" to process the data
5. **View Results**: Check the sidebar for IRI value, road quality, and assessment
6. **Map Visualization**: IRI values are automatically plotted on the map with color coding

### Data Upload
- **IRI Data**: CSV with `lat`, `lon`, `iri_score` columns
- **Vehicle Data**: CSV with `lat`, `lon`, `vehicle_type` columns  
- **Pothole Data**: CSV with `lat`, `lon`, `image_path` columns

## Data Collection Setup

### For IRI Calculation:
1. Use Physics Toolbox Sensor Suite app on your smartphone
2. Enable Linear Accelerometer, Gyroscope, and GPS
3. Record data while driving at consistent speed (50-80 km/hr)
4. Export as CSV format

## File Structure

```
DAAN/
├── streamlit_app.py          # Main application
├── calculator.py             # Standalone IRI calculator
├── utils/
│   └── iri_calculator.py     # IRI calculation engine
├── requirements.txt          # Dependencies
└── README.md                # This file
```

## Dependencies

- streamlit>=1.33.0
- pandas>=2.2.0
- numpy>=1.24.0
- folium>=0.15.0
- geopandas>=0.14.0
- streamlit-folium>=0.14.0
- matplotlib>=3.7.0
- pillow>=10.0.0
- scipy>=1.11.0
- plotly>=5.17.0

## Road Quality Classification

- **Good (≤3)**: Acceptable pavement condition
- **Fair (3-5)**: Moderate pavement roughness  
- **Poor (5-7)**: Significant pavement deterioration
- **Bad (>7)**: Severe pavement distress
