from __future__ import annotations
import os
from typing import List, Dict
from google.cloud import storage

_storage = None

def get_storage_client():
    global _storage
    if _storage is None:
        # Explicitly set the project if it's not in environment
        import os
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT', 'hack-deal-generator')
        _storage = storage.Client(project=project_id)
    return _storage

def download_gcs_objects(gcs_paths: List[str]) -> List[Dict]:
    out = []
    for uri in gcs_paths:
        if not uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {uri}")
        bucket_name, blob_name = uri.replace("gs://", "").split("/", 1)
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        filename = os.path.basename(blob_name)
        local_path = os.path.join("/tmp", filename)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)

        ext = os.path.splitext(local_path)[1].lower().lstrip(".")  # pdf|pptx|ppt
        out.append({"path": local_path, "type": ext})
    return out
