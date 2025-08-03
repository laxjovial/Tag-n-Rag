import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

class GoogleDriveService:
    def __init__(self, user_credentials_json: str):
        """
        Initializes the Google Drive service with a user's credentials.
        :param user_credentials_json: The user's Google credentials in JSON format.
        """
        self.credentials = Credentials.from_authorized_user_info(user_credentials_json)
        self.service = build('drive', 'v3', credentials=self.credentials)

    def list_files(self, folder_id='root', page_size=100):
        """
        Lists files and folders in a given Google Drive folder.
        :param folder_id: The ID of the folder to list. Defaults to 'root'.
        :param page_size: The number of files to return per page.
        :return: A list of files and folders.
        """
        results = self.service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=page_size,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        return results.get('files', [])

    def download_file(self, file_id: str) -> io.BytesIO:
        """
        Downloads a file from Google Drive.
        :param file_id: The ID of the file to download.
        :return: A BytesIO object containing the file's content.
        """
        request = self.service.files().get_media(fileId=file_id)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)

        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # You could add progress reporting here if needed
            print(f"Download {int(status.progress() * 100)}%.")

        file_buffer.seek(0)
        return file_buffer
