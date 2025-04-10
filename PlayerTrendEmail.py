import base64
import mimetypes
import os.path
from email import encoders
from email.message import EmailMessage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_google_creds():
    """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    return creds


def send_player_trends_email(creds, attachment_filename):
    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()
        recipients = ["dylanknuth01@gmail.com"]
        # recipients = ["dylanknuth01@gmail.com","josedamian33@gmail.com"]
        # Headers
        message["To"] = ", ".join(recipients)
        message["From"] = "playerstattrends@gmail.com"
        message["Subject"] = "Player Trends"

        message.attach(build_file_part(attachment_filename))

        # guessing the MIME type
        type_subtype, _ = mimetypes.guess_type(attachment_filename)

        maintype, subtype = type_subtype.split("/")
        with open(attachment_filename, "rb") as fp:
            attachment_data = fp.read()
        message.add_attachment(attachment_data, maintype, subtype)

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}
        # pylint: disable=E1101
        send_message = (
            service.users()
            .messages()
            .send(userId="me", body=create_message)
            .execute()
        )
        print(f'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None
    return send_message


def build_file_part(filePath):
    content_type, encoding = mimetypes.guess_type(filePath)
    if content_type is None or encoding is not None:
        content_type = "application/octet-stream"
    main_type, sub_type = content_type.split("/", 1)
    if main_type == "text":
        with open(filePath, "rb"):
            msg = MIMEText("r", _subtype=sub_type)
    elif main_type == "image":
        with open(filePath, "rb"):
            msg = MIMEImage("r", _subtype=sub_type)
    elif main_type == "audio":
        with open(filePath, "rb"):
            msg = MIMEAudio("r", _subtype=sub_type)
    else:
        with open(filePath, "rb") as f:
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(f.read())
    filename = os.path.basename(filePath)
    encoders.encode_base64(msg)
    msg.add_header("Content-Disposition", "attachment", filename=filename)
    return msg
