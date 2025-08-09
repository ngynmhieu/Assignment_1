import logging

from back_end.services.google_service.google_service import GoogleService

def main_upload_output_data(query_dict: dict, google_service: GoogleService) -> dict:
    try:
        # Extract relevant information from the query_dict
        input_source_data = query_dict.get("data", [])
        updating_input_source_data = []
        google_drive_folder_url = query_dict.get("google_drive_folder_url")

        # Store data to Google Drive
        for row in input_source_data:
            file_path = row.get("file_path")
            if file_path and google_drive_folder_url:
                uploaded_file = google_service.store_data_to_drive(file_path, google_drive_folder_url)
                if uploaded_file:
                    row["google_drive_uploaded_file"] = uploaded_file
            else:
                row["google_drive_uploaded_file"] = {}

            updating_input_source_data.append(row)

        return updating_input_source_data
    except Exception as e:
        logging.error(f"Error in main_upload_output_data: {e}")
        return {}