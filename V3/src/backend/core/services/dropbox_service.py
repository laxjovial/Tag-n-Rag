import dropbox
import json
from src.backend.core.security import decrypt_credentials

class DropboxService:
    def __init__(self, encrypted_credentials: bytes):
        """
        Initializes the Dropbox service with a user's encrypted credentials.
        """
        creds_json = decrypt_credentials(encrypted_credentials)
        creds = json.loads(creds_json)

        # A real implementation would handle token refresh using the refresh_token
        self.dbx = dropbox.Dropbox(creds['access_token'])

    def list_files(self, path=''):
        """
        Lists files and folders in a given Dropbox path.
        """
        try:
            result = self.dbx.files_list_folder(path)
            return [{"id": entry.id, "name": entry.name, "type": "folder" if isinstance(entry, dropbox.files.FolderMetadata) else "file"} for entry in result.entries]
        except dropbox.exceptions.AuthError as e:
            # This indicates the token may have expired.
            # A full implementation needs a refresh flow.
            print(f"Dropbox auth error: {e}")
            return []

    def download_file(self, file_path: str) -> bytes:
        """
        Downloads a file from Dropbox.
        """
        try:
            metadata, res = self.dbx.files_download(path=file_path)
            return res.content
        except dropbox.exceptions.ApiError as e:
            print(f"Dropbox API error: {e}")
            return b""
