import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_password_reset_link(to, token):
  sender_email = "noreply@twidder.com"

  message = MIMEMultipart("alternative")
  message["Subject"] = "Password reset"
  message["From"] = sender_email
  message["To"] = to

  # Create the plain-text and HTML version of your message
  text = """\
  Hi,
  How are you?

  Someone has recently requested a password reset for your account.
  If that wasn't you, you can savely ignore this email.
  If you did request a password reset, here is your link:
  """ + 'http://localhost:5000/reset_password/' + token

  # Turn these into plain/html MIMEText objects
  part1 = MIMEText(text, "plain")

  # Add HTML/plain-text parts to MIMEMultipart message
  # The email client will try to render the last part first
  message.attach(part1)


  with smtplib.SMTP('localhost', port=1025) as server:
    server.sendmail(
        sender_email, to, message.as_string()
    )
    server.quit()
