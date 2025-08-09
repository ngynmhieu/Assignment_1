
import matplotlib.pyplot as plt
import datetime
import io, base64
import logging

from back_end.services.google_service.google_service import GoogleService
from back_end.services.mongodb_service.mongodb_service import MongoDBService

def main_generate_daily_report(
    query_dict: dict, 
    mongodb_service: MongoDBService, 
    google_service: GoogleService
) -> dict:
    """
    Generate a daily report from the processed data.
    """
    try:
        email_address = query_dict.get("email_address")
        
        # 1. Fetch the necessary data from the mongodb
        all_docs = mongodb_service.find_documents_with_filter({})

        # 2. Group documents by their creation date
        grouped_docs = _group_documents_by_date(all_docs)

        # 3. Generate analytics chart
        chart_html = _generate_analytics_chart(grouped_docs)

        # 4. Generate email content
        subject, body = _generate_mail_content(grouped_docs, chart_html)

        # 5. Send email notification if email address is provided
        sent_mail = google_service.send_email(email_address, subject, body)

        return sent_mail
    except Exception as e:
        logging.error(f"Error at main_generate_daily_report: {e}")
        return {}


def _group_documents_by_date(docs: list) -> dict:
    """
    Group documents by their creation date.
    """
    grouped_docs = {}
    for doc in docs:
        date = doc.get("created_date").date()
        if date not in grouped_docs:
            grouped_docs[date] = {"Success": [], "Failed": []}

        # Consider a successful doc by the generation status
        if doc.get("generation_status", "Failed") == "Success":
            grouped_docs[date]["Success"].append(doc)
        else:
            grouped_docs[date]["Failed"].append(doc)
    return grouped_docs

def _generate_mail_content(docs: dict, chart_html: str) -> tuple:
    subject = "[AutomationWorkflow] Daily report"

    body = """
<h1 style='color:#2d7cff;'>📅 Daily Report Summary</h1>
<hr>
"""
    # Add analytics chart image
    body += f"<div style='text-align:center;'>{chart_html}</div><hr>"
    if not docs:
        body += "<p>No data available for the selected period.</p>"
    else:
        for date, results in sorted(docs.items()):
            body += f"<h2 style='color:#444;'>{date}</h2>"
            num_success = len(results.get("Success", []))
            num_failed = len(results.get("Failed", []))
            body += f"<ul>"
            body += f"<li><b>✅ Successful generations:</b> {num_success}</li>"
            body += f"<li><b>❌ Failed generations:</b> {num_failed}</li>"
            body += f"</ul>"
            body += "<hr>"
    return subject, body

def _generate_analytics_chart(docs: dict) -> str:
    # Get last 5 days sorted
    today = datetime.date.today()
    last_5_days = [today - datetime.timedelta(days=i) for i in range(4, -1, -1)]
    last_5_days_str = [d.strftime('%Y-%m-%d') for d in last_5_days]
    success_counts = []
    failed_counts = []
    for d in last_5_days:
        day_docs = docs.get(d, {'Success': [], 'Failed': []})
        success_counts.append(len(day_docs.get('Success', [])))
        failed_counts.append(len(day_docs.get('Failed', [])))
    plt.figure(figsize=(7,3.5))
    plt.plot(last_5_days_str, success_counts, marker='o', color='green', label='Success')
    plt.plot(last_5_days_str, failed_counts, marker='o', color='red', label='Failed')
    plt.xlabel('Date')
    plt.ylabel('Number of Documents')
    plt.title('Daily Success/Failed Document Counts (Last 5 Days)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    # Save to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    # Return HTML img tag with some styling
    return f"<img src='data:image/png;base64,{img_base64}' alt='Analytics Chart' style='max-width:500px;width:100%;border:1px solid #ccc;border-radius:8px;box-shadow:0 2px 8px #aaa;margin:10px 0;'/>"