"""
Email service for sending verification emails
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from loguru import logger

from app.core.config import settings


class EmailService:
    """Email service for sending verification emails"""
    
    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_from = settings.SMTP_FROM
        self.smtp_tls = settings.SMTP_TLS
        self.enabled = settings.SMTP_ENABLED
    
    async def send_verification_email(
        self, 
        to_email: str, 
        verification_token: str,
        username: str
    ) -> bool:
        """Send email verification email"""
        if not self.enabled:
            logger.warning("SMTP is disabled, skipping email verification")
            return True
        
        try:
            # Create verification link
            verification_link = f"http://localhost:8000/api/v1/auth/verify-email?token={verification_token}"
            
            # Create email content
            subject = "Verify Your EdgeTrade Account"
            
            html_content = f"""
            <html>
            <body>
                <h2>Welcome to EdgeTrade!</h2>
                <p>Hello {username},</p>
                <p>Thank you for registering with EdgeTrade Trading Platform. Please verify your email address by clicking the link below:</p>
                <p><a href="{verification_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Verify Email Address</a></p>
                <p>Or copy and paste this link into your browser:</p>
                <p>{verification_link}</p>
                <p>This link will expire in 24 hours.</p>
                <p>If you didn't create an account with EdgeTrade, please ignore this email.</p>
                <br>
                <p>Best regards,<br>EdgeTrade Team</p>
            </body>
            </html>
            """
            
            text_content = f"""
            Welcome to EdgeTrade!
            
            Hello {username},
            
            Thank you for registering with EdgeTrade Trading Platform. Please verify your email address by visiting the link below:
            
            {verification_link}
            
            This link will expire in 24 hours.
            
            If you didn't create an account with EdgeTrade, please ignore this email.
            
            Best regards,
            EdgeTrade Team
            """
            
            # Send email
            return await self._send_email(to_email, subject, text_content, html_content)
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {e}")
            return False
    
    async def _send_email(
        self, 
        to_email: str, 
        subject: str, 
        text_content: str, 
        html_content: Optional[str] = None
    ) -> bool:
        """Send email using SMTP"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_from
            msg['To'] = to_email
            
            # Add text content
            text_part = MIMEText(text_content, 'plain')
            msg.attach(text_part)
            
            # Add HTML content if provided
            if html_content:
                html_part = MIMEText(html_content, 'html')
                msg.attach(html_part)
            
            # Connect to SMTP server
            server = smtplib.SMTP(self.smtp_host, self.smtp_port)
            
            if self.smtp_tls:
                server.starttls()
            
            # Login and send email
            server.login(self.smtp_user, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Verification email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False


# Singleton instance
email_service = EmailService()
