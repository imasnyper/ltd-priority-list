"""Mailgun backend class."""

import requests

from django.conf import settings
from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import sanitize_address


class MailgunBackend(BaseEmailBackend):
    """
    A wrapper that manages mailgun API
    """

    def __init__(self, url=None, fail_silently=False):
        super().__init__(fail_silently=fail_silently)
        self.url = url or settings.MAILGUN_API_URL
        self.api_key = settings.MAILGUN_API_KEY

    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not email_messages:
            return
        num_sent = 0
        for message in email_messages:
            sent = self._send(message)
            if sent:
                num_sent += 1
        return num_sent

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        body = email_message.body
        try:
            requests.post(
                self.url,
                auth=("api", self.api_key),
                data={"from": from_email,
                      "to": recipients,
                      "subject": email_message.subject,
                      "text": body}
            )
        except:
            if not self.fail_silently:
                raise
            return False
        return True
