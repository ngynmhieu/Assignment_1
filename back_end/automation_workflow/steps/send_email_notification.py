import logging

from back_end.google_service.google_service import GoogleService

def main_send_email_notifications(query_dict: dict, google_service: GoogleService) -> dict:
    """
    Main function to send email notifications
    """
    try:
        email_address = query_dict.get("email_address")
        if email_address:
            subject = "File Uploaded Successfully"
            body = f"Your file has been uploaded successfully."
            sent_message = google_service.send_email(email_address, subject, body)

        return sent_message
    except Exception as e:
        logging.error(f"Error in main_send_email_notifications: {e}")
        return {}