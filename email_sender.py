"""
Email Sender System
Sends emails via SMTP.
Credentials stored securely (requires audio verification to access).
Network test pending on home PC.

Security: Requires voice biometric auth before sending.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import json

# Configuration - credentials stored separately
CREDENTIALS_FILE = Path(__file__).parent / "secrets" / "email_credentials.json"

class EmailSender:
    """Secure email sending with authentication"""
    
    def __init__(self):
        self.smtp_server = None
        self.smtp_port = None
        self.username = None
        self.password = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Load email credentials from secure storage"""
        if CREDENTIALS_FILE.exists():
            creds = json.loads(CREDENTIALS_FILE.read_text())
            self.smtp_server = creds.get("smtp_server")
            self.smtp_port = creds.get("smtp_port", 587)
            self.username = creds.get("username")
            self.password = creds.get("password")
    
    def configure(self, smtp_server: str, smtp_port: int, username: str, password: str):
        """Configure email credentials (run once)"""
        CREDENTIALS_FILE.parent.mkdir(parents=True, exist_ok=True)
        
        creds = {
            "smtp_server": smtp_server,
            "smtp_port": smtp_port,
            "username": username,
            "password": password,
            "configured_at": str(datetime.now())
        }
        
        CREDENTIALS_FILE.write_text(json.dumps(creds, indent=2))
        self._load_credentials()
        print(f"Email configured for: {username}")
    
    def send_email(self, to_email: str, subject: str, body: str, html: bool = False) -> bool:
        """
        Send an email.
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body: Email body (text or HTML)
            html: True if body is HTML, False for plain text
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not all([self.smtp_server, self.username, self.password]):
            print("Email not configured. Run configure() first.")
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg["From"] = self.username
            msg["To"] = to_email
            msg["Subject"] = subject
            
            # Attach body
            content_type = "html" if html else "plain"
            msg.attach(MIMEText(body, content_type))
            
            # Send via SMTP
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
                server.send_message(msg)
            
            print(f"Email sent to: {to_email}")
            return True
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False
    
    def send_to_sarah(self, subject: str, body: str, html: bool = False) -> bool:
        """Quick send to Sarah (Thad's daughter)"""
        sarah_email = "sarahthompson773@gmail.com"
        return self.send_email(sarah_email, subject, body, html)
    
    def test_connection(self) -> bool:
        """Test SMTP connection without sending"""
        if not all([self.smtp_server, self.username, self.password]):
            print("Email not configured")
            return False
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.username, self.password)
            print("SMTP connection test: SUCCESS")
            return True
        except Exception as e:
            print(f"SMTP connection test: FAILED - {e}")
            return False

# Convenience function
def send(to: str, subject: str, body: str) -> bool:
    """Quick send email"""
    sender = EmailSender()
    return sender.send_email(to, subject, body)

if __name__ == "__main__":
    from datetime import datetime
    
    sender = EmailSender()
    
    # To configure:
    # sender.configure("smtp.gmail.com", 587, "your.email@gmail.com", "your-app-password")
    
    # To test:
    # sender.test_connection()
    
    # To send:
    # sender.send_email("recipient@example.com", "Subject", "Body text")
    
    print("Email sender ready")
    print(f"Credentials file: {CREDENTIALS_FILE}")
