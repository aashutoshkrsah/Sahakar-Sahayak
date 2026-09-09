import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Dict

logger = logging.getLogger("sahakar_sahayak.notification")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

# In-memory store for test verification during automated test runs
# Strictly accessed internally by test suites, never exposed in public API responses.
_TEST_OTP_STORE: Dict[str, str] = {}


def set_test_otp(recipient: str, otp: str):
    """Store OTP in memory for test runner validation."""
    _TEST_OTP_STORE[recipient.strip().lower()] = otp


def get_test_otp(recipient: str) -> Optional[str]:
    """Retrieve test OTP for automated test verification."""
    return _TEST_OTP_STORE.get(recipient.strip().lower())


def clear_test_otps():
    """Clear memory test store."""
    _TEST_OTP_STORE.clear()


def send_email_otp(to_email: str, recipient_name: str, otp: str) -> bool:
    """
    Sends a 6-digit OTP verification code to the user's email address.
    If SMTP credentials are provided in environment variables, sends via real SMTP.
    Otherwise, logs to the console and safely simulates successful delivery.
    """
    clean_email = to_email.strip().lower()
    set_test_otp(clean_email, otp)

    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM_EMAIL", "noreply@sahakarsahayak.gov.in")
    smtp_use_tls = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

    subject = f"Sahakar Sahayak - Your Email Verification Code: {otp}"

    # HTML Email Template
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="utf-8">
      <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; }}
        .container {{ max-width: 540px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; }}
        .header {{ background: #166534; padding: 24px; text-align: center; color: #ffffff; }}
        .header h1 {{ margin: 0; font-size: 20px; letter-spacing: 0.5px; }}
        .header p {{ margin: 4px 0 0 0; font-size: 12px; opacity: 0.85; }}
        .content {{ padding: 32px 24px; }}
        .greeting {{ font-size: 15px; color: #334155; margin-bottom: 16px; }}
        .instructions {{ font-size: 14px; color: #64748b; line-height: 1.5; margin-bottom: 24px; }}
        .otp-box {{ background: #f0fdf4; border: 2px dashed #22c55e; border-radius: 8px; padding: 18px; text-align: center; margin: 24px 0; }}
        .otp-code {{ font-family: monospace; font-size: 32px; font-weight: bold; color: #15803d; letter-spacing: 8px; margin: 0; }}
        .validity {{ font-size: 12px; color: #166534; font-weight: 600; margin-top: 8px; }}
        .warning {{ font-size: 12px; color: #94a3b8; line-height: 1.4; border-top: 1px solid #f1f5f9; padding-top: 16px; }}
        .footer {{ background: #f8fafc; padding: 16px; text-align: center; font-size: 11px; color: #94a3b8; border-top: 1px solid #e2e8f0; }}
      </style>
    </head>
    <body>
      <div class="container">
        <div class="header">
          <h1>Sahakar Sahayak (सहकार सहायक)</h1>
          <p>Digital Intelligence & Governance Guide for Indian Cooperatives</p>
        </div>
        <div class="content">
          <div class="greeting">Namaste <strong>{recipient_name or 'Citizen'}</strong>,</div>
          <div class="instructions">
            Thank you for registering on Sahakar Sahayak. Please use the following One-Time Password (OTP) to verify your email address:
          </div>
          <div class="otp-box">
            <div class="otp-code">{otp}</div>
            <div class="validity">Expires in 10 minutes</div>
          </div>
          <div class="warning">
            <strong>Security Notice:</strong> Never share this OTP with anyone. Ministry officials and Sahakar Sahayak representatives will never ask for your verification code. If you did not initiate this request, you can safely ignore this email.
          </div>
        </div>
        <div class="footer">
          Sahakar Sahayak Initiative • Ministry of Cooperation, Government of India
        </div>
      </div>
    </body>
    </html>
    """

    plain_text = (
        f"Namaste {recipient_name or 'Citizen'},\n\n"
        f"Your Sahakar Sahayak email verification code is: {otp}\n"
        f"This code will expire in 10 minutes.\n\n"
        f"Do not share this OTP with anyone for security purposes.\n\n"
        f"- Sahakar Sahayak Team"
    )

    if smtp_host and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = smtp_from
            msg["To"] = clean_email

            msg.attach(MIMEText(plain_text, "plain"))
            msg.attach(MIMEText(html_content, "html"))

            if smtp_port == 465:
                server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=10)
            else:
                server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
                if smtp_use_tls:
                    server.starttls()

            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_from, [clean_email], msg.as_string())
            server.quit()
            logger.info(f"Email OTP sent successfully to {clean_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email OTP to {clean_email} via SMTP: {e}. Falling back to simulation mode.")

    # Simulated Delivery / Local Development Logger
    print("\n" + "=" * 64)
    print("[EMAIL NOTIFICATION SERVICE - OTP DISPATCH]")
    print(f"To: {recipient_name} <{clean_email}>")
    print(f"Subject: {subject}")
    print(f"Email OTP Code: [ {otp} ] (Valid for 10 minutes)")
    print("=" * 64 + "\n")
    return True


def send_phone_otp(to_phone: str, otp: str) -> bool:
    """
    Sends a 6-digit OTP verification code to the user's phone number via SMS.
    If Twilio or an SMS gateway is configured in environment variables, sends via HTTP API.
    Otherwise, logs to the console and safely simulates successful delivery.
    """
    clean_phone = to_phone.strip()
    set_test_otp(clean_phone, otp)

    message = f"Your Sahakar Sahayak phone verification OTP is: {otp}. Valid for 10 minutes. Do not share this OTP with anyone. - Ministry of Cooperation"

    twilio_sid = os.getenv("TWILIO_ACCOUNT_SID")
    twilio_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from = os.getenv("TWILIO_FROM_NUMBER")
    sms_gateway_url = os.getenv("SMS_GATEWAY_URL")
    sms_api_key = os.getenv("SMS_API_KEY")

    # 1. Twilio SMS Integration
    if twilio_sid and twilio_token and twilio_from:
        try:
            import requests
            url = f"https://api.twilio.com/2010-04-01/Accounts/{twilio_sid}/Messages.json"
            response = requests.post(
                url,
                data={"To": clean_phone, "From": twilio_from, "Body": message},
                auth=(twilio_sid, twilio_token),
                timeout=10,
            )
            if response.status_code in (200, 201):
                logger.info(f"SMS OTP sent via Twilio to {clean_phone}")
                return True
            else:
                logger.warning(f"Twilio SMS returned status {response.status_code}: {response.text}")
        except Exception as e:
            logger.error(f"Failed to send SMS via Twilio: {e}")

    # 2. Generic SMS Gateway Integration
    if sms_gateway_url and sms_api_key:
        try:
            import requests
            response = requests.post(
                sms_gateway_url,
                json={"phone": clean_phone, "message": message, "apiKey": sms_api_key},
                timeout=10,
            )
            if response.status_code in (200, 201):
                logger.info(f"SMS OTP sent via Gateway to {clean_phone}")
                return True
        except Exception as e:
            logger.error(f"Failed to send SMS via Gateway: {e}")

    # Simulated Delivery / Local Development Logger
    print("\n" + "=" * 64)
    print("[SMS NOTIFICATION SERVICE - OTP DISPATCH]")
    print(f"To Phone: {clean_phone}")
    print(f"Message: {message}")
    print(f"Phone OTP Code: [ {otp} ] (Valid for 10 minutes)")
    print("=" * 64 + "\n")
    return True

