from __future__ import with_statement
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers

import urllib
from models import MyFile

class MainPage(webapp.RequestHandler):
    def get(self):
        q=MyFile.all()
        mfiles=q.fetch(100)
        template_values={'files':mfiles}
        content = template.render('templates/index.html',template_values)
        self.response.out.write(content)

class DownloadHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)

application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/downloads/([^/]+)?',DownloadHandler),
                                      ], debug=False)


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
