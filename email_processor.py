import webapp2

from views import MainPage, SubscriberPage


application = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/subscriber', SubscriberPage),
], debug=True)
