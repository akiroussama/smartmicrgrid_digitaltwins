---
title: MH-U-CBF Digital Twin
emoji: 🏭
colorFrom: blue
colorTo: cyan
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: true
license: mit
---

# MH-U-CBF Digital Twin

**Real-time Microgrid Visualization with Safety-Certified Control**

## Features

- Real-time digital twin visualization
- U-CBF (Uncertainty-aware Control Barrier Functions) safety monitoring
- Animated energy flows with CSS animations
- Multiple simulation scenarios (Normal, Heatwave, Cloud Cover, Cyber Attack)
- Live metrics and charts

## Quick Deploy

### Streamlit Cloud
1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Deploy from `digitalTwinApp/app.py`

### Hugging Face Spaces
1. Create a new Space with Streamlit SDK
2. Upload this folder
3. Done!

### Local Run
```bash
cd digitalTwinApp
pip install -r requirements.txt
streamlit run app.py
```

## Author

**Oussama AKIR**
PhD Candidate, Sup'Com
University of Carthage, Tunisia

## Thesis

*MH-U-CBF: Multi-Horizon Uncertainty-Aware Control Barrier Functions for Safe Reinforcement Learning*
