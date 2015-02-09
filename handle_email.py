from datetime import datetime

import webapp2

from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext import ndb

from models import Email, Subscriber

from google.appengine.api import mail


class LogSenderHandler(InboundMailHandler):
    def receive(self, message):
        # Rebuild body
        content = ""
        for content_type, body in message.bodies('text/html'):
            content += body.decode()

        # Save email
        email = Email(parent=Email.get_root(),
                      sender=message.sender,
                      subject=message.subject,
                      content=content,
        # Correct format would be "%a, %d %b %Y %H:%M:%S %z", but "%z" has issues...
                      date=datetime.strptime(message.date[:-6], "%a, %d %b %Y %H:%M:%S"))
        email.put()

        # See if any subscriber wants this email
        subscribers = Subscriber.query()
        for subscriber in subscribers:
            for word in subscriber.words:
                if word in email.content:
                    subscriber.forwarded.append(email)
                    subscriber.put()
                    mail.send_mail(sender="forwarder@email-processor-sample.appspotmail.com",
                        to=subscriber.email,
                        subject=email.subject,
                        body=content)
                    break

app = webapp2.WSGIApplication([LogSenderHandler.mapping()], debug=True)
