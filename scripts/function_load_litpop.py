import matplotlib.pyplot as plt
import geopandas as gpd
import numpy as np
from climada.util.api_client import Client
from climada.entity import Exposures, LitPop

# High-res Natural Earth boundary path
NE10_PATH = r"C:\CMIP data\cmip6\Climada\Country Shape Files\ne_10m_admin_0_countries\ne_10m_admin_0_countries.shp"

__all__ = ["get_litpop_exposure", "load_boundary", "plot_litpop_exposure"]

# ─────────────────────────────────────────────────────────────
# Load LitPop Exposure (Multi-country Compatible)
# ─────────────────────────────────────────────────────────────
def get_litpop_exposure(countries, buffer_bounds=None):
    """
    Download LitPop exposure for one or more countries.
    Returns a concatenated Exposures object with normalized .gdf columns.
    """
    client = Client()
    exposures = []

    for country_name in countries:
        print(f"🌍 Downloading LitPop for: {country_name}")
        exposure = client.get_litpop(country=country_name)  # ✅ Removed res_km
        gdf = exposure.gdf.copy()
        gdf = gdf.rename(columns={"lon": "longitude", "lat": "latitude"})
        gdf = gdf.set_crs("EPSG:4326", allow_override=True)

        if buffer_bounds:
            lon_min, lat_min, lon_max, lat_max = buffer_bounds
            gdf = gdf.cx[lon_min:lon_max, lat_min:lat_max]
            print(f"✅ {country_name} exposure clipped to bounds: {buffer_bounds}")

        exposures.append(Exposures(gdf))

    if not exposures:
        raise ValueError("No exposure data downloaded.")

    combined = exposures[0]
    for exp in exposures[1:]:
        combined = Exposures.concat([combined, exp])

    return combined

# ─────────────────────────────────────────────────────────────
# Load Country Boundary
# ─────────────────────────────────────────────────────────────
def load_boundary(country_name, ne10_path=NE10_PATH):
    """
    Load high-resolution country boundary from Natural Earth 10m shapefile.
    Filters to mainland USA if needed.
    """
    try:
        boundary = gpd.read_file(ne10_path).to_crs(epsg=4326)
        boundary = boundary[boundary['ADMIN'] == country_name]

        if country_name == 'United States of America':
            boundary = boundary.cx[-130:-60, 20:55]

        return boundary
    except Exception as e:
        print(f"⚠️ Boundary loading failed: {e}")
        return None

# ─────────────────────────────────────────────────────────────
# Plot LitPop Exposure with Optional Impact Overlay
# ─────────────────────────────────────────────────────────────
def plot_litpop_exposure(country_name, impact_obj=None, impact_column='imp',
                         save_fig=False, save_path=None):
    """
    Plot LitPop exposure as a scatter-style heatmap with optional impact overlay.
    Returns the GeoDataFrame for downstream use.
    """
    assets = get_litpop_exposure([country_name])
    gdf = assets.gdf.copy()
    gdf['log_value'] = np.log10(gdf['value'] + 1)

    # Overlay impact if available
    if impact_obj is not None and hasattr(impact_obj, 'gdf'):
        if impact_column in impact_obj.gdf.columns:
            gdf[impact_column] = impact_obj.gdf[impact_column].values
        else:
            print(f"⚠️ Impact column '{impact_column}' not found.")
            impact_obj = None

    # Load boundary
    boundary = load_boundary(country_name)

    # Create plot
    fig, ax = plt.subplots(figsize=(10, 8))
    if boundary is not None and not boundary.empty:
        boundary.boundary.plot(ax=ax, edgecolor='black', linewidth=1)

    sc = ax.scatter(
        gdf['longitude'], gdf['latitude'],
        c=gdf['log_value'], cmap='plasma',
        s=10, alpha=0.6
    )
    plt.colorbar(sc, ax=ax, label='log₁₀ exposure')

    # Optional impact overlay
    if impact_obj is not None and impact_column in gdf.columns:
        ax.scatter(
            gdf['longitude'], gdf['latitude'],
            c=gdf[impact_column], cmap='Reds',
            s=12, alpha=0.5
        )
        ax.set_title(f'LitPop Exposure + Impact – {country_name}', fontsize=12, fontweight='bold')
    else:
        ax.set_title(f'LitPop Exposure – {country_name} (log₁₀ scale)', fontsize=12, fontweight='bold')

    ax.set_facecolor('white')
    ax.tick_params(axis='both', labelsize=8)
    ax.annotate('Exposure base with optional impact overlay',
                xy=(0.5, -0.1), xycoords='axes fraction',
                ha='center', fontsize=9)

    plt.tight_layout()

    if save_fig:
        fallback_name = f"{country_name}_litpop_exposure.png"
        fig.savefig(save_path or fallback_name, dpi=300, bbox_inches='tight')
        print(f"✅ Exposure figure saved to: {save_path or fallback_name}")

    plt.show()
    return gdf
