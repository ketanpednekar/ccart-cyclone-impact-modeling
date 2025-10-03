import numpy as np
from sklearn.cluster import DBSCAN

def cluster_tracks_by_path(tracks, eps=1.0, min_samples=3):
    """
    Cluster cyclone tracks based on lat/lon path using DBSCAN.
    
    Parameters:
        tracks (List[xarray.Dataset]): List of historical cyclone tracks.
        eps (float): DBSCAN epsilon (distance threshold in degrees).
        min_samples (int): Minimum samples per cluster.
    
    Returns:
        List[int]: Cluster labels for each track.
    """
    # Extract mean lat/lon per track as a simple feature
    features = []
    for track in tracks:
        lat = track["lat"].values
        lon = track["lon"].values
        features.append([np.mean(lat), np.mean(lon)])

    features = np.array(features)

    # Run DBSCAN clustering
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(features)
    labels = clustering.labels_

    print(f"✅ Clustered {len(tracks)} tracks into {len(set(labels)) - (1 if -1 in labels else 0)} clusters")
    return labels
