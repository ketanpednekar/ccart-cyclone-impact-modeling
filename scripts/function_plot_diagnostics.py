# ─────────────────────────────────────────────────────────────
# Visualization Module for CCART Diagnostics
# ─────────────────────────────────────────────────────────────

# ─────────────────────────────────────────────────────────────
# Imports
# ─────────────────────────────────────────────────────────────
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import geopandas as gpd
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from shapely.geometry import MultiPoint
from matplotlib.collections import LineCollection

# ─────────────────────────────────────────────────────────────
# Public Functions
# ─────────────────────────────────────────────────────────────
__all__ = ["plot_tc_impact"]

# ─────────────────────────────────────────────────────────────
# Plot Tropical Cyclone Impact
# ─────────────────────────────────────────────────────────────
def plot_tc_impact(track, gdf_litpop, gdf_impact,
                   title="TC Impact",
                   wind_var="max_sustained_wind",
                   boundary_gdf=None,
                   save_fig=False,
                   save_path=None,
                   show_buffer=False,
                   show_grid=False):
    """
    Plot tropical cyclone impact diagnostics using scatter overlays.
    Includes exposure, impact, storm track, and optional boundary clipping.
    """

    def inject_coordinates(gdf):
        gdf = gdf.copy()
        gdf["longitude"] = gdf.geometry.x
        gdf["latitude"] = gdf.geometry.y
        return gdf

    gdf_litpop = inject_coordinates(gdf_litpop)
    gdf_impact = inject_coordinates(gdf_impact)

    # Defensive check
    required_cols = ['longitude', 'latitude', 'value']
    missing = [col for col in required_cols if col not in gdf_litpop.columns]
    if missing:
        raise KeyError(f"Missing columns in exposure data: {missing}")
    if wind_var not in track or gdf_impact.empty:
        print("⚠️ Missing wind data or impact points.")
        return

    # Setup figure with gridspec
    fig = plt.figure(figsize=(14, 10))
    gs = gridspec.GridSpec(1, 2, width_ratios=[20, 1])
    ax = fig.add_subplot(gs[0], projection=ccrs.PlateCarree())

    # Add base features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.STATES, linewidth=0.3)

    # Optional gridlines
    if show_grid:
        gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='gray', alpha=0.3)
        gl.top_labels = gl.right_labels = False

    # Set extent
    lon_min, lon_max = gdf_impact['longitude'].min(), gdf_impact['longitude'].max()
    lat_min, lat_max = gdf_impact['latitude'].min(), gdf_impact['latitude'].max()
    if lon_min == lon_max: lon_min -= 0.5; lon_max += 0.5
    if lat_min == lat_max: lat_min -= 0.5; lat_max += 0.5
    extent = [lon_min - 1, lon_max + 1, lat_min - 1, lat_max + 1]
    ax.set_extent(extent, crs=ccrs.PlateCarree())

    # ─────────────────────────────────────────────────────────────
    # Exposure Diagnostic (Scatter Only)
    # ─────────────────────────────────────────────────────────────
    log_exp = np.log10(np.maximum(gdf_litpop['value'].values, 1))
    scatter_exp = ax.scatter(gdf_litpop['longitude'], gdf_litpop['latitude'],
                             c=log_exp, cmap='inferno', s=10, alpha=0.6,
                             transform=ccrs.PlateCarree())
    cbar_exp = fig.colorbar(scatter_exp, ax=ax, orientation='vertical', shrink=0.6, pad=0.01)
    cbar_exp.set_label("log₁₀(Asset Value)")
    print("✅ Exposure plotted via scatter.")

    # ─────────────────────────────────────────────────────────────
    # Impact Diagnostic (Scatter Only)
    # ─────────────────────────────────────────────────────────────
    gdf_impact.plot(ax=ax, column='impact_usd', cmap='magma', markersize=12,
                    legend=True, legend_kwds={'label': "Impact (USD)", 'shrink': 0.6},
                    transform=ccrs.PlateCarree())
    print("✅ Impact plotted via points.")

    # ─────────────────────────────────────────────────────────────
    # Optional Boundary Overlay
    # ─────────────────────────────────────────────────────────────
    if boundary_gdf is not None:
        try:
            impact_zone = MultiPoint(gdf_impact.geometry.tolist()).buffer(0.5)
            boundary_clipped = boundary_gdf.clip(impact_zone)
            if boundary_clipped.empty:
                print("⚠️ Clipped boundary is empty. Using full country boundary.")
                boundary_clipped = boundary_gdf
            boundary_clipped = boundary_clipped[boundary_clipped.is_valid]
            boundary_clipped = boundary_clipped[boundary_clipped.geom_type.isin(['Polygon', 'MultiPolygon'])]
            boundary_clipped.plot(ax=ax, edgecolor='dimgray', linewidth=0.8,
                                  facecolor='none', alpha=0.6, transform=ccrs.PlateCarree())
            print("✅ Boundary overlay plotted.")

            if show_buffer:
                gpd.GeoSeries(impact_zone).plot(ax=ax, edgecolor='blue', facecolor='none', alpha=0.3)
                print("🌀 Buffered impact zone previewed.")
        except Exception as e:
            print(f"⚠️ Boundary clipping failed: {e}")

    # ─────────────────────────────────────────────────────────────
    # Storm Track with Gradient and Markers
    # ─────────────────────────────────────────────────────────────
    track_lons = track['lon'].values
    track_lats = track['lat'].values
    track_wind = track[wind_var].values
    segments = np.concatenate([track_lons[:-1, None], track_lats[:-1, None],
                               track_lons[1:, None], track_lats[1:, None]], axis=1).reshape(-1, 2, 2)
    ax.plot(track_lons, track_lats, color='black', linewidth=5, alpha=0.3,
            transform=ccrs.PlateCarree(), zorder=2)
    lc = LineCollection(segments, cmap='cividis', norm=plt.Normalize(track_wind.min(), track_wind.max()),
                        linewidth=4, array=track_wind, transform=ccrs.PlateCarree())
    ax.add_collection(lc)
    scatter_track = ax.scatter(track_lons, track_lats, c=track_wind, cmap='plasma', s=30,
                               edgecolor='black', linewidth=0.5, transform=ccrs.PlateCarree(), zorder=4)
    cbar_track = fig.colorbar(lc, ax=ax, orientation='vertical', shrink=0.6, pad=0.02)
    cbar_track.set_label("Wind Speed (knots)")
    print("✅ Storm track plotted.")

    # ─────────────────────────────────────────────────────────────
    # Final Touches
    # ─────────────────────────────────────────────────────────────
    fig.suptitle(f"{title}", fontsize=16, fontweight='bold')
    fig.text(0.5, 0.01, "CCART diagnostics – scatter mode", ha='center', fontsize=10)
    fig.subplots_adjust(left=0.05, right=0.95, top=0.92, bottom=0.05)

    if save_fig:
        fallback_name = f"{title.replace(' ', '_')}.png"
        fig.savefig(save_path or fallback_name, dpi=300, bbox_inches='tight')
        print(f"✅ Figure saved to: {save_path or fallback_name}")

    plt.show()

    # ─────────────────────────────────────────────────────────────
    # Summary Stats
    # ─────────────────────────────────────────────────────────────
    try:
        total_impact = gdf_impact['impact_usd'].sum()
        print(f"\n💥 Total impact: ${total_impact:,.0f}")
        print(f"Plotted zones (> $1M): {len(gdf_impact)}")
    except Exception as e:
        print(f"⚠️ Failed to summarize impact: {e}")
