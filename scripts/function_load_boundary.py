# ─────────────────────────────────────────────────────────────
# Boundary Overlay Loader for CCART
# ─────────────────────────────────────────────────────────────
import geopandas as gpd
from shapely.geometry import MultiPoint

__all__ = ["load_boundary_overlay"]

def load_boundary_overlay(boundary_path, countries, clip_points=None):
    """
    Load country boundaries from shapefile and optionally clip to buffered impact zone.
    
    Parameters:
        boundary_path (str): Path to Natural Earth shapefile.
        countries (list): List of country names to filter.
        clip_points (list): Optional list of shapely Points to define impact zone.
    
    Returns:
        GeoDataFrame: Filtered and optionally clipped country boundaries.
    """
    try:
        gdf = gpd.read_file(boundary_path).to_crs(epsg=4326)
        gdf = gdf[gdf['ADMIN'].isin(countries)]

        if clip_points:
            impact_zone = MultiPoint(clip_points).buffer(0.5)
            gdf = gdf.clip(impact_zone)

        return gdf

    except Exception as e:
        print(f"⚠️ Failed to load or clip boundary overlay: {e}")
        return gpd.GeoDataFrame(columns=['geometry'], geometry=[], crs="EPSG:4326")
