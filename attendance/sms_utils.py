from twilio.rest import Client
from django.conf import settings
import os

def send_sms(phone_number, message):
    """Send SMS using Twilio"""
    try:
        # Twilio credentials from environment variables
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        from_number = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, from_number]):
            return False, "SMS credentials not configured"
        
        client = Client(account_sid, auth_token)
        
        # Format phone number (add +91 for India if not present)
        if not phone_number.startswith('+'):
            phone_number = f'+91{phone_number}'
        
        message = client.messages.create(
            body=message,
            from_=from_number,
            to=phone_number
        )
        
        return True, f"SMS sent successfully. SID: {message.sid}"
        
    except Exception as e:
        return False, f"Failed to send SMS: {str(e)}"

def send_absence_notification(devotee, sabha, sender_name):
    """Send absence notification to devotee"""
    message = f"""
🏛️ BAPS Temple Attendance

Dear {devotee.name},

You were marked absent for {sabha.get_sabha_type_display()} on {sabha.date}.

Please contact {sender_name} if this is incorrect.

🙏 Temple Administration
    """.strip()
    
    return send_sms(devotee.contact_number, message)