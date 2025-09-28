## 📦 Getting Started

Clone the repository and install dependencies:

```bash
git clone https://github.com/ketanpednekar/ccart-cyclone-impact-modeling.git
cd ccart-cyclone-impact-modeling
pip install -r requirements.txt
```
```python
# Run a Cyclone Diagnostic
from scripts.function_run_ccart_pipeline import run_ccart_pipeline

# Example: Cyclone Amphan (2020), North Indian Ocean, affecting India and Bangladesh
run_ccart_pipeline("Amphan", 2020, "NI", ["IND", "BGD"])
```
🌪️ About CCART
CCART Cyclone Impact Modeling is a modular pipeline for diagnosing tropical cyclone impacts using geospatial overlays, hazard metadata, and census-informed exposure. Built for reproducibility, scenario toggling, and scientific clarity.

🤝 Collaborate

We’re looking to connect with:

Climate modelers

Disaster risk analysts

Geospatial scientists

Scenario simulation enthusiasts

If you're exploring multi-hazard diagnostics, synthetic cyclone generation, or census-enhanced modeling — we’d love to hear from you.

📣 Acknowledgments

Built using CLIMADA, Python, and supported by Microsoft Copilot.

## License
This project is licensed under the MIT License with attribution. See the [LICENSE](./LICENSE) file for details.

© 2025 CCART GHG Consulting LLP. All rights reserved.
