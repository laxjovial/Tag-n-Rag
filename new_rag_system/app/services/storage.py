import os
from fastapi import UploadFile
from google.cloud import storage
from google.api_core import exceptions

class CloudStorageService:
    """
    A service for interacting with Google Cloud Storage.
    """
    def __init__(self):
        self.bucket_name = os.environ.get("CLOUD_STORAGE_BUCKET")
        if not self.bucket_name:
            print("WARNING: CLOUD_STORAGE_BUCKET environment variable not set. "
                  "Google Cloud Storage service will be disabled.")
            self.client = None
            self.bucket = None
        else:
            try:
                self.client = storage.Client()
                self.bucket = self.client.get_bucket(self.bucket_name)
                print(f"Google Cloud Storage service initialized for bucket: {self.bucket_name}")
            except exceptions.NotFound:
                print(f"ERROR: Bucket '{self.bucket_name}' not found.")
                self.client = None
                self.bucket = None
            except Exception as e:
                print(f"ERROR: Failed to initialize GCS client: {e}")
                self.client = None
                self.bucket = None

    def upload(self, file: UploadFile, destination_filename: str):
        """
        Uploads a file to the GCS bucket.
        """
        if not self.bucket:
            print("Skipping GCS upload because storage service is not configured.")
            return

        try:
            blob = self.bucket.blob(destination_filename)
            blob.upload_from_file(file.file, content_type=file.content_type)
            file.file.seek(0)
            print(f"Successfully uploaded '{file.filename}' to '{self.bucket_name}/{destination_filename}'.")
        except Exception as e:
            print(f"ERROR: Failed to upload file to GCS: {e}")
            # You might want to raise an exception here to handle the error upstream
            raise

    def download(self, source_filename: str) -> bytes:
        """
        Downloads a file from the GCS bucket.
        """
        if not self.bucket:
            print("Skipping GCS download because storage service is not configured.")
            return b""

        try:
            blob = self.bucket.blob(source_filename)
            return blob.download_as_bytes()
        except exceptions.NotFound:
            print(f"ERROR: File '{source_filename}' not found in bucket '{self.bucket_name}'.")
            return b""
        except Exception as e:
            print(f"ERROR: Failed to download file from GCS: {e}")
            raise

    def delete(self, filename: str):
        """
        Deletes a file from the GCS bucket.
        """
        if not self.bucket:
            print("Skipping GCS deletion because storage service is not configured.")
            return

        try:
            blob = self.bucket.blob(filename)
            blob.delete()
            print(f"Successfully deleted '{filename}' from bucket '{self.bucket_name}'.")
        except exceptions.NotFound:
            print(f"WARNING: File '{filename}' not found for deletion in bucket '{self.bucket_name}'.")
        except Exception as e:
            print(f"ERROR: Failed to delete file from GCS: {e}")
            raise
