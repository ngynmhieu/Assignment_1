

from back_end.google_service.google_service import GoogleService
import logging


def main_load_input_source_data(query_dict: dict, google_service: GoogleService) -> None:
    """
    Main function to load input source data for the automation workflow.
    """
    try:
        # Extract Google Sheets URL
        google_sheets_url = query_dict.get("google_sheets_url", "")

        # Load data from Google Sheets
        if google_sheets_url:
            data = google_service.get_data_from_sheets(google_sheets_url)
            return data
    
    except Exception as e:
        logging.error(f"Error loading input source data: {e}")
        return []