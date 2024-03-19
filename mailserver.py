import base64

from email.message import EmailMessage
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from requests import HTTPError

SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
    ]
flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
creds = flow.run_local_server(port=0)

def send_password_reset_link(to, token):
  service = build('gmail', 'v1', credentials=creds)
  # Create the plain-text and HTML version of your message
  text = """\
  Hi,
  How are you?

  Someone has recently requested a password reset for your account.
  If that wasn't you, you can savely ignore this email.
  If you did request a password reset, here is your link:
  """ + 'http://localhost:5000/reset_password/' + token
  message = EmailMessage()
  message.set_content(text)
  
  message["Subject"] = "Password reset"
  # this doesn't work with google api sadly
  # message["From"] = "noreply@twidder.com"
  message["To"] = to
  create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

  try:
      message = (service.users().messages().send(userId="me", body=create_message).execute())
      print(F'sent message to {message} Message Id: {message["id"]}')
  except HTTPError as error:
      print(F'An error occurred: {error}')
      message = None
