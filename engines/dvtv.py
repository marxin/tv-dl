#!/usr/bin/env python3
#
__author__ = "Martin Liška"
__desc__ = "DVTV"
__url__ = r"http?://video\.aktualne\.cz/.+"

import re,os.path 
import json
from urllib.request import urlopen
from urllib.parse import urlencode
from os.path import basename
import logging

log = logging.getLogger()

def get_key(t):
  return t['format'] + '_' + t['quality']

class DvtvEngine:
    def __init__(self, url):
        self.url = url
        self.page = urlopen(url).read().decode('utf-8')
        self.get_playlist()
        
        if len(self.playlist) == 0:
            raise ValueError('Není k dispozici žádná kvalita videa.')
        
    def get_playlist(self):
        videosJson = re.search(r'sources: (\[[^\]]*\])', self.page, re.MULTILINE)
        if videosJson == None:
          return
        
        videosJson = videosJson.group(1).replace('file:', '"file":').replace('type:', '"type":').replace('label:', '"label":').replace("'", '"')
        videos = json.loads(videosJson)
        self.playlist = list(map(lambda x: {'quality': x['label'], 'format': x['type'].split('/')[1], 'url': x['file'], 'default': 'default' in x}, videos))
      
    def qualities(self):
      return map(lambda x: (get_key(x), x['quality'] + ' ' +x['format']), self.playlist)

    def movies(self):
      return []

    def download(self, quality, movie):
      video = None
      if quality == None:
        video = next(x for x in self.playlist if x['default'] == True)
      else:
        video = next(x for x in self.playlist if get_key(x) == quality)
      return ('http', basename(self.url.rsplit('/')[-3]) + '.' + video['format'], { 'url': video['url'] })
