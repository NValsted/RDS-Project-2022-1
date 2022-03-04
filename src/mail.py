import smtplib
import ssl
import os
import json
from io import BytesIO, StringIO
from typing import List, Union, Optional, Tuple
from datetime import datetime
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart

from src.utils import get_logger

PORT = int(os.getenv("PORT", 465))
GMAIL = os.getenv("GMAIL")
GMAIL_PASSWORD = os.getenv("GMAIL_PASSWORD")
MAIL_RECEIVERS = json.loads(os.getenv("MAIL_RECEIVERS", "[]"))

context = ssl.create_default_context()


def send_email(
    receivers: List[str] = MAIL_RECEIVERS,
    subject: str = f"Bot report {datetime.now()}",
    attachments: Optional[
        List[
            Tuple[str, Union[BytesIO, StringIO]]
        ]
    ] = None,
):
    logger = get_logger("SEND-EMAIL")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = GMAIL

    for filename, payload in attachments:
        part = MIMEBase("application", "octet-streams")
        payload.seek(0)
        part.set_payload(payload.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )
        message.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", PORT, context=context) as server:
        server.login(GMAIL, GMAIL_PASSWORD)
        for receiver in receivers:
            message["To"] = receiver
            server.sendmail(GMAIL, receiver, message.as_string())
            logger.info(f"Sent email to {receiver}")
