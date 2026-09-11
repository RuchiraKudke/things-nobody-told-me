import json
import urllib.request
import urllib.error

from django.core.mail.backends.base import BaseEmailBackend


class ResendEmailBackend(BaseEmailBackend):

    def send_messages(self, email_messages):

        if not email_messages:
            return 0

        sent_count = 0

        api_key = self._get_api_key()

        if not api_key:
            return 0

        for email_message in email_messages:

            if self._send_email(email_message, api_key):
                sent_count += 1

        return sent_count


    def _get_api_key(self):

        from django.conf import settings

        return getattr(
            settings,
            "RESEND_API_KEY",
            ""
        )


    def _send_email(self, email_message, api_key):

        recipients = email_message.to

        if not recipients:
            return False

        payload = {
            "from": str(email_message.from_email),
            "to": recipients,
            "subject": email_message.subject,
            "text": email_message.body,
        }

        if email_message.alternatives:

            html_content = None

            for content, content_type in email_message.alternatives:

                if content_type == "text/html":

                    html_content = content
                    break

            if html_content:

                payload["html"] = html_content


        data = json.dumps(payload).encode("utf-8")


        request = urllib.request.Request(
            "https://api.resend.com/emails",
            data=data,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )


        try:

            with urllib.request.urlopen(
                request,
                timeout=20
            ) as response:

                return 200 <= response.status < 300


        except urllib.error.HTTPError as error:

            print(
                "Resend HTTP Error:",
                error.code,
                error.read().decode()
            )

            return False


        except Exception as error:

            print(
                "Resend Email Error:",
                error
            )

            return False