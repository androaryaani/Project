import streamlit as st
from twilio.rest import Client
import smtplib
from email.message import EmailMessage

st.set_page_config(page_title="Multi-Tool Automation App", layout="wide")
st.title("🛠️ All-in-One Automation Dashboard")

# Sidebar Navigation
option = st.sidebar.selectbox(
    "Choose a tool",
    ("Send Email", "Send SMS", "Make a Call", "Send WhatsApp Message", "Post to Instagram")
)

# Twilio Credentials (Replace with secure methods for deployment)
ACCOUNT_SID = "enter_your_sid"
AUTH_TOKEN = "enter_your_token"
TWILIO_PHONE = "+1enteryournumber"
TWILIO_WHAT = "whatsapp:+14155238886"  # Twilio Sandbox WhatsApp number

# Email Credentials (Use app password, not your real Gmail password)
EMAIL_ADDRESS = "your@gmail,com"
EMAIL_PASSWORD = "password"

# -------------------- Send Email --------------------
if option == "Send Email":
    st.header("✉️ Send Email")
    to_email = st.text_input("Recipient Email")
    subject = st.text_input("Subject")
    body = st.text_area("Email Body")
    if st.button("Send Email"):
        try:
            msg = EmailMessage()
            msg['Subject'] = subject
            msg['From'] = EMAIL_ADDRESS
            msg['To'] = to_email
            msg.set_content(body)
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
                smtp.send_message(msg)
            st.success("✅ Email sent successfully!")
        except Exception as e:
            st.error(f"❌ Failed to send email: {e}")

# -------------------- Send SMS --------------------
elif option == "Send SMS":
    st.header("📱 Send SMS")
    to_number = st.text_input("Recipient Phone Number (with country code)")
    message = st.text_area("Message")
    if st.button("Send SMS"):
        try:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            msg = client.messages.create(
                body=message,
                from_=TWILIO_PHONE,
                to=to_number
            )
            st.success("✅ SMS sent successfully!")
        except Exception as e:
            st.error(f"❌ Failed to send SMS: {e}")

# -------------------- Make a Call --------------------
elif option == "Make a Call":
    st.header("📞 Make a Call")
    to_number = st.text_input("Recipient Phone Number (with country code)")
    message_url = st.text_input("Message URL (TwiML XML)", value="http://demo.twilio.com/docs/voice.xml")
    if st.button("Call Now"):
        try:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            call = client.calls.create(
                url=message_url,
                to=to_number,
                from_=TWILIO_PHONE
            )
            st.success(f"✅ Call placed successfully! SID: {call.sid}")
        except Exception as e:
            st.error(f"❌ Failed to make a call: {e}")

# -------------------- Send WhatsApp Message --------------------
# -------------------- Send WhatsApp Message --------------------
elif option == "Send WhatsApp Message":
    st.header("💬 Send WhatsApp Message")

    raw_number = st.text_input("Recipient Number (e.g., +91XXXXXXXXXX)")
    to_number = f"whatsapp:{raw_number.strip()}" if raw_number else ""
    message = st.text_area("Message")

    if st.button("Send WhatsApp"):
        try:
            client = Client(ACCOUNT_SID, AUTH_TOKEN)
            msg = client.messages.create(
                body=message,
                from_="whatsapp:+14155238886",  # This is the Twilio Sandbox Number
                to=to_number                    # Must be whatsapp:+91XXXX...
            )
            st.success("✅ WhatsApp message sent successfully!")
        except Exception as e:
            st.error(f"❌ Failed to send WhatsApp message: {e}")



# -------------------- Instagram Placeholder --------------------
elif option == "Post to Instagram":
    from instagrapi import Client
    import tempfile
    import os

    st.header("📸 Post to Instagram")

    # Credentials (for demo/testing — move to st.secrets in production)
    username = st.text_input("Instagram Username")
    password = st.text_input("Instagram Password", type="password")

    uploaded_image = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"])
    caption = st.text_area("Caption for the post")

    if st.button("Post to Instagram"):
        if not username or not password:
            st.error("❌ Please enter your Instagram credentials.")
        elif not uploaded_image:
            st.error("❌ Please upload an image.")
        else:
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
                    tmp_file.write(uploaded_image.read())
                    tmp_file_path = tmp_file.name

                cl = Client()
                cl.login(username, password)
                cl.photo_upload(tmp_file_path, caption)
                st.success("✅ Image posted successfully!")

                os.remove(tmp_file_path)  # Clean up temp image file

            except Exception as e:
                st.error(f"❌ Failed to post image: {e}")

