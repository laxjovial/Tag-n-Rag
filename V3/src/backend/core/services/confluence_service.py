import json
from atlassian import Confluence
from src.backend.core.security import decrypt_credentials

class ConfluenceService:
    def __init__(self, encrypted_credentials: bytes, site_url: str):
        """
        Initializes the Confluence service with a user's encrypted credentials and site URL.
        """
        if not site_url:
            raise ValueError("Confluence site URL is required.")

        creds_json = decrypt_credentials(encrypted_credentials)
        creds = json.loads(creds_json)

        self.confluence = Confluence(
            url=site_url,
            token=creds['access_token']
        )

    def get_all_spaces(self):
        """
        Gets all spaces from Confluence.
        """
        try:
            return self.confluence.get_all_spaces(start=0, limit=50, expand=None)
        except Exception as e:
            print(f"Confluence API error: {e}")
            return []

    def get_all_pages_from_space(self, space_key: str):
        """
        Gets all pages from a given space.
        """
        try:
            return self.confluence.get_all_pages_from_space(space_key)
        except Exception as e:
            print(f"Confluence API error: {e}")
            return []
