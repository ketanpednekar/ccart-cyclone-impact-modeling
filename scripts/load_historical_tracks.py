import numpy as np
from climada.hazard import TCTracks

def load_historical_tracks(
    basin="NI",
    year_range=(1980, 2020),
    provider="usa",
    min_wind=40,
    correct_pres=False,
    verbose=True
):
    """
    Load historical cyclone tracks using TCTracks.from_ibtracs_netcdf.
    Filters by basin, year range, and minimum wind speed.

    Parameters:
        basin (str): Basin code (e.g., "NI" for North Indian Ocean).
        year_range (tuple): Year range for filtering (start_year, end_year).
        provider (str): IBTrACS provider (e.g., "usa", "jtwc", "tokyo").
        min_wind (float): Minimum peak wind speed (knots).
        correct_pres (bool): Whether to exclude tracks with missing pressure data.
        verbose (bool): Whether to print summary info.

    Returns:
        List[xarray.Dataset]: Filtered cyclone tracks.
    """
    # Load tracks from IBTrACS NetCDF
    tc_tracks = TCTracks.from_ibtracs_netcdf(
        provider=provider,
        year_range=year_range,
        basin=basin,
        correct_pres=correct_pres
    )

    # Filter by peak wind
    filtered_tracks = []
    for track in tc_tracks.data:
        if track["max_sustained_wind"].max() >= min_wind:
            filtered_tracks.append(track)

    if verbose:
        print(f"✅ Loaded {len(filtered_tracks)} tracks from basin '{basin}' with wind ≥ {min_wind} kn")
        print(f"📦 Total tracks in raw archive: {tc_tracks.size}")
        print(f"📅 Year range: {year_range}")
        print(f"🌊 Basin: {basin}, Provider: {provider}")
        print(f"🌀 Example track name: {filtered_tracks[0].attrs.get('name', 'N/A')}")
        print(f"🧭 Example SID: {filtered_tracks[0].attrs.get('sid', 'N/A')}")

    return filtered_tracks
