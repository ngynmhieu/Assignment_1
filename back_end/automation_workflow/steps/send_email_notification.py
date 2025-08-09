from datetime import datetime
import logging

from back_end.services.google_service.google_service import GoogleService

def main_send_email_notifications(progress_status: str, query_dict: dict, error_message: str, google_service: GoogleService) -> dict:
    """
    Main function to send email notifications
    """
    from email.mime.text import MIMEText
    try:
        # Get email address
        email_address = query_dict.get("email_address")
        if email_address:
            subject, body = _prepare_mail_content(progress_status, query_dict, error_message)
            sent_message = google_service.send_email(email_address, subject, body)

        return sent_message
    except Exception as e:
        logging.error(f"Error in main_send_email_notifications: {e}")
        return {}

def _prepare_mail_content(progress_status: str, query_dict: dict, error_message: str) -> tuple:
    """
    Prepare the email subject and body content
    """
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_name = query_dict.get("file_name", "Untitled")
    sheet_name = query_dict.get("sheet_name", "Sheet1")

    # Subject of the email
    subject = f"[AutomationWorkflow] {progress_status} - {time_now}"

    # Body of the email (HTML)
    if progress_status == "Success":
        body = f"""
<h1 style='color:green;'>✅ Processing Complete</h1>
<b>Google Sheet File:</b> {file_name}<br>
<b>Sheet Name:</b> {sheet_name}<br><br>
Your Google Sheet file has been processed successfully.<br>
<hr>
"""
    else:
        body = f"""
<h1 style='color:red;'>❌ Processing Failed</h1>
<b>Google Sheet File:</b> {file_name}<br>
<b>Sheet Name:</b> {sheet_name}<br><br>
Your Google Sheet file has failed processing.<br><br>
<b>Error:</b><br>
<pre style='color:red;'>{error_message}</pre>
<hr>
"""

    # Continued body of the email
    all_files = query_dict.get("data", [])
    created_files = [file for file in all_files if file.get("generation_status") == "Success"]
    uploaded_files = [file for file in all_files if file.get("google_drive_uploaded_file") != {}]
    body += f"""
<h2>📊 Summary</h2>
<ul>
  <li><b>Files created successfully:</b> {len(created_files)}/{len(all_files)}</li>
  <li><b>Files uploaded to Google Drive:</b> {len(uploaded_files)}/{len(all_files)}</li>
</ul>
<h2>📄 Details of Each File</h2>
<ul>
"""
    for idx, file in enumerate(all_files, 1):
        file_name = file.get("File Name", "N/A")
        file_extension = file.get("Output Format", "N/A").lower()
        generation_status = file.get("generation_status", "N/A")
        uploaded_status = "Uploaded" if file.get("google_drive_uploaded_file") else "Not Uploaded"
        invalid_message = file.get("invalid_message", "")
        body += f"  <li><b>{idx}. File Name:</b> {file_name}.{file_extension}<br>"
        body += f"  &nbsp;&nbsp;- <b>Generation Status:</b> {generation_status}<br>"
        body += f"  &nbsp;&nbsp;- <b>Uploaded Status:</b> {uploaded_status}"
        if invalid_message:
            body += f"<br>  &nbsp;&nbsp;- <b>Invalid input:</b> {invalid_message}"
        body += "</li>\n"
    body += "</ul>"

    return subject, body