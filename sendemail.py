import base64
import os
from sendgrid import SendGridAPIClient, Attachment, FileContent, FileName, FileType, Disposition
from sendgrid.helpers.mail import Mail
from dotenv import  load_dotenv

load_dotenv()

FROM_EMAIL_ADDRESS = os.getenv("FROM_EMAIL_ADDRESS")
TO_EMAIL_ADDRESS = os.getenv("TO_EMAIL_ADDRESS")
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

def send_email(image_path):
    message = Mail(
        from_email=FROM_EMAIL_ADDRESS,
        to_emails=TO_EMAIL_ADDRESS,
        subject="Hey! Image Detected!",
        plain_text_content="Hey there! Motion detected!",
    )
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        image_file.close()
    encoded_image = base64.b64encode(image_data).decode()

    attachmentFile = Attachment(
        file_content=encoded_image,
        file_name=image_path,
        file_type="image/png",
    )
    message.attachment= attachmentFile

    try:
        sg = SendGridAPIClient(api_key=SENDGRID_API_KEY)
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(f"error: {e}")


if __name__ == "__main__":
    send_email("image.png")
