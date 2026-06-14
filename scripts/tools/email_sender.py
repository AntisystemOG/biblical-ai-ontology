#!/usr/bin/env python3
"""
Email sender for Spock via Gmail SMTP
Secure, authorized-only sending with audit trail
"""

import smtplib
import os
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path

# Authorized recipients (update EMAIL.md to add more)
AUTHORIZED_RECIPIENTS = {
    "sarah": "sarahthompson773@gmail.com",
    "thad": "thadandashley@gmail.com",
    "ashley": "thadandashley@gmail.com",
}

# Gmail credentials from environment
GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

# Audit log
AUDIT_LOG = Path("memory/email_audit.json")


def log_email(to_address, subject, status, error=None):
    """Log email send attempt to audit trail"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "to": to_address,
        "subject": subject,
        "status": status,
        "error": error,
    }
    
    # Load existing log
    if AUDIT_LOG.exists():
        with open(AUDIT_LOG) as f:
            logs = json.load(f)
    else:
        logs = []
    
    logs.append(log_entry)
    
    # Save updated log
    with open(AUDIT_LOG, "w") as f:
        json.dump(logs, f, indent=2)


def is_authorized(email_address):
    """Check if email is in authorized list"""
    return email_address.lower() in [v.lower() for v in AUTHORIZED_RECIPIENTS.values()]


def send_email(to_address, subject, body, is_html=False):
    """
    Send email via Gmail SMTP
    
    Args:
        to_address (str): Recipient email
        subject (str): Email subject
        body (str): Email body (plain text or HTML)
        is_html (bool): If True, body is treated as HTML
    
    Returns:
        dict: {"success": bool, "message": str}
    """
    
    # Validate credentials
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        error = "Gmail credentials not configured. Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD env vars."
        log_email(to_address, subject, "failed", error)
        return {"success": False, "message": error}
    
    # Check authorization
    if not is_authorized(to_address):
        error = f"{to_address} not in authorized recipients"
        log_email(to_address, subject, "blocked", error)
        return {"success": False, "message": error}
    
    try:
        # Build message
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = to_address
        msg["Subject"] = subject
        
        content_type = "html" if is_html else "plain"
        msg.attach(MIMEText(body, content_type))
        
        # Send via SMTP (TLS on port 587)
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        
        log_email(to_address, subject, "sent")
        return {"success": True, "message": f"Email sent to {to_address}"}
    
    except smtplib.SMTPAuthenticationError:
        error = "Gmail authentication failed. Check app password."
        log_email(to_address, subject, "failed", error)
        return {"success": False, "message": error}
    
    except smtplib.SMTPException as e:
        error = f"SMTP error: {str(e)}"
        log_email(to_address, subject, "failed", error)
        return {"success": False, "message": error}
    
    except Exception as e:
        error = f"Unexpected error: {str(e)}"
        log_email(to_address, subject, "failed", error)
        return {"success": False, "message": error}


def get_authorized_list():
    """Return list of authorized recipients"""
    return AUTHORIZED_RECIPIENTS


# Test when run directly
if __name__ == "__main__":
    print("Email Sender Ready")
    print(f"Gmail account: {GMAIL_ADDRESS}")
    print(f"Authorized recipients: {', '.join(AUTHORIZED_RECIPIENTS.values())}")
    
    # Test send (uncomment to test)
    # result = send_email("sarahthompson773@gmail.com", "Test from Spock", "If you got this, it works!")
    # print(result)
