import smtplib
from email.message import EmailMessage
import os

EMAIL_USER = "asthasingh00442@gmail.com"
EMAIL_PASS = "tayb uzra jqsw fcaw"  # Gmail App Password

def send_email_alert(df, attachment_path, recipient_email):
    try:
        # Check if file exists
        if not os.path.exists(attachment_path):
            print(f"❌ Attachment file not found: {attachment_path}")
            return

        # Compose Email
        msg = EmailMessage()
        msg['Subject'] = '🚨 Fund Misuse Alert'
        msg['From'] = EMAIL_USER
        msg['To'] = recipient_email
        msg.set_content('Suspicious fund usage has been detected. Please see the attached report.')

        # Attach File
        with open(attachment_path, 'rb') as f:
            filename = os.path.basename(attachment_path)
            msg.add_attachment(f.read(), maintype='application', subtype='octet-stream', filename=filename)

        # Send via Gmail SMTP SSL
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)

        print("✅ Email sent successfully to", recipient_email)

    except smtplib.SMTPAuthenticationError as auth_error:
        print(f"❌ SMTP Authentication Error: {auth_error}")
    except FileNotFoundError as file_error:
        print(f"❌ File not found: {file_error}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

