import os
import shutil # For creating/deleting directories
from fastapi import UploadFile
from google.cloud import storage # Keep import for type hinting, but won't be used if GCS is disabled
from google.api_core import exceptions # Keep import for type hinting

class CloudStorageService:
    """
    A service for interacting with Google Cloud Storage or local file system.
    """
    def __init__(self):
        self.bucket_name = os.environ.get("CLOUD_STORAGE_BUCKET")
        self.use_gcs = False # Flag to control GCS usage

        if not self.bucket_name:
            print("WARNING: CLOUD_STORAGE_BUCKET environment variable not set. "
                  "Using local file system for storage.")
            self.client = None
            self.bucket = None
            self.local_storage_dir = "local_storage"
            os.makedirs(self.local_storage_dir, exist_ok=True) # Ensure local storage directory exists
        else:
            try:
                self.client = storage.Client()
                self.bucket = self.client.get_bucket(self.bucket_name)
                self.use_gcs = True
                print(f"Google Cloud Storage service initialized for bucket: {self.bucket_name}")
            except exceptions.NotFound:
                print(f"ERROR: Bucket '{self.bucket_name}' not found. Falling back to local storage.")
                self.client = None
                self.bucket = None
                self.local_storage_dir = "local_storage"
                os.makedirs(self.local_storage_dir, exist_ok=True)
            except Exception as e:
                print(f"ERROR: Failed to initialize GCS client: {e}. Falling back to local storage.")
                self.client = None
                self.bucket = None
                self.local_storage_dir = "local_storage"
                os.makedirs(self.local_storage_dir, exist_ok=True)


    # Modified to accept content as bytes directly, or UploadFile for compatibility
    def upload(self, destination_filename: str, content: bytes):
        """
        Uploads content (as bytes) to GCS or saves to local file system.
        """
        if self.use_gcs:
            try:
                blob = self.bucket.blob(destination_filename)
                blob.upload_from_string(content) # Use upload_from_string for bytes
                print(f"Successfully uploaded '{destination_filename}' to GCS bucket '{self.bucket_name}'.")
            except Exception as e:
                print(f"ERROR: Failed to upload file to GCS: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload to GCS: {e}")
        else:
            # Local storage implementation
            file_path = os.path.join(self.local_storage_dir, destination_filename)
            try:
                with open(file_path, "wb") as f:
                    f.write(content)
                print(f"Successfully saved '{destination_filename}' to local storage.")
            except Exception as e:
                print(f"ERROR: Failed to save file to local storage: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save locally: {e}")


    def download(self, source_filename: str) -> bytes:
        """
        Downloads a file from GCS or reads from local file system.
        """
        if self.use_gcs:
            try:
                blob = self.bucket.blob(source_filename)
                return blob.download_as_bytes()
            except exceptions.NotFound:
                print(f"ERROR: File '{source_filename}' not found in GCS bucket '{self.bucket_name}'.")
                return b"" # Return empty bytes if not found
            except Exception as e:
                print(f"ERROR: Failed to download file from GCS: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to download from GCS: {e}")
        else:
            # Local storage implementation
            file_path = os.path.join(self.local_storage_dir, source_filename)
            if not os.path.exists(file_path):
                print(f"ERROR: File '{source_filename}' not found in local storage.")
                return b""
            try:
                with open(file_path, "rb") as f:
                    return f.read()
            except Exception as e:
                print(f"ERROR: Failed to read file from local storage: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to read locally: {e}")


    def delete(self, filename: str):
        """
        Deletes a file from GCS or from local file system.
        """
        if self.use_gcs:
            try:
                blob = self.bucket.blob(filename)
                blob.delete()
                print(f"Successfully deleted '{filename}' from GCS bucket '{self.bucket_name}'.")
            except exceptions.NotFound:
                print(f"WARNING: File '{filename}' not found for deletion in GCS bucket '{self.bucket_name}'.")
            except Exception as e:
                print(f"ERROR: Failed to delete file from GCS: {e}")
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete from GCS: {e}")
        else:
            # Local storage implementation
            file_path = os.path.join(self.local_storage_dir, filename)
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"Successfully deleted '{filename}' from local storage.")
                except Exception as e:
                    print(f"ERROR: Failed to delete file from local storage: {e}")
                    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete locally: {e}")
            else:
                print(f"WARNING: File '{filename}' not found for deletion in local storage.")

