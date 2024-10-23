import mimetypes
import base64
from email.message import EmailMessage
from email.mime.text import MIMEText

import google.auth
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
GOOGLE_APPLICATION_CREDENTIALS = "./credentials.json"
flow = InstalledAppFlow.from_client_secrets_file(GOOGLE_APPLICATION_CREDENTIALS, SCOPES)

creds = flow.run_local_server(port=0)

service = build('gmail', 'v1', credentials=creds)

message = MIMEText('Tghis is the body of the email')
message["To"] = "dylanknuth01@gmail.com"
message["From"] = "playerstattrends@gmail.com"
message["Subject"] = "sample with attachment"

filen = './ESPN_PlayerData_10.23.24.xlsx'

PASS = '9wby=B*R45f6'

type_subtype, _ = mimetypes.guess_type(filen)
maintype, subtype = type_subtype.split("/")

with open(filen, "rb") as fp:
    attachment_data = MIME

message.add_attachment(attachment_data, maintype, subtype)



def gmail_send_email_with_attachment(fileName):
  creds, _ = google.auth.default()

  try:
    # create gmail api client
    service = build("gmail", "v1", credentials=creds)
    message = EmailMessage()

    # headers
    message["To"] = "dylanknuth01@gmail.com"
    message["From"] = "playerstattrends@gmail.com"
    message["Subject"] = "sample with attachment"

    # text
    message.set_content(
        "Hi, this is automated mail with attachment.Please do not reply."
    )

    # attachment
    attachment_filename = fileName
    # guessing the MIME type
    type_subtype, _ = mimetypes.guess_type(attachment_filename)
    maintype, subtype = type_subtype.split("/")

    with open(attachment_filename, "rb") as fp:
      attachment_data = fp.read()
    message.add_attachment(attachment_data, maintype, subtype)

    encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    create_draft_request_body = {"message": {"raw": encoded_message}}
    # pylint: disable=E1101
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