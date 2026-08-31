import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any
from jinja2 import Template
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    async def send_confirmation_email(
        to_email: str,
        submission_data: Dict[str, Any],
        widget_title: str
    ) -> bool:
        """
        Send a confirmation email to the lead.
        Returns: True if sent successfully, False otherwise.
        """
        try:
            # Create email content
            subject = f"Thank you for your submission - {widget_title}"
            
            # HTML template for the email
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #007bff; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .footer { text-align: center; padding: 10px; font-size: 12px; color: #666; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>Thank You!</h2>
                    </div>
                    <div class="content">
                        <p>Dear {{ name }},</p>
                        <p>Thank you for submitting your information through our <strong>{{ widget_title }}</strong> form.</p>
                        <p>We have received your submission and will get back to you shortly.</p>
                        <p><strong>Your submission details:</strong></p>
                        <ul>
                            {% for key, value in submission_data.items() %}
                                <li><strong>{{ key|capitalize }}:</strong> {{ value }}</li>
                            {% endfor %}
                        </ul>
                        <p>If you have any questions, please don't hesitate to contact us.</p>
                        <p>Best regards,<br>The Team</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated message, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Render template
            template = Template(html_template)
            html_content = template.render(
                name=submission_data.get('name', 'Valued Customer'),
                widget_title=widget_title,
                submission_data=submission_data
            )
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = to_email
            
            # Attach HTML content
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email using SMTP
            try:
                # For local development with Mailpit
                if settings.ENVIRONMENT == 'development':
                    # Use Mailpit (no auth)
                    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                    server.send_message(msg)
                    server.quit()
                else:
                    # Production SMTP with TLS
                    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                    server.starttls()
                    if settings.SMTP_USER and settings.SMTP_PASSWORD:
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(msg)
                    server.quit()
                
                logger.info(f"Confirmation email sent to {to_email}")
                return True
                
            except Exception as e:
                logger.error(f"SMTP error sending email to {to_email}: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error preparing email for {to_email}: {e}")
            return False

    @staticmethod
    async def send_lead_notification_email(
        to_email: str,
        submission_data: Dict[str, Any],
        widget_title: str,
        widget_id: int
    ) -> bool:
        """
        Send a lead notification email to the widget owner.
        """
        try:
            subject = f"New Lead: {widget_title}"
            
            html_template = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                    .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                    .header { background: #28a745; color: white; padding: 20px; text-align: center; }
                    .content { padding: 20px; background: #f9f9f9; }
                    .alert { background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>🎉 New Lead Notification</h2>
                    </div>
                    <div class="content">
                        <div class="alert">
                            <strong>New submission received!</strong> A new lead has been submitted through your widget.
                        </div>
                        
                        <p><strong>Widget:</strong> {{ widget_title }}</p>
                        <p><strong>Widget ID:</strong> {{ widget_id }}</p>
                        
                        <p><strong>Lead Details:</strong></p>
                        <ul>
                            {% for key, value in submission_data.items() %}
                                <li><strong>{{ key|capitalize }}:</strong> {{ value }}</li>
                            {% endfor %}
                        </ul>
                        
                        <p>Visit your dashboard to view all leads.</p>
                        
                        <p>Best regards,<br>Lead Capture Platform</p>
                    </div>
                    <div class="footer">
                        <p>This is an automated notification from your lead capture widget.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            template = Template(html_template)
            html_content = template.render(
                widget_title=widget_title,
                widget_id=widget_id,
                submission_data=submission_data
            )
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = settings.EMAIL_FROM
            msg['To'] = to_email
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            if settings.ENVIRONMENT == 'development':
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                server.send_message(msg)
                server.quit()
            else:
                server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                server.starttls()
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                server.quit()
            
            logger.info(f"Lead notification email sent to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending lead notification to {to_email}: {e}")
            return False
