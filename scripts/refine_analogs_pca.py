import numpy as np
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import cosine_similarity

def encode_track(track, n_points=20):
    """
    Encode cyclone track as fixed-length lat/lon vector.
    """
    lat = np.interp(np.linspace(0, 1, n_points), np.linspace(0, 1, len(track["lat"])), track["lat"])
    lon = np.interp(np.linspace(0, 1, n_points), np.linspace(0, 1, len(track["lon"])), track["lon"])
    return np.concatenate([lat, lon])

def refine_bhola_analogs(tracks, labels, target_cluster=2, n_components=10, top_n=5):
    """
    Refine Bhola-like analogs using PCA and cosine similarity.

    Parameters:
        tracks (List[xarray.Dataset]): All tracks.
        labels (List[int]): Cluster labels from DBSCAN.
        target_cluster (int): Cluster ID to refine.
        n_components (int): PCA components.
        top_n (int): Number of refined analogs to return.

    Returns:
        List[xarray.Dataset]: Refined Bhola-like tracks.
    """
    encoded = np.array([encode_track(t) for t in tracks])
    pca = PCA(n_components=n_components)
    reduced = pca.fit_transform(encoded)

    # Compute centroid of target cluster
    cluster_indices = [i for i, label in enumerate(labels) if label == target_cluster]
    centroid = np.mean([reduced[i] for i in cluster_indices], axis=0)

    # Compute cosine similarity to centroid
    similarities = cosine_similarity([centroid], reduced)[0]
    top_indices = np.argsort(similarities)[-top_n:]

    refined_tracks = [tracks[i] for i in top_indices]
    print(f"✅ Refined {top_n} Bhola-like analogs using PCA and cosine similarity")
    return refined_tracks
