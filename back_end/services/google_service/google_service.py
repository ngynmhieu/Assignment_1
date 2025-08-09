import os
import pickle
import base64
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from email.mime.text import MIMEText

SERVICE_ACCOUNT_FILE = "back_end\\services\\google_service\\configs\\automation-workflow-project-73a3cbdd2942.json"
CLIENT_SECRET_FILE = "back_end\\services\\google_service\\configs\\client_secret_608833324413-fkq10e04u2pht5ksua1rm7j6bjtpeduo.apps.googleusercontent.com.json"
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/gmail.send"
]
SERVICES_USE_O2AUTH = ["drive", "gmail"] 

class GoogleService:
    def get_data_from_sheets(self, google_sheets_url) -> dict   :
        """        
        Get data from Google Sheets
        """
        # Preparation
        service = self._get_service('sheets', 'v4')
        spreadsheet_id = google_sheets_url.split('/d/')[1].split('/')[0]
        range_name = 'Sheet1!A1:Z1000'

        # Get spreadsheet metadata (file name and sheet names)
        sheet = service.spreadsheets()
        metadata = sheet.get(spreadsheetId=spreadsheet_id).execute()
        file_name = metadata.get('properties', {}).get('title', None)
        sheets = metadata.get('sheets', [])
        sheet_name = sheets[0]['properties']['title'] if sheets else None
        range_name = f'{sheet_name}!A1:Z1000' if sheet_name else 'Sheet1!A1:Z1000'
        # Fetch data
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        data = result.get('values', [])
        return {
            "data": data,
            "file_name": file_name,
            "sheet_name": sheet_name
        }

    def store_data_to_drive(self, file_path, google_drive_folder_path):
        """
        Store data to Google Drive
        """
        # Preparation
        service = self._get_service('drive', 'v3')
        folder_id = google_drive_folder_path.split('/')[-1] if google_drive_folder_path else None
        file_metadata = {
            'name': os.path.basename(file_path),
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, resumable=True)
        
        # Upload file
        uploaded_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name'
        ).execute()

        # Result
        return uploaded_file
    
    def send_email(self, email_address, subject, body):
        """
        Send email notification
        """
        service = self._get_service('gmail', 'v1')

        # Prepare the email
        to = email_address
        subject = subject
        body = body

        message = MIMEText(body, 'html')
        message['to'] = to
        message['subject'] = subject

        # Encode the message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Send the email
        sent_message = service.users().messages().send(
            userId="me",
            body={'raw': raw_message}
        ).execute()
        
        return sent_message

    def _get_service(self, api_name, api_version):
        """
        Get Google API service instance with token caching
        """
        # Create credentials
        creds = self._load_credentials(api_name)

        # Build the service
        if not creds:
            service = build(api_name, api_version)
        else:
            service = build(api_name, api_version, credentials=creds)
        return service

    def _load_credentials(self, api_name):
        """
        Load credentials from a file
        """
        creds = None

        if api_name in SERVICES_USE_O2AUTH:
            token_dir = "back_end/services/google_service/configs"
            os.makedirs(token_dir, exist_ok=True)
            token_file = os.path.join(token_dir, f"token.pickle")

            # Load existing token
            if os.path.exists(token_file):
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)
                    
            # If no valid credentials, create new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
                    creds = flow.run_local_server(port=8080)
                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)
        else:
            creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            
        return creds