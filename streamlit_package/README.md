# Streamlit Pothole Detection Package

This package contains all files needed for the Streamlit mapping app.

## Files:
- `data/pothole_detections.csv`: Detection data with GPS coordinates
- `images/`: Folder containing 0 pothole detection images
- `README.md`: This file

## Usage in Streamlit:
```python
import pandas as pd
df = pd.read_csv('data/pothole_detections.csv')
# Use latitude/longitude for mapping
# Use image_path to display images (prefix with 'images/')
```
