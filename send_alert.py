# Import required libraries
import smtplib  # For sending emails using SMTP protocol
import re  # For validating email format using regular expressions
import os  # For accessing environment variables and system functions
from twilio.rest import Client  # For sending SMS messages using Twilio service
from email.mime.text import MIMEText  # For creating plain text email content
from email.mime.multipart import MIMEMultipart  # For creating email with multiple parts (subject, body, etc.)
from dotenv import load_dotenv  # For loading sensitive data from .env file

# Load environment variables from .env file
load_dotenv()


class AlertSender:
    """
    A class that handles sending alerts through SMS and email
    Uses Twilio for SMS and Gmail SMTP for email
    """

    def __init__(self):
        # Initialize Twilio client with account credentials from .env file
        self.twilio_client = Client(
            os.getenv("TWILIO_ACCOUNT_SID"),  # Get Twilio account ID from environment
            os.getenv("TWILIO_AUTH_TOKEN")  # Get Twilio authentication token from environment
        )
        # Store Twilio phone number and email credentials from environment variables
        self.twilio_number = os.getenv("TWILIO_PHONE_NUMBER")  # The Twilio phone number to send from
        self.email_address = os.getenv("EMAIL_ADDRESS")  # Gmail address to send from
        self.email_password = os.getenv("EMAIL_PASSWORD")  # Gmail password or app password

    def is_valid_email(self, email):
        """
        Validates if the given email address has correct format
        Returns True if email format is valid, False otherwise
        """
        # Regular expression pattern for basic email validation
        pattern = r"[^@]+@[^@]+\.[^@]+"
        return re.match(pattern, email) is not None

    def send_sms(self, to_phone, message):
        """
        Sends SMS message using Twilio service
        Returns tuple of (success_status, response_message)
        """
        try:
            # Check if Twilio phone number is configured
            if not self.twilio_number:
                raise ValueError("Twilio 'from' number is not set. Check your .env file for TWILIO_PHONE_NUMBER.")
            
            # Create and send SMS message using Twilio
            sms = self.twilio_client.messages.create(
                body=message,  # The message content
                from_=self.twilio_number,  # Sender's Twilio number
                to=to_phone,  # Recipient's phone number
            )
            print("SMS sent successfully.")
            return True, sms.sid  # Return success and message ID
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False, str(e)  # Return failure and error message

    def send_email(self, to_email, subject, message):
        """
        Sends email using Gmail SMTP server
        Returns tuple of (success_status, response_message)
        """
        try:
            # Create email message object
            msg = MIMEMultipart()
            msg["From"] = self.email_address  # Set sender email
            msg["To"] = to_email  # Set recipient email
            msg["Subject"] = subject  # Set email subject
            msg.attach(MIMEText(message, "plain"))  # Add message body as plain text

            # Connect to Gmail SMTP server and send email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(self.email_address, self.email_password)  # Login to Gmail
                server.send_message(msg)  # Send the email

            print("Email sent successfully.")
            return True, "Email sent"
        except Exception as e:
            print(f"Email sending failed: {e}")
            return False, str(e)

    def send_alert(self, phone, email, message):
        """
        Main alert sending function that tries SMS first, then falls back to email if sms fails
        Returns tuple of (method_used, response_message)
        """
        # Try sending SMS first
        sms_success, sms_response = self.send_sms(phone, message)
        if sms_success:
            return "SMS", sms_response

        # If SMS fails, try sending email
        if self.is_valid_email(email):
            email_success, email_response = self.send_email(
                email,
                "Severe Weather Alert",  # Email subject
                message,  # Email body
            )
            if email_success:
                return "Email", email_response
            else:
                return "Failed", email_response
        else:
            return "Failed", "Invalid email address"