#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import cgi
import jinja2
import os
from google.appengine.ext import db

# set up jinja
template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir))

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Entry(db.Model):
    title = db.StringProperty(required = True)
    entry = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class MainPage(Handler):
    # handles the '/' webpage
    def get(self):
        self.render("base.html")

class NewEntry(Handler):
    # handles new-entry form submissions
    def render_entry_form(self, title="", entry="", error=""):
        self.render("new-entry.html", title=title, entry=entry, error=error)

    def get(self):
        self.render_entry_form()

    def post(self):
        title = self.request.get("title")
        entry = self.request.get("entry")

        if title and entry:
            e = Entry(title=title, entry=entry)
            e.put()

            self.redirect("/blog")
        else:
            error = "We need both a title and entry content!"
            self.render_entry_form(title, entry, error)

class BlogEntries(Handler):
    #handles the '/blog' webpage
    def render_entries(self, title="", entry="", error=""):
        entries = db.GqlQuery("SELECT * FROM Entry ORDER BY created DESC LIMIT 5")
        self.render("front.html", title=title, entry=entry, error=error, entries=entries)
    def get(self):
        self.render_entries()

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', BlogEntries),
    ('/new-entry', NewEntry)
], debug=True)
