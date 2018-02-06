# -*- coding: utf-8 -*-
from __future__ import print_function
import os
from scrapy.dupefilters import RFPDupeFilter
from yokaspider.tools import URL_NO_FILTER
from scrapy.utils.request import request_fingerprint

class CustomDupeFilter(RFPDupeFilter):
    def request_seen(self, request):
        if request.url not in URL_NO_FILTER:
            fp = self.request_fingerprint(request)
            if fp in self.fingerprints:
                return True
            self.fingerprints.add(fp)
            if self.file:
                self.file.write(fp + os.linesep)