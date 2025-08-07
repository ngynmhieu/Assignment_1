import logging

from back_end.google_service.google_service import GoogleService

def main_store_output_data(query_dict: dict, google_service: GoogleService) -> dict:
    try:
        # Extract relevant information from the query_dict
        file_path = query_dict.get("file_path")
        google_drive_folder_url = query_dict.get("google_drive_folder_url")

        if not file_path or not google_drive_folder_url:
            return ""

        # Store data to Google Drive
        uploaded_file = google_service.store_data_to_drive(file_path, google_drive_folder_url)
        return uploaded_file
    except Exception as e:
        logging.error(f"Error in main_store_output_data: {e}")
        return {}