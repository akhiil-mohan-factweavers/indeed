import os

from scrapy.dupefilter import RFPDupeFilter


class CustomFilter(RFPDupeFilter):

    def __getid(self, url):
        mm = url.split("&refer")[0] #or something like that
        return mm

    def request_seen(self, request):
        fp = self.__getid(request.url)
        if fp in self.fingerprints:
            return True
        self.fingerprints.add(fp)
        if self.file:
            self.file.write(fp + os.linesep)