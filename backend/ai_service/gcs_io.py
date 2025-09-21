from __future__ import annotations
import os
from typing import List, Dict
from google.cloud import storage

_storage = storage.Client()

def download_gcs_objects(gcs_paths: List[str]) -> List[Dict]:
    out = []
    for uri in gcs_paths:
        if not uri.startswith("gs://"):
            raise ValueError(f"Invalid GCS URI: {uri}")
        bucket_name, blob_name = uri.replace("gs://", "").split("/", 1)
        bucket = _storage.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        filename = os.path.basename(blob_name)
        local_path = os.path.join("/tmp", filename)
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        blob.download_to_filename(local_path)

        ext = os.path.splitext(local_path)[1].lower().lstrip(".")  # pdf|pptx|ppt
        out.append({"path": local_path, "type": ext})
    return out
