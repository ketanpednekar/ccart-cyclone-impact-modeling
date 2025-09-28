# Imports
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
from scipy.sparse import find
from matplotlib.collections import LineCollection
import cartopy.crs as ccrs
import cartopy.feature as cfeature

from climada.hazard import TCTracks, TropCyclone, Centroids
from climada.entity import Exposures
from climada.entity.impact_funcs import ImpactFuncSet, ImpfTropCyclone
from climada.engine import ImpactCalc
from climada.util.api_client import Client

# Public functions for modular import
__all__ = [
    "load_storm_by_year", "filter_litpop_exposure", "generate_hazard",
    "assign_impact_function", "compute_impact", "extract_impact_gdf",
    "rebuild_geometry", "plot_tc_impact"
]

# ────────────────────────────────────────────────────────────────────────────────
# Storm Track Loading
# ────────────────────────────────────────────────────────────────────────────────

def load_storm_by_year(year=2020, basin="NI", name_filter="AMPHAN", provider="usa"):
    """
    Load a tropical cyclone track from IBTrACS by name, year, and basin.
    """
    tr_all = TCTracks.from_ibtracs_netcdf(provider=provider, year_range=(year, year), basin=basin)
    for track in tr_all.data:
        name = track.attrs.get('name', 'Unnamed')
        if name_filter.upper() in name.upper():
            return track
    raise ValueError(f"Storm '{name_filter}' not found in {year} {basin} basin.")

# ────────────────────────────────────────────────────────────────────────────────
# Exposure Preparation
# ────────────────────────────────────────────────────────────────────────────────

def filter_litpop_exposure(track, buffer_deg=3.0, countries=["IND", "BGD"]):
    """
    Filter LitPop exposure data within a spatial buffer around the track.
    Supports multi-country exposure merging.
    """
    lat_min = track['lat'].min().item() - buffer_deg
    lat_max = track['lat'].max().item() + buffer_deg
    lon_min = track['lon'].min().item() - buffer_deg
    lon_max = track['lon'].max().item() + buffer_deg
    client = Client()
    exposures = []
    for country in countries:
        exp = client.get_litpop(country=country)
        gdf = exp.gdf.copy()
        gdf['lat'] = gdf.geometry.y
        gdf['lon'] = gdf.geometry.x
        gdf_filtered = gdf[
            (gdf['lat'] >= lat_min) & (gdf['lat'] <= lat_max) &
            (gdf['lon'] >= lon_min) & (gdf['lon'] <= lon_max)
        ].copy()
        exposures.append(Exposures(gdf_filtered))
    exp_combined = Exposures.concat(exposures)
    exp_combined.gdf['lat'] = exp_combined.gdf.geometry.y
    exp_combined.gdf['lon'] = exp_combined.gdf.geometry.x
    return exp_combined

def rebuild_geometry(gdf):
    """
    Rebuild geometry column from lat/lon for plotting.
    """
    gdf['geometry'] = [Point(xy) for xy in zip(gdf['lon'], gdf['lat'])]
    return gpd.GeoDataFrame(gdf, crs="EPSG:4326")

# ────────────────────────────────────────────────────────────────────────────────
# Hazard & Impact Modeling
# ────────────────────────────────────────────────────────────────────────────────

def generate_hazard(track, exposure):
    """
    Generate TropCyclone hazard object using exposure centroids.
    """
    lat = exposure.gdf['lat'].values
    lon = exposure.gdf['lon'].values
    centroids = Centroids(lat=lat, lon=lon)
    track_container = TCTracks()
    track_container.data = [track]
    return TropCyclone.from_tracks(track_container, centroids=centroids)

def assign_impact_function(exposure):
    """
    Assign default impact function (Emanuel USA) to exposure.
    """
    impf = ImpfTropCyclone.from_emanuel_usa()
    impf_set = ImpactFuncSet([impf])
    haz_type = impf_set.get_hazard_types()[0]
    haz_id = impf_set.get_ids()[haz_type][0]
    exposure.gdf["impf_" + haz_type] = haz_id
    exposure.impact_funcs = impf_set
    return impf_set

def compute_impact(exposure, impf_set, hazard):
    """
    Compute impact using CLIMADA's ImpactCalc engine.
    """
    return ImpactCalc(exposure, impf_set, hazard).impact()

def extract_impact_gdf(impact, threshold=1e6):
    """
    Extract high-impact points from impact matrix as a GeoDataFrame.
    """
    row, col, val = find(impact.imp_mat)
    lat = impact.coord_exp[:, 0][col]
    lon = impact.coord_exp[:, 1][col]
    gdf = gpd.GeoDataFrame({
        'impact_usd': val,
        'latitude': lat,
        'longitude': lon
    }, geometry=[Point(xy) for xy in zip(lon, lat)], crs="EPSG:4326")
    return gdf[gdf['impact_usd'] > threshold]

# ────────────────────────────────────────────────────────────────────────────────
# Visualization
# ────────────────────────────────────────────────────────────────────────────────

def plot_tc_impact(track, gdf_litpop, gdf_impact, title="TC Impact",
                   wind_var="max_sustained_wind", zoom_buffer=2.0,
                   save_fig=False, verbose=True, save_path=None):
    """
    Plot cyclone impact map with wind-gradient track and exposure points.
    Saves PNG if save_fig=True and save_path is provided.
    """
    if wind_var not in track:
        raise KeyError(f"'{wind_var}' not found in track dataset. Available keys: {list(track.keys())}")
    if gdf_impact.empty:
        print("⚠️ No impact points above threshold. Try lowering the threshold or expanding the buffer.")
        return

    # Prepare track segments
    track_lats = track['lat'].values
    track_lons = track['lon'].values
    track_wind = track[wind_var].values
    points = np.array([track_lons, track_lats]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    lc = LineCollection(
        segments,
        cmap='plasma',
        norm=plt.Normalize(track_wind.min(), track_wind.max()),
        linewidth=2.5,
        array=track_wind,
        transform=ccrs.PlateCarree()
    )

    # Plot setup
    fig, ax = plt.subplots(figsize=(10, 8), subplot_kw={'projection': ccrs.PlateCarree()})
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linewidth=0.3)
    gdf_litpop.plot(ax=ax, color='lightblue', markersize=1.5, alpha=0.4,
                    label='LitPop Exposure', transform=ccrs.PlateCarree())
    gdf_impact.plot(ax=ax, column='impact_usd', cmap='plasma', markersize=6,
                    legend=True, legend_kwds={'label': "Impact (USD)", 'shrink': 0.6},
                    transform=ccrs.PlateCarree())
    ax.add_collection(lc)
    cbar = plt.colorbar(lc, ax=ax, orientation='vertical', shrink=0.6, pad=0.02)
    cbar.set_label("Wind Speed (knots)")
    ax.set_extent([
        gdf_impact['longitude'].min() - zoom_buffer,
        gdf_impact['longitude'].max() + zoom_buffer,
        gdf_impact['latitude'].min() - zoom_buffer,
        gdf_impact['latitude'].max() + zoom_buffer
    ], crs=ccrs.PlateCarree())
    ax.set_title(title, fontsize=14)
    ax.legend(loc='lower left')
    plt.tight_layout()

    # Save figure
    if save_fig:
        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches='tight')
        else:
            fig.savefig(f"{title.replace(' ', '_')}.png", dpi=300)

    plt.show()

    if verbose:
        print(f"\n💥 Total impact: ${gdf_impact['impact_usd'].sum():,.0f}")
        print(f"Plotted points (> $1M): {len(gdf_impact)}")
