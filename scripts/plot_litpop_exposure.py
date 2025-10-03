import os
import geopandas as gpd
import matplotlib.pyplot as plt
from climada.entity.exposures.litpop import LitPop

def plot_litpop_exposure(countries,
                          exposure_mode="population",
                          res_arcsec=120,
                          reference_year=2020,
                          fin_mode="pc",
                          data_dir=None,
                          boundary_path=None,
                          asset_thresh=1e6,
                          plot_modes=["scatter", "raster"],
                          save_plots=True,
                          output_dir="outputs"):
    """
    Load and plot LitPop exposure for given countries with optional boundary overlay.
    """

    # === Load Exposure ===
    if exposure_mode == "population":
        exp = LitPop.from_population(countries=countries,
                                     res_arcsec=res_arcsec,
                                     reference_year=reference_year,
                                     data_dir=data_dir)
    elif exposure_mode == "nightlight":
        exp = LitPop.from_nightlight_intensity(countries=countries,
                                               res_arcsec=res_arcsec)
    elif exposure_mode == "default":
        exp = LitPop.from_countries(countries=countries,
                                    res_arcsec=res_arcsec,
                                    reference_year=reference_year,
                                    fin_mode=fin_mode)
    else:
        raise ValueError(f"Unknown exposure_mode: {exposure_mode}")

    # === Filter by Asset Value ===
    # === Filter by Asset Value ===
    #filtered_gdf = exp.gdf[exp.gdf["value"] > asset_thresh]
    #exp = LitPop()
    #exp.gdf = filtered_gdf

    # === Load Boundary ===
    boundary_gdf = None
    if boundary_path:
        try:
            boundary_gdf = gpd.read_file(boundary_path).to_crs("EPSG:4326")
            boundary_gdf = boundary_gdf[boundary_gdf['ADMIN'].isin(countries)]
        except Exception as e:
            print(f"⚠️ Failed to load boundary: {e}")

    # === Plot Modes ===
    os.makedirs(output_dir, exist_ok=True)
    for mode in plot_modes:
        title = f"LitPop Exposure – {', '.join(countries)} – {mode.title()} Mode"

        if mode == "scatter":
            ax = exp.plot_scatter(title=title)
        elif mode == "raster":
            ax = exp.plot_raster()
            ax.set_title(title)  # ✅ valid

        else:
            print(f"⚠️ Unknown plot mode: {mode}")
            continue

        # Overlay boundary
        if boundary_gdf is not None and not boundary_gdf.empty:
            boundary_gdf.plot(ax=ax, edgecolor="black", linewidth=0.5)

        # Save plot
        if save_plots:
            fig = ax.get_figure()
            filename = f"litpop_{'_'.join(countries)}_{mode}.png".replace(" ", "_")
            fig.savefig(os.path.join(output_dir, filename), dpi=300)
            print(f"✅ Saved: {filename}")
