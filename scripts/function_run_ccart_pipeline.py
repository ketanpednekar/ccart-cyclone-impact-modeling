# ─────────────────────────────────────────────────────────────
# CCART Pipeline Orchestration
# ─────────────────────────────────────────────────────────────
import geopandas as gpd
import os
import traceback
from shapely.geometry import Point

# Modular imports
from function_load_tc_tracks import (
    load_storm_by_year,
    get_track_bounds,
    generate_hazard,
    assign_impact_function,
    compute_impact,
    extract_impact_gdf
)
from function_load_litpop import get_litpop_exposure
from function_plot_diagnostics import plot_tc_impact
from function_load_boundary import load_boundary_overlay

# ─────────────────────────────────────────────────────────────
# Run CCART Diagnostics Pipeline
# ─────────────────────────────────────────────────────────────
def run_ccart_pipeline(name, year, basin, countries,
                       threshold=1e6, buffer_deg=3.0,
                       wind_var="max_sustained_wind",
                       save_fig=True,
                       boundary_path=None,track_override=None):
    """
    Run CCART diagnostics for a given tropical cyclone using scatter-style diagnostics.
    Loads xarray-native storm track, computes hazard and impact, and plots diagnostics.
    Returns exposure, impact, and storm track GeoDataFrames.
    """
    try:
        # Setup output path
        output_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "outputs"))
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, f"{name.lower()}_impact_map.png")

        print(f"\n🌀 Running diagnostics for: {name} ({year}, {basin})")

        # Load storm track
        track = track_override or load_storm_by_year(year=year, basin=basin, name_filter=name)
        if not all(coord in track.coords for coord in ["lon", "lat"]):
            raise KeyError("Track data missing 'lon' or 'lat' coordinates.")

        # Load exposure
        bounds = get_track_bounds(track, buffer_deg=buffer_deg)
        exposure = get_litpop_exposure(countries, buffer_bounds=bounds)
        print("✅ Exposure loaded with", len(exposure.gdf), "points.")

        # Generate hazard and compute impact
        hazard = generate_hazard(track, buffer_deg=buffer_deg)
        impf_set, exposure = assign_impact_function(exposure)
        print("✅ Impact function assigned.")
        impact = compute_impact(exposure, impf_set, hazard)
        gdf_impact = extract_impact_gdf(impact, threshold=threshold)

        if gdf_impact.empty:
            print("⚠️ No impact zones above threshold. Skipping plot and export.")
            return exposure.gdf, gdf_impact, None

        print("✅ Impact extracted with", len(gdf_impact), "zones above threshold.")

        # Log total impact
        if "total_impact_usd" in gdf_impact.attrs:
            print(f"📊 Total impact (from metadata): ${gdf_impact.attrs['total_impact_usd']:,.0f}")

        # Optional boundary overlay
        boundary_gdf = None
        if boundary_path:
            impact_pts = [Point(xy) for xy in zip(gdf_impact['longitude'], gdf_impact['latitude'])]
            boundary_gdf = load_boundary_overlay(boundary_path, countries=countries, clip_points=impact_pts)
            print("✅ Boundary GDF loaded:", type(boundary_gdf))

        # Plot diagnostics
        plot_tc_impact(track, exposure.gdf, gdf_impact,
                       title=f"{name.title()} – Impact, Exposure & Wind-Gradient Track",
                       wind_var=wind_var,
                       save_fig=save_fig,
                       save_path=save_path,
                       boundary_gdf=boundary_gdf)

        # Export storm track
        if len(track['lon']) == 0 or len(track['lat']) == 0:
            print("⚠️ Storm track is empty. Skipping track export.")
            gdf_track = None
        else:
            gdf_track = gpd.GeoDataFrame({
                "lon": track['lon'].values,
                "lat": track['lat'].values
            }, geometry=[Point(xy) for xy in zip(track['lon'].values, track['lat'].values)], crs="EPSG:4326")
            track_path = os.path.join(output_dir, f"{name.lower()}_track.geojson")
            gdf_track.to_file(track_path, driver="GeoJSON")
            print(f"✅ Storm track exported to: {track_path}")

        # Export exposure and impact
        exposure_path = os.path.join(output_dir, f"{name.lower()}_exposure.geojson")
        impact_path = os.path.join(output_dir, f"{name.lower()}_impact.geojson")
        exposure.gdf.to_file(exposure_path, driver="GeoJSON")
        gdf_impact.to_file(impact_path, driver="GeoJSON")
        print(f"✅ Exposure exported to: {exposure_path}")
        print(f"✅ Impact exported to: {impact_path}")

        return exposure.gdf, gdf_impact, gdf_track, track

    except Exception as e:
        print(f"⚠️ Error running pipeline for {name}: {e}")
        traceback.print_exc()
        return None
