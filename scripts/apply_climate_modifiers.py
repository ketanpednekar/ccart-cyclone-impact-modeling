def apply_climate_modifiers(track, wind_boost=1.15, rmw_shrink=0.85):
    """
    Apply climate change modifiers to a cyclone track.

    Parameters:
        track (xarray.Dataset): Original track.
        wind_boost (float): Multiplier for max sustained wind.
        rmw_shrink (float): Multiplier for radius of max wind.

    Returns:
        xarray.Dataset: Modified synthetic track.
    """
    modified = track.copy(deep=True)

    # Apply wind boost
    modified["max_sustained_wind"] *= wind_boost

    # Apply RMW shrinkage if available
    if "radius_max_wind" in modified:
        modified["radius_max_wind"] *= rmw_shrink

    # Adjust central pressure (simple parametric logic)
    if "central_pressure" in modified:
        modified["central_pressure"] = 1000 - (modified["max_sustained_wind"] * 0.5)

    # Tag metadata
    modified.attrs["sid"] = f"SYNTH_{track.attrs.get('sid', 'N/A')}_WARMED"
    modified.attrs["scenario"] = f"Wind x{wind_boost}, RMW x{rmw_shrink}"
    modified.attrs["orig_event_flag"] = False
    modified.attrs["category"] = 5  # Optional override

    return modified
