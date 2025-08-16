#!/usr/bin/env python3
# Test email sending functionality

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def test_email():
    print("Testing email configuration...")
    
    # Get email settings
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")
    receiver_emails_env = os.getenv("RECEIVER_EMAIL", "")
    receiver_emails = [email.strip() for email in receiver_emails_env.split(",") if email.strip()]
    
    print(f"SMTP Server: {smtp_server}:{smtp_port}")
    print(f"Sender: {sender_email}")
    print(f"Recipients: {receiver_emails}")
    
    # Check required settings
    if not sender_email:
        print("❌ SENDER_EMAIL not set")
        return False
    if not sender_password:
        print("❌ SENDER_PASSWORD not set")
        return False
    if not receiver_emails:
        print("❌ RECEIVER_EMAIL not set")
        return False
    
    try:
        # Create test message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = ", ".join(receiver_emails)
        msg['Subject'] = "🧪 POPMART Stock Checker - Email Test"
        
        body = """
This is a test email from your POPMART stock checker.

If you receive this, your email configuration is working correctly!

Test details:
- SMTP Server: {}:{}
- Sender: {}
- Time: Testing phase

🎉 Email notifications are ready!
        """.format(smtp_server, smtp_port, sender_email).strip()
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        print("Connecting to SMTP server...")
        
        # Try SMTP_SSL first (port 465)
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                print("Using SMTP_SSL (port 465)...")
                print("Logging in...")
                server.login(sender_email, sender_password)
                print("Sending email...")
                server.send_message(msg)
        else:
            # Try regular SMTP with STARTTLS (port 587)
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                print("Starting TLS...")
                server.starttls()
                print("Logging in...")
                server.login(sender_email, sender_password)
                print("Sending email...")
                server.send_message(msg)
        
        print(f"✅ Test email sent successfully to {', '.join(receiver_emails)}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send test email: {e}")
        return False

if __name__ == "__main__":
    test_email()