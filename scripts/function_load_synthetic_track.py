import numpy as np
import xarray as xr

def load_synthetic_bhola_track():
    """
    Create a synthetic Bhola (1970) track with windfield realism and pressure-gradient physics.
    Returns xarray-native track object compatible with CCART pipeline and CLIMADA.
    """

    # Define time steps (3-hour intervals)
    times = np.arange("2035-10-01T00", "2035-10-02T21", dtype="datetime64[3h]")[:15]

    # Define storm path (northward trajectory)
    lats = np.linspace(16.0, 23.0, len(times))
    lons = np.linspace(89.0, 90.5, len(times))

    # Define wind intensities (knots)
    max_sustained_wind = np.array([
        40, 45, 50, 60, 70, 85, 100, 120,
        135, 145, 140, 130, 115, 100, 85
    ])

    # Compute pressure fields (mb)
    central_pressure = 1000 - (max_sustained_wind * 0.5)
    environmental_pressure = np.full_like(max_sustained_wind, 1010.0)

    # Define radius of maximum wind (km) — float64 to avoid casting errors
    radius_max_wind = np.array([
        60, 55, 50, 45, 40, 35, 30, 25,
        20, 20, 25, 30, 35, 40, 45
    ], dtype=np.float64)

    # Define time step (hours)
    time_step = np.full_like(max_sustained_wind, 3.0)

    # Define basin (North Indian Ocean)
    basin = np.full(len(times), "NI")

    # Build xarray Dataset
    track = xr.Dataset(
        data_vars={
            "max_sustained_wind": (["time"], max_sustained_wind),
            "central_pressure": (["time"], central_pressure),
            "environmental_pressure": (["time"], environmental_pressure),
            "radius_max_wind": (["time"], radius_max_wind),
            "time_step": (["time"], time_step),
            "basin": (["time"], basin)
        },
        coords={
            "time": times,
            "lat": (["time"], lats),
            "lon": (["time"], lons)
        }
    )

    # Required metadata for CLIMADA windfield engine
    track["central_pressure"].attrs["long_name"] = "central_pressure"
    track["environmental_pressure"].attrs["long_name"] = "environmental_pressure"
    track["radius_max_wind"].attrs["long_name"] = "radius_max_wind"

    track.attrs["max_sustained_wind_unit"] = "kn"
    track.attrs["central_pressure_unit"] = "mb"
    track.attrs["environmental_pressure_unit"] = "mb"
    track.attrs["radius_max_wind_unit"] = "km"

    # Scenario metadata
    track.attrs["name"] = "Synthetic Bhola"
    track.attrs["agency"] = "CCART-AI"
    track.attrs["scenario"] = "+2°C warming"
    track.attrs["sid"] = "Synthetic_Bhola_2035"
    track.attrs["orig_event_flag"] = False
    track.attrs["category"] = 5

    return track
