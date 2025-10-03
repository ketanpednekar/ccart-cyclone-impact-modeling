# CCART Cyclone Impact Modeling – Amphan SSP Diagnostics

This repository contains a modular pipeline for simulating tropical cyclone impacts under climate change scenarios using CCART (Climate Change Assessment and Risk Tool). The current focus is on Cyclone Amphan (2035) under SSP2-4.5, SSP3-7.0, and SSP5-8.5.

---

## Features

- Scenario-wise impact diagnostics using synthetic cyclone tracks  
- Climate modifiers applied to wind speed and radius of maximum wind (RMW)  
- Modular pipeline with reproducible outputs  
- GeoJSON exports for exposure, impact, and track  
- Inline visual diagnostics with scatter-mode overlays  

---

## Folder Structure

- `scripts/` → Core pipeline modules  
- `notebooks/` → Execution notebooks (e.g., `execute_tropical_cyclones.ipynb`)  
- `outputs/` → GeoJSONs and diagnostic maps  

---

## How to Run

1. Clone the repo  
2. Install dependencies (`geopandas`, `xarray`, etc.)  
3. Run `execute_tropical_cyclones.ipynb`  
4. Outputs will be saved in the `outputs/` folder with scenario tags  

---

## Sample Output

- Total impact (SSP2-4.5): $2.35B  
- Zones > $1M: 264  
- GeoJSONs: `impact_ssp2-45.geojson`, `track_ssp2-45.geojson`, `exposure_ssp2-45.geojson`  

---

## 🌪️ About CCART

CCART Cyclone Impact Modeling is a modular pipeline for diagnosing tropical cyclone impacts using geospatial overlays, hazard metadata, and census-informed exposure. Built for reproducibility, scenario toggling, and scientific clarity.

---

## 🤝 Collaborate

We’re looking to connect with:  
- Climate modelers  
- Disaster risk analysts  
- Geospatial scientists  
- Scenario simulation enthusiasts  

If you're exploring multi-hazard diagnostics, synthetic cyclone generation, or census-enhanced modeling — we’d love to hear from you.

---

## 📣 Acknowledgments

Built using CLIMADA, Python, and supported by Microsoft Copilot.

---

## License

This project is licensed under the MIT License with attribution. See the [LICENSE](./LICENSE) file for details.

© 2025 CCART GHG Consulting LLP. All rights reserved.
