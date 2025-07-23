# 🚧 Project DAAN  
**Digital Analytics for Asset-based Navigation of Roads**

Project DAAN is a Streamlit-based web application designed for visualizing and analyzing road condition data using AI-powered models. It integrates multiple data sources — including smartphone-based IRI, object detection (YOLOv8), and surface defect classification (CNN) — to create an interactive map for assessing and monitoring road assets.


## 🚀 Demo App

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://project-daan.streamlit.app/)


## 📂 Features

- 📍 **Interactive Map with Layered Data**
  - View pothole locations, pavement types, and vehicle counts with icon-based markers
  - Image popups for potholes detected by CNN
- 📈 **IRI Computation and Visualization**
  - Upload accelerometer data to compute IRI (International Roughness Index)
  - Classify road quality based on computed IRI
- 🎯 **AI-Powered Analysis**
  - YOLOv8 for vehicle detection and traffic volume estimation
  - CNN for classifying road surface defects (e.g., potholes, cracks)
- 🗺️ **Custom Visualization**
  - Dark gray for flexible pavement, white for rigid pavement
  - Satellite and terrain map layers supported via Folium

## 📤 Data Workflow

1. Upload road videos and accelerometer logs
2. Models detect vehicles and surface defects
3. GPS-tagged outputs (IRI, potholes, traffic counts) are visualized on a single interactive map

---

## 🛠️ Tech Stack

- **Frontend:** Streamlit + Folium + GeoPandas
- **Backend:** Python (Pandas, NumPy, OpenCV, YOLOv8, TensorFlow/Keras)
- **Map Layers:** Satellite, terrain, street (via Leaflet tiles)
- **Other Tools:** GitHub Codespaces, Google Colab (optional model training)

---
