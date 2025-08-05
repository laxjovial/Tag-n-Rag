import json
from msgraph.core import GraphClient
from src.backend.core.security import decrypt_credentials

class OneDriveService:
    def __init__(self, encrypted_credentials: bytes):
        """
        Initializes the OneDrive service with a user's encrypted credentials.
        """
        creds_json = decrypt_credentials(encrypted_credentials)
        creds = json.loads(creds_json)

        # A real implementation would handle token refresh.
        # The access token is in creds['access_token']
        # For this example, we assume the GraphClient can be initialized
        # with just the token, but it's more complex in reality.
        # This is a simplified placeholder for the logic.
        self.access_token = creds.get('access_token')
        self.client = GraphClient(credential=self.access_token)

    def list_files(self, item_id='root'):
        """
        Lists files and folders in a given OneDrive location.
        """
        try:
            # This is a simplified example of the API call.
            # The actual call might be more complex.
            response = self.client.get(f'/me/drive/items/{item_id}/children').json()
            return response.get('value', [])
        except Exception as e:
            print(f"OneDrive API error: {e}")
            return []

    def download_file(self, item_id: str) -> bytes:
        """
        Downloads a file from OneDrive.
        """
        try:
            # The download URL is typically on the item's metadata
            response = self.client.get(f'/me/drive/items/{item_id}/content')
            return response.content
        except Exception as e:
            print(f"OneDrive API error: {e}")
            return b""
