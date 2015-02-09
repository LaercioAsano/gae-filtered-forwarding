import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2

from models import Email, Subscriber

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "html")),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class SubscriberPage(webapp2.RequestHandler):
    def get_subscriber(self):
        user = users.get_current_user()

        # User not logged, redirect to login
        if user is None:
            self.redirect(users.create_login_url(self.request.uri))
            return None, None

        # User logged. If not registered, register.
        query = Subscriber.query(Subscriber.uid == user.user_id(), ancestor=Subscriber.get_root())
        subscriber = query.get()
        new_subscriber = False
        if subscriber is None:
            new_subscriber = True
            subscriber = Subscriber(email=user.email(),
                                    uid=user.user_id(),
                                    name=user.nickname(),
                                    parent=Subscriber.get_root())
            subscriber.put()

        return subscriber, new_subscriber

    def render_page(self, subscriber, new_one, message, status):
        # Get list of the recently received email
        last_forwarded = subscriber.forwarded[-10:]
        last_forwarded.reverse()

        template_values = {
            'words' : subscriber.words,
            'forwarded' : last_forwarded,
            'message' : message,
            'name' : users.get_current_user().nickname(),
            'logout' : users.create_logout_url("/"),
            'status' : status
        }
        template = JINJA_ENVIRONMENT.get_template('subscriber.html')
        self.response.write(template.render(template_values))


    def get(self):
        # Simply get the subscriber and render the page.
        subscriber, new_subscriber = self.get_subscriber()
        if subscriber is None:
            return

        # Remember if already registered.
        message = "Nice to meet you!" if new_subscriber else "Welcome back!"
        self.render_page(subscriber, new_subscriber, message, "info")


    def post(self):
        subscriber, new_subscriber = self.get_subscriber()
        if subscriber is None:
            return

        # Try to add or remove word from watching list
        word = self.request.get('word')
        add = self.request.get('bt') == "add"
        if add:
            if word not in subscriber.words:
                subscriber.words.append(word)
                message = "'%s' added succesfully." % word
                status = 'success'
            else:
                subscriber.words.append(word)
                message = "'%s' already in watched words." % word
                status = 'danger'
        else:
            if word in subscriber.words:
                subscriber.words.remove(word)
                message = "'%s' removed succesfully." % word
                status = 'success'
            else:
                message = "'%s' not in watched words." % word
                status = 'danger'
        subscriber.put()

        self.render_page(subscriber, new_subscriber, message, status)


class MainPage(webapp2.RequestHandler):

    def get(self):
        # Get the last 20 emails received to show on the main page.
        query = Email.query(ancestor=Email.get_root()).order(-Email.date)
        emails = query.fetch(20)

        user = users.get_current_user()
        template_values = {
            'emails': emails,
            'logged' : user is not None,
            'login' : users.create_login_url("/subscriber"),
            'logout' : users.create_logout_url(self.request.uri)
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
