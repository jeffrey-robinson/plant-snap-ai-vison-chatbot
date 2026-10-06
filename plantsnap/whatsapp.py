import json

from twilio.rest import Client as TwilioClient

REQUIRED_TWILIO_SECRETS = (
    "TWILIO_ACCOUNT_SID",
    "TWILIO_AUTH_TOKEN",
    "TWILIO_WHATSAPP_FROM",
    "TWILIO_CONTENT_SID",
)


def clean_whatsapp_text(text):
    if not text:
        return "No plant summary available."
    text = " ".join(text.split())
    return text[:1500] + "..." if len(text) > 1500 else text


def send_whatsapp(secrets, to_number, user_name, summary):
    missing_secrets = [key for key in REQUIRED_TWILIO_SECRETS if key not in secrets]
    if missing_secrets:
        return False, "WhatsApp sending is not configured. Add the Twilio settings to Streamlit secrets."

    try:
        client = TwilioClient(
            secrets["TWILIO_ACCOUNT_SID"],
            secrets["TWILIO_AUTH_TOKEN"],
        )
        content_variables = json.dumps(
            {"1": user_name, "2": clean_whatsapp_text(summary)},
            ensure_ascii=False,
        )
        message = client.messages.create(
            from_=secrets["TWILIO_WHATSAPP_FROM"],
            to=f"whatsapp:{to_number}",
            content_sid=secrets["TWILIO_CONTENT_SID"],
            content_variables=content_variables,
        )
        return True, message.sid
    except Exception as error:
        return False, f"Couldn't send that: {error}"