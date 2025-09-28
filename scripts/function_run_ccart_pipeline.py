import os
from function_load_tc_tracks import (
    load_storm_by_year,
    filter_litpop_exposure,
    generate_hazard,
    assign_impact_function,
    compute_impact,
    extract_impact_gdf,
    plot_tc_impact,
    rebuild_geometry
)

def run_ccart_pipeline(name, year, basin, countries,
                       threshold=1e6, buffer_deg=3.0,
                       wind_var="max_sustained_wind",
                       zoom_buffer=2.0, save_fig=True, verbose=True):
    """
    Run CCART diagnostics for a given tropical cyclone.
    """
    try:
        # Ensure outputs folder exists
        output_dir = os.path.abspath(os.path.join(os.getcwd(), "..", "outputs"))
        os.makedirs(output_dir, exist_ok=True)

        # Define save path for PNG
        save_path = os.path.join(output_dir, f"{name.lower()}_impact_map.png")

        # Load and process
        track = load_storm_by_year(year=year, basin=basin, name_filter=name)
        exp_filtered = filter_litpop_exposure(track, buffer_deg=buffer_deg, countries=countries)
        hazard = generate_hazard(track, exp_filtered)
        impf_set = assign_impact_function(exp_filtered)
        impact = compute_impact(exp_filtered, impf_set, hazard)
        gdf_impact = extract_impact_gdf(impact, threshold=threshold)
        gdf_litpop = rebuild_geometry(exp_filtered.gdf.copy())

        # Plot and save
        plot_tc_impact(track, gdf_litpop, gdf_impact,
                       title=f"{name.title()} – Impact, Exposure & Wind-Gradient Track",
                       wind_var=wind_var,
                       zoom_buffer=zoom_buffer,
                       save_fig=save_fig,
                       verbose=verbose,
                       save_path=save_path)

    except Exception as e:
        print(f"⚠️ Error running pipeline for {name}: {e}")
